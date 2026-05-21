# HandsomeBench

Introducing HandsomeBench, a benchmark that ranks models by how highly they rate my selfie on a scale from 1 to 100.

HandsomeBench is a mostly unserious multimodal model benchmark. It sends the included photo to a roster of frontier vision models and asks each model to answer with a direct 1-100 attractiveness score. The current roster includes OpenAI, Gemini, Grok, Claude via Anthropic's official API, Qwen via DashScope, and DeepSeek V4 rows marked as skipped because DeepSeek V4 does not currently document image input support.

## Current Leaderboard

Open the generated chart:

[results/20260521-155039-official-merged-final/HandsomeBench.html](results/20260521-155039-official-merged-final/HandsomeBench.html)

The underlying run artifacts are also included:

- `results/20260521-155039-official-merged-final/leaderboard.md`
- `results/20260521-155039-official-merged-final/leaderboard.csv`
- `results/20260521-155039-official-merged-final/raw.jsonl`

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
ANTHROPIC_API_KEY=...
DASHSCOPE_API_KEY=...
DEEPSEEK_API_KEY=...
```

The harness ignores provider-truncated responses when ranking. In the first run, `gemini-3.5-flash` with high thinking emitted a partial `8` before hitting `MAX_TOKENS`; the current leaderboard uses the later complete official-Google rerun instead.

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
