import re
from collections import Counter
from typing import Iterable, List, Tuple

from unidecode import unidecode


def normalize(text: str) -> str:
	return re.sub(r"[^a-z]", "", unidecode(text.lower()))


def extract_morphemes(names: Iterable[str], min_len: int = 3, max_len: int = 6) -> List[Tuple[str, int]]:
	counts: Counter[str] = Counter()
	for raw in names:
		name = normalize(raw)
		for l in range(min_len, max_len + 1):
			for i in range(0, len(name) - l + 1):
				frag = name[i : i + l]
				counts[frag] += 1
	return counts.most_common()


def top_prefixes_suffixes(names: Iterable[str], k: int = 30) -> Tuple[List[str], List[str]]:
	prefixes: Counter[str] = Counter()
	suffixes: Counter[str] = Counter()
	for raw in names:
		name = normalize(raw)
		if len(name) < 4:
			continue
		for l in [2, 3, 4]:
			if len(name) >= l:
				prefixes[name[:l]] += 1
				suffixes[name[-l:]] += 1
	return ([p for p, _ in prefixes.most_common(k)], [s for s, _ in suffixes.most_common(k)])


