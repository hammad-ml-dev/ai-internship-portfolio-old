import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .pipeline import generate_and_rank_names

app = typer.Typer(add_completion=False)
console = Console()


def parse_keywords(raw: Optional[str]) -> List[str]:
	if not raw:
		return []
	parts = [p.strip() for p in raw.replace(";", ",").split(",")]
	return [p for p in parts if p]


@app.command()
def main(
	keywords: Optional[str] = typer.Option(
		None, help="Comma-separated keywords e.g. 'growth, trust, advisory'"
	),
	count: int = typer.Option(100, help="Number of raw candidates to generate"),
	top: int = typer.Option(15, help="Top N names to display/export"),
	tlds: List[str] = typer.Option([], help="TLDs to check (e.g., .com .co .io)"),
	check_domains: bool = typer.Option(False, help="Enable domain availability checks"),
	min_len: int = typer.Option(5, help="Minimum name length"),
	max_len: int = typer.Option(12, help="Maximum name length"),
):
	"""Generate and rank brandable business names."""
	user_keywords = parse_keywords(keywords)
	results = generate_and_rank_names(
		user_keywords=user_keywords,
		num_candidates=count,
		max_results=top,
		check_domains=check_domains,
		tlds=tlds,
		min_len=min_len,
		max_len=max_len,
	)

	# Display table
	table = Table(title="Top Name Suggestions")
	table.add_column("Rank", justify="right")
	table.add_column("Name", justify="left")
	table.add_column("Score", justify="right")
	if tlds:
		for t in tlds:
			table.add_column(f"{t}")

	for idx, r in enumerate(results, start=1):
		row = [str(idx), r["name"], f"{r['score']:.3f}"]
		if tlds:
			for t in tlds:
				row.append(r.get("domains", {}).get(t, "-"))
		table.add_row(*row)
	console.print(table)

	# Export
	output_dir = Path("output")
	output_dir.mkdir(parents=True, exist_ok=True)
	ts = datetime.now().strftime("%Y%m%d_%H%M%S")
	json_path = output_dir / f"names_{ts}.json"
	csv_path = output_dir / f"names_{ts}.csv"
	with open(json_path, "w", encoding="utf-8") as f:
		json.dump(results, f, ensure_ascii=False, indent=2)

	with open(csv_path, "w", encoding="utf-8") as f:
		header = ["rank", "name", "score"] + [t for t in tlds]
		f.write(",".join(header) + "\n")
		for idx, r in enumerate(results, start=1):
			row = [str(idx), r["name"], f"{r['score']:.3f}"]
			for t in tlds:
				row.append(r.get("domains", {}).get(t, ""))
			f.write(",".join(row) + "\n")

	console.print(f"\nSaved: {json_path} and {csv_path}")


if __name__ == "__main__":
	app()


