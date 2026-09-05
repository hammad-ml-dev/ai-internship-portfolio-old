## AI-Powered Business Name Recommender

An ML-assisted tool to generate attractive, brandable names for SME consultancy services (company formation, compliance, business setup). It blends curated keywords with brandable morphemes, applies readability and professionalism scoring, and optionally checks domain availability.

### Quick Start

1) Install Python 3.10+
2) Create a virtual environment and install dependencies:

```bash
python -m venv .venv
./.venv/Scripts/Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

3) Run the web app (UI + API):

```bash
python -m name_recommender
```

Open `http://localhost:8000/static/index.html` in your browser.

4) Run the CLI to generate names (no domain checks):

```bash
python -m name_recommender.cli --count 50 --top 15
```

5) With custom keywords and TLDs:

```bash
python -m name_recommender.cli \
  --keywords "growth, trust, advisory, guardian, launch, setup, ledger" \
  --tlds .com .co .io \
  --count 120 --top 20
```

6) Enable domain availability checks (optional):

- Domainr API: set `DOMAINR_CLIENT_ID` env var
- GoDaddy API: set `GODADDY_API_KEY` and `GODADDY_API_SECRET`

```bash
# Example with Domainr and GoDaddy enabled
$env:DOMAINR_CLIENT_ID = "your_domainr_client_id"
$env:GODADDY_API_KEY = "your_key"
$env:GODADDY_API_SECRET = "your_secret"
python -m name_recommender.cli --check-domains --tlds .com .co --count 100 --top 15
```

Outputs are written to `output/` as timestamped CSV and JSON, and printed to console.

### Features

- Curated SME consultancy keywords and seed names
- Brandable name generation: blends, compounds, alliteration, prefixes/suffixes
- Scoring: length, pronounceability, professionalism, relevance
- Filters: profanity, overly generic phrases, duplicates
- Optional domain availability checks for `.com`, `.co`, and custom TLDs

### Project Structure

```
AI-Powered Business Name Recommender Tool byHD/
  README.md
  requirements.txt
  src/
    name_recommender/
      __init__.py
      __main__.py
      cli.py
      pipeline.py
      generator.py
      scorer.py
      preprocess.py
      domain_checker.py
      api.py
      ml/
        __init__.py
        morpheme_stats.py
        embeddings.py
      data/
        keywords.txt
        seed_names.txt
        banned_words.txt
      static/
        index.html
        styles.css
        app.js
  output/  # created at runtime
```

### Reproducible Workflow

- Data collection & preprocessing: see `preprocess.py` and `data/`
- Model experimentation: `generator.py` and `scorer.py`
- Integration: `domain_checker.py` + `pipeline.py`
- CLI run: `cli.py`

### Documentation: AI Workflow & Rationale

1) Input preparation
- Cleans user-supplied keywords, merges with curated SME list
- Deduplicates and normalizes (lowercase, ascii, alpha)

2) Candidate generation
- Compound names (e.g., GrowthGuard, LaunchLedger)
- Portmanteau blends with brandable morphemes (e.g., Trustoria, Complynt)
- Prefix/suffix patterns (e.g., Nova + Trust → Novatrust, Advisoria)
- Alliteration and rhythm heuristics
- Optional real-data bias: If you provide a CSV of existing business names, we mine common prefixes/suffixes and adjust generation priors accordingly

3) Scoring & filtering
- Length: prefer 5–12 chars (brandability window)
- Pronounceability: vowel/consonant ratio, cluster penalties
- Professionalism: business morphemes, avoids slang
- Relevance: overlap with SME keywords
- Similarity dedupe: RapidFuzz ratio threshold
- Banned list: profanity + generic phrases filtered

4) Domain availability (optional)
- For each candidate, checks `<name><affix>.<tld>` variants via Domainr or GoDaddy when configured; otherwise uses a heuristic availability score

5) Output
- Ranks by aggregate score + availability and emits CSV/JSON. CLI prints a top shortlist with rationale scores.

### Example

```bash
python -m name_recommender.cli --keywords "growth, trust, advisory, guardian, launch" --tlds .com .co --count 150 --top 15 --check-domains
```
With real-data CSV biasing (server-side path):

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["growth", "trust", "advisory"],
    "count": 200,
    "top": 20,
    "min_len": 5,
    "max_len": 12,
    "check_domains": false,
    "tlds": [".com", ".co"],
    "dataset_csv": "C:/datasets/companies.csv"
  }'
```


Expected console output (abridged):

```
Rank Name           Score  Availability(.com,.co)
1    GrowthGuard    0.86   free, taken
2    Trustoria      0.84   taken, free
3    LaunchLedger   0.82   unknown, free
...
```

### Roles 
- ML Engineer: implement `generator.py`, `scorer.py`, tune parameters
- Data Engineer: expand/maintain `data/` corpora, profanity list
- Software Engineer: implement/maintain `domain_checker.py` integrations

### Success Criteria

- Generates 50–200 unique, relevant candidates per run
- At least 2–3 candidates pass domain availability and brand quality checks
- Reproducible runs and documented workflow

### Notes

- This project favors lightweight, local heuristics for speed and privacy. You can hybridize with hosted LLMs (e.g., OpenAI) by adding a generator in `generator.py` that consumes `OPENAI_API_KEY` and merges results before scoring.


