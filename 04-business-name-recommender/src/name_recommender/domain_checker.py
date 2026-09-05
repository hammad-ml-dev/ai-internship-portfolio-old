import os
from typing import Dict, List

import requests


class DomainChecker:
	"""Check domain availability via Domainr and/or GoDaddy if configured.

	Falls back to a heuristic label when APIs are not configured.
	"""

	def __init__(self) -> None:
		self.domainr_client_id = os.getenv("DOMAINR_CLIENT_ID")
		self.godaddy_key = os.getenv("GODADDY_API_KEY")
		self.godaddy_secret = os.getenv("GODADDY_API_SECRET")

	def check_name(self, name: str, tlds: List[str]) -> Dict[str, str]:
		availability: Dict[str, str] = {}
		for tld in tlds:
			label = self._check_single(name, tld)
			availability[tld] = label
		return availability

	def _check_single(self, name: str, tld: str) -> str:
		domain = f"{name.lower()}{tld}"
		# Try RDAP (free, no API key)
		try:
			ok = self._rdap_available(domain)
			if ok is not None:
				return "free" if ok else "taken"
		except Exception:
			pass
		# Prefer Domainr
		if self.domainr_client_id:
			try:
				label = self._domainr_status(domain)
				if label:
					return label
			except Exception:
				pass
		# Try GoDaddy
		if self.godaddy_key and self.godaddy_secret:
			try:
				ok = self._godaddy_available(domain)
				return "free" if ok else "taken"
			except Exception:
				pass
		# Fallback heuristic: DNS resolve using Google DNS JSON API
		try:
			if self._dns_free(domain):
				return "free"
			return "taken"
		except Exception:
			return "unknown"

	def _domainr_status(self, domain: str) -> str:
		url = "https://api.domainr.com/v2/status"
		params = {"domain": domain, "client_id": self.domainr_client_id}
		resp = requests.get(url, params=params, timeout=10)
		resp.raise_for_status()
		data = resp.json()
		statuses = data.get("status", [])
		if not statuses:
			return "unknown"
		# Domainr status codes: https://domainr.build/docs/api/reference/status
		status = statuses[0].get("status", "")
		if any(s in status for s in ["inactive", "undelegated", "marketed"]):
			return "free"
		if any(s in status for s in ["active", "reserved", "transferable"]):
			return "taken"
		return "unknown"

	def _godaddy_available(self, domain: str) -> bool:
		url = "https://api.godaddy.com/v1/domains/available"
		headers = {
			"Authorization": f"sso-key {self.godaddy_key}:{self.godaddy_secret}",
			"Accept": "application/json",
			"Content-Type": "application/json",
		}
		resp = requests.get(url, params={"domain": domain}, headers=headers, timeout=10)
		resp.raise_for_status()
		data = resp.json()
		return bool(data.get("available", False))

	def _rdap_available(self, domain: str) -> bool | None:
		"""Query RDAP (free) via rdap.org. Returns True if available, False if taken, None if unknown."""
		url = f"https://rdap.org/domain/{domain}"
		resp = requests.get(url, timeout=10)
		if resp.status_code == 200:
			return False
		if resp.status_code == 404:
			return True
		return None

	def _dns_free(self, domain: str) -> bool:
		"""Use Google's DNS JSON API to infer availability.

		If NXDOMAIN (status 3) for A and AAAA queries, we consider it likely free.
		This is heuristic and may be wrong for parked or non-resolving domains.
		"""
		try:
			status_a = self._dns_query(domain, "1")
			status_aaaa = self._dns_query(domain, "28")
			return (status_a == 3) and (status_aaaa == 3)
		except Exception:
			return False

	def _dns_query(self, domain: str, qtype: str) -> int:
		resp = requests.get("https://dns.google/resolve", params={"name": domain, "type": qtype}, timeout=8)
		resp.raise_for_status()
		data = resp.json()
		return int(data.get("Status", 0))


