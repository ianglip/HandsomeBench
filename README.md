# HandsomeBench

Introducing HandsomeBench, a benchmark that ranks models by how highly they rate my selfie on a scale from 1 to 100.

HandsomeBench is a mostly unserious multimodal model benchmark. It sends the included photo to a roster of frontier vision models and asks each model to answer with a direct 1-100 attractiveness score.

## Current Leaderboard

Open the generated chart:

[results/20260521-140032/HandsomeBench.html](results/20260521-140032/HandsomeBench.html)

The underlying run artifacts are also included:

- `results/20260521-140032/leaderboard.md`
- `results/20260521-140032/leaderboard.csv`
- `results/20260521-140032/raw.jsonl`

## Run It

Create a local environment and install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Create `dev.vars.local` with the provider API keys you want to use:

```bash
OPENAI_API_KEY=...
GOOGLE_AI_API_KEY=...
XAI_API_KEY=...
LINKAPI_API_KEY=...
DASHSCOPE_API_KEY=...
```

Check the roster and provider availability:

```bash
.venv/bin/python handsome_bench.py --dry-run
.venv/bin/python handsome_bench.py --preflight --timeout 30
```

Run the benchmark:

```bash
.venv/bin/python handsome_bench.py --timeout 360
```

Regenerate the Artificial Analysis-style chart from the included results:

```bash
python3 render_artificial_analysis_chart.py
```
