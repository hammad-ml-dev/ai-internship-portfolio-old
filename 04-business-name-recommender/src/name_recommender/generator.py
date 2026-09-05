import random
import re
from typing import Iterable, List, Set

from unidecode import unidecode


BRAND_PREFIXES = [
	"neo",
	"nova",
	"alto",
	"prime",
	"omni",
	"valor",
	"axi",
	"veri",
	"forti",
	"astro",
	"lumen",
	"pro",
	"meta",
]

BRAND_SUFFIXES = [
	"ly",
	"io",
	"ify",
	"ity",
	"ora",
	"ium",
	"ara",
	"ium",
	"able",
	"path",
	"works",
	"core",
	"forge",
	"wise",
]

GENERIC_TERMS = {"consulting", "consultancy", "solutions", "services", "group", "global"}


def normalize_token(token: str) -> str:
	return re.sub(r"[^a-z]", "", unidecode(token.lower()))


class NameGenerator:
	def __init__(
		self,
		curated_keywords: List[str],
		seed_names: List[str],
		banned_words: List[str],
		min_len: int = 5,
		max_len: int = 12,
	):
		self.curated_keywords = [normalize_token(k) for k in curated_keywords]
		self.seed_names = [normalize_token(s) for s in seed_names]
		self.banned_set = {normalize_token(b) for b in banned_words}
		self.min_len = min_len
		self.max_len = max_len

	def generate_candidates(self, user_keywords: List[str], target_count: int = 200) -> List[str]:
		keywords = [normalize_token(k) for k in user_keywords] + self.curated_keywords
		keywords = [k for k in keywords if k and k not in self.banned_set]
		random.shuffle(keywords)

		candidates: Set[str] = set()
		while len(candidates) < target_count and keywords:
			strategy = random.choice([self._compound, self._blend, self._affix, self._alliterate])
			new = strategy(keywords)
			for n in new:
				if self._is_viable(n):
					candidates.add(n)
					if len(candidates) >= target_count:
						break
		return sorted(candidates)

	def _is_viable(self, name: str) -> bool:
		if not name:
			return False
		if any(g in name for g in GENERIC_TERMS):
			return False
		if not (self.min_len <= len(name) <= self.max_len):
			return False
		if any(b in name for b in self.banned_set):
			return False
		return True

	def _compound(self, keywords: List[str]) -> Iterable[str]:
		if len(keywords) < 2:
			return []
		left = random.choice(keywords)
		right = random.choice([k for k in keywords if k != left])
		return {self._title(left + right), self._title(right + left)}

	def _blend(self, keywords: List[str]) -> Iterable[str]:
		if len(keywords) < 2:
			return []
		left = random.choice(keywords)
		right = random.choice([k for k in keywords if k != left])
		l = left[: max(2, len(left) // 2)]
		r = right[-max(2, len(right) // 2) :]
		return {self._title(l + r), self._title(r + l)}

	def _affix(self, keywords: List[str]) -> Iterable[str]:
		k = random.choice(keywords)
		prefix = random.choice(BRAND_PREFIXES)
		suffix = random.choice(BRAND_SUFFIXES)
		return {self._title(prefix + k), self._title(k + suffix)}

	def _alliterate(self, keywords: List[str]) -> Iterable[str]:
		k = random.choice(keywords)
		c = k[0]
		alts = [x for x in keywords if x.startswith(c) and x != k]
		if not alts:
			return []
		alt = random.choice(alts)
		return {self._title(k + alt), self._title(alt + k)}

	@staticmethod
	def _title(text: str) -> str:
		text = normalize_token(text)
		if not text:
			return ""
		return text[0].upper() + text[1:]


