import math
import re
from typing import List, Optional

from rapidfuzz import fuzz


VOWELS = set("aeiou")


def _vowel_consonant_ratio(name: str) -> float:
	name = name.lower()
	v = sum(1 for c in name if c in VOWELS)
	c = sum(1 for c in name if c.isalpha() and c not in VOWELS)
	if c == 0:
		return 0.0
	return v / c


def _cluster_penalty(name: str) -> float:
	# Penalize long consonant clusters (e.g., "stpr")
	clusters = re.findall(r"[^aeiou]{3,}", name.lower())
	return -0.05 * sum(len(x) - 2 for x in clusters)


def _length_score(name: str, min_len: int = 5, max_len: int = 12) -> float:
	length = len(name)
	if length < min_len or length > max_len:
		return 0.0
	center = (min_len + max_len) / 2
	spread = (max_len - min_len) / 2
	return math.exp(-((length - center) ** 2) / (2 * (spread ** 2)))


def _relevance_score(name: str, curated_keywords: List[str]) -> float:
	name_l = name.lower()
	return 1.0 if any(k in name_l for k in curated_keywords[:30]) else 0.6


def _professionalism_score(name: str) -> float:
	# Encourage endings and stems that feel professional
	bonuses = [
		("guard", 0.25),
		("trust", 0.25),
		("veri", 0.15),
		("fort", 0.15),
		("advis", 0.2),
		("comply", 0.2),
		("ledger", 0.15),
	]
	score = 0.4
	for stem, b in bonuses:
		if stem in name.lower():
			score += b
	return min(score, 1.0)


def _is_banned(name: str, banned_words: List[str]) -> bool:
	lower = name.lower()
	return any(b in lower for b in banned_words)


class ScoreEngine:
	def __init__(self, curated_keywords: List[str], banned_words: List[str]):
		self.curated_keywords = [x.lower() for x in curated_keywords]
		self.banned_words = [x.lower() for x in banned_words]
		self._recent: List[str] = []

	def score(self, name: str) -> Optional[float]:
		if _is_banned(name, self.banned_words):
			return None
		# Basic dedupe vs. recent suggestions using similarity threshold
		if self._recent and max(fuzz.ratio(name, r) for r in self._recent) > 92:
			return None

		length = _length_score(name)
		pronounce = 0.5 + 0.3 * _vowel_consonant_ratio(name) + _cluster_penalty(name)
		pronounce = max(0.0, min(pronounce, 1.0))
		relevance = _relevance_score(name, self.curated_keywords)
		professional = _professionalism_score(name)

		score = 0.30 * length + 0.30 * pronounce + 0.25 * professional + 0.15 * relevance
		self._recent.append(name)
		if len(self._recent) > 50:
			self._recent.pop(0)
		return float(score)


