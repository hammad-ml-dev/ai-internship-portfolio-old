from typing import List, Optional

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel, Field

from .pipeline import generate_and_rank_names
from .domain_checker import DomainChecker


app = FastAPI(title="AI-Powered Business Name Recommender", version="0.1.0")


class GenerateRequest(BaseModel):
	keywords: Optional[List[str]] = Field(default=None, description="Keywords to guide naming")
	count: int = Field(default=120, ge=10, le=1000)
	top: int = Field(default=15, ge=1, le=100)
	tlds: List[str] = Field(default_factory=list)
	check_domains: bool = False
	min_len: int = Field(default=5, ge=3, le=20)
	max_len: int = Field(default=12, ge=5, le=24)
	dataset_csv: Optional[str] = Field(default=None, description="Optional path to a CSV with a 'name' column to bias generation")
	use_llm: bool = False
	only_free_tld: Optional[str] = Field(default=None, description="If set (e.g., '.com'), only return names likely free for this TLD")


@app.get("/health")
def health():
	return {"status": "ok"}


@app.post("/generate")
@app.post("/api/generate")
def generate(req: GenerateRequest):
	results = generate_and_rank_names(
		user_keywords=req.keywords or [],
		num_candidates=req.count,
		max_results=req.top,
		check_domains=(req.check_domains or bool(req.only_free_tld)),
		tlds=req.tlds,
		min_len=req.min_len,
		max_len=req.max_len,
		dataset_csv=req.dataset_csv,
		use_llm=req.use_llm,
	)
	# Optional filter: only names with specified TLD marked free
	if req.only_free_tld:
		tld = req.only_free_tld
		results = [r for r in results if r.get("domains", {}).get(tld) == "free"]
	return {"results": results}


@app.post("/api/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
	"""Upload a CSV dataset with a 'name' column. Saves to tmp and returns a path to use.

	Note: This saves to a temporary file on the server running the backend.
	"""
	import tempfile
	import os

	fd, path = tempfile.mkstemp(prefix="names_", suffix=".csv")
	os.close(fd)
	with open(path, "wb") as f:
		f.write(await file.read())
	return {"dataset_csv": path}


class RecheckRequest(BaseModel):
	names: List[str]
	tlds: List[str]


@app.post("/api/recheck")
def recheck(req: RecheckRequest):
	checker = DomainChecker()
	out = []
	for n in req.names:
		availability = checker.check_name(n, req.tlds)
		free = sum(1 for v in availability.values() if isinstance(v, str) and v.lower() == "free")
		out.append({"name": n, "domains": availability, "availability_score": free / max(1, len(req.tlds))})
	return {"results": out}


