from typing import Dict, List

from .generator import NameGenerator
from .scorer import ScoreEngine
from .preprocess import load_curated_keywords, load_seed_names, load_banned_words, ingest_dataset_csv
from .ml.morpheme_stats import top_prefixes_suffixes
from .ml.llm import openai_generate_names
from .domain_checker import DomainChecker


def generate_and_rank_names(
	user_keywords: List[str],
	num_candidates: int,
	max_results: int,
	check_domains: bool,
	tlds: List[str],
	min_len: int,
	max_len: int,
    dataset_csv: str | None = None,
    use_llm: bool = False,
) -> List[Dict]:
	curated_keywords = load_curated_keywords()
	seed_names = load_seed_names()
	banned_words = load_banned_words()

	# Optional: enhance prefixes/suffixes from real dataset
	if dataset_csv:
		corpus = ingest_dataset_csv(dataset_csv)
		if corpus:
			pref, suff = top_prefixes_suffixes(corpus, k=20)
			# Prepend to curated keywords to bias generation
			curated_keywords = list(dict.fromkeys(pref + curated_keywords + suff))

	generator = NameGenerator(
		curated_keywords=curated_keywords,
		seed_names=seed_names,
		banned_words=banned_words,
		min_len=min_len,
		max_len=max_len,
	)
	scorer = ScoreEngine(curated_keywords=curated_keywords, banned_words=banned_words)
	domain_checker = DomainChecker()

	candidates = generator.generate_candidates(user_keywords=user_keywords, target_count=num_candidates)

	# LLM boost: merge extra candidates if enabled
	if use_llm and user_keywords:
		llm_candidates = openai_generate_names(user_keywords, max(20, num_candidates // 2))
		for c in llm_candidates:
			c = c.strip()
			if c and c not in candidates:
				candidates.append(c)
	scored = []
	for name in candidates:
		score = scorer.score(name)
		if score is None:
			continue
		item = {"name": name, "score": score}
		if check_domains and tlds:
			availability = domain_checker.check_name(name, tlds)
			item["domains"] = availability
			free = sum(1 for v in availability.values() if isinstance(v, str) and v.lower() == "free")
			item["availability_score"] = free / max(1, len(tlds))
		scored.append(item)

	scored.sort(key=lambda x: x["score"], reverse=True)
	return scored[: max_results]


