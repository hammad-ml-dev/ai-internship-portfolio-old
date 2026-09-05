from typing import Iterable, List

try:
	from rapidfuzz.embeddings import TfIdf
except Exception:  # pragma: no cover
	TfIdf = None  # optional


def keyword_rank(keywords: List[str], corpus: Iterable[str]) -> List[str]:
	"""Rank corpus items by TF-IDF similarity to the keyword query.

	If TF-IDF is not available, returns the corpus unchanged.
	"""
	if TfIdf is None or not corpus:
		return list(corpus)
	model = TfIdf()
	model.fit(corpus)
	scores = model.transform([" ".join(keywords)]) @ model.transform(corpus).T
	indices = scores.toarray().ravel().argsort()[::-1]
	corpus_list = list(corpus)
	return [corpus_list[i] for i in indices]


