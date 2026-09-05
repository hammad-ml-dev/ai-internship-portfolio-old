from pathlib import Path
from typing import List


DATA_DIR = Path(__file__).parent / "data"


def _read_lines(file_path: Path) -> List[str]:
	if not file_path.exists():
		return []
	with open(file_path, "r", encoding="utf-8") as f:
		return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


def load_curated_keywords() -> List[str]:
	return _read_lines(DATA_DIR / "keywords.txt")


def load_seed_names() -> List[str]:
	return _read_lines(DATA_DIR / "seed_names.txt")


def load_banned_words() -> List[str]:
	return _read_lines(DATA_DIR / "banned_words.txt")


def ingest_dataset_csv(csv_path: str, name_column: str = "name") -> List[str]:
	"""Load business names from a CSV file with a given column.

	Simple CSV reader to avoid adding heavy deps. Expects a header row.
	"""
	path = Path(csv_path)
	if not path.exists():
		return []
	rows: List[str] = []
	with open(path, "r", encoding="utf-8") as f:
		header = f.readline().strip().split(",")
		if name_column not in header:
			return []
		idx = header.index(name_column)
		for line in f:
			cols = [c.strip() for c in line.rstrip("\n").split(",")]
			if idx < len(cols):
				val = cols[idx]
				if val:
					rows.append(val)
	return rows


