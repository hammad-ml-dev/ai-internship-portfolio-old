import os
from typing import List

import requests


def openai_generate_names(keywords: List[str], count: int = 50) -> List[str]:
	"""Generate candidate names using OpenAI's Chat Completions API.

	Set OPENAI_API_KEY in environment to enable. Returns an empty list if key is missing or any error occurs.
	"""
	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		return []

	try:
		prompt = (
			"You are a branding assistant. Generate a list of short, professional, brandable business "
			"names for an SME consultancy. Avoid generic words like consulting, group, services. Return "
			f"exactly {count} unique names separated by commas, based on keywords: {', '.join(keywords)}."
		)
		resp = requests.post(
			"https://api.openai.com/v1/chat/completions",
			headers={
				"Authorization": f"Bearer {api_key}",
				"Content-Type": "application/json",
			},
			json={
				"model": "gpt-4o-mini",
				"messages": [{"role": "user", "content": prompt}],
				"temperature": 0.8,
			},
			timeout=30,
		)
		resp.raise_for_status()
		text = resp.json()["choices"][0]["message"]["content"]
		parts = [p.strip() for p in text.replace("\n", ",").split(",")]
		return [p for p in parts if p]
	except Exception:
		return []


