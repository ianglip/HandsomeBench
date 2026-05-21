#!/usr/bin/env python3
"""Render HandsomeBench results in an Artificial Analysis-inspired style."""

from __future__ import annotations

import csv
import html
from pathlib import Path


RESULT_DIR = Path("results/20260521-140032")
SRC = RESULT_DIR / "leaderboard.csv"
OUT = RESULT_DIR / "HandsomeBench.html"

PROVIDER_COLORS = {
    "xai": "#202124",
    "dashscope": "#f06a2a",
    "openai": "#202124",
    "google": "#55ae62",
    "linkapi": "#c58265",
}

PROVIDER_BADGES = {
    "xai": "xI",
    "dashscope": "Q",
    "openai": "◎",
    "google": "G",
    "linkapi": "AI",
}


def short_label(row: dict[str, str]) -> str:
    model = row["label"]
    reason = row.get("reasoning") or ""
    parts = [
        ("grok-4.20-", "Grok 4.20 "),
        ("grok-4.3", "Grok 4.3"),
        ("qwen3.5-", "Qwen3.5 "),
        ("qwen3.6-", "Qwen3.6 "),
        ("gpt-", "GPT-"),
        ("gemini-", "Gemini "),
        ("claude-", "Claude "),
    ]
    for old, new in parts:
        model = model.replace(old, new)
    model = model.replace("-preview", "").replace("-0309", "")
    if "effort=" in reason:
        model += f" ({reason.split('=', 1)[1]})"
    elif "thinkingLevel=" in reason:
        model += f" ({reason.split('=', 1)[1]})"
    elif "enable_thinking=True" in reason:
        model += " (thinking)"
    elif "thinkingBudget=" in reason:
        model += f" ({reason.split('=', 1)[1]})"
    return model


def load_rows() -> tuple[list[dict[str, str]], int]:
    valid: list[dict[str, str]] = []
    invalid = 0
    with SRC.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("status") == "ok":
                valid.append(row)
            elif row.get("status"):
                invalid += 1
    valid.sort(key=lambda row: (-(float(row["score"])), float(row.get("latency_ms") or 0)))
    return valid, invalid


def render() -> None:
    rows, invalid = load_rows()
    width = max(860, len(rows) * 29 + 52)
    height = 540
    left = 26
    right = 12
    top = 32
    plot_height = 260
    baseline = top + plot_height
    plot_width = width - left - right
    gap = 5
    bar_width = max(20, (plot_width - gap * (len(rows) - 1)) / len(rows))
    grid = []
    for tick in (25, 50, 75, 100):
        y = baseline - plot_height * tick / 100
        grid.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" class="grid" />'
        )

    bars = []
    labels = []
    for index, row in enumerate(rows):
        score = float(row["score"])
        provider = row["provider"]
        x = left + index * (bar_width + gap)
        h = plot_height * score / 100
        y = baseline - h
        cx = x + bar_width / 2
        color = PROVIDER_COLORS.get(provider, "#64748b")
        badge = PROVIDER_BADGES.get(provider, provider[:2].upper())
        title = f"#{index + 1} {row['label']} {row.get('reasoning') or ''} - {score:g}"
        bars.append(
            f'<g class="bar"><title>{html.escape(title)}</title>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{h:.1f}" rx="4" fill="{color}" />'
            f'<text x="{cx:.1f}" y="{y + h / 2 + 4:.1f}" class="score" text-anchor="middle">{score:g}</text>'
            f'<circle cx="{cx:.1f}" cy="{baseline + 13}" r="7" fill="#fff" />'
            f'<text x="{cx:.1f}" y="{baseline + 17}" class="badge-text" text-anchor="middle">{html.escape(badge)}</text>'
            f"</g>"
        )
        labels.append(
            f'<text x="{cx:.1f}" y="{baseline + 30}" transform="rotate(60 {cx:.1f} {baseline + 30})" '
            f'class="model-label">{html.escape(short_label(row))}</text>'
        )

    table_rows = []
    for rank, row in enumerate(rows, 1):
        table_rows.append(
            "<tr>"
            f"<td>{rank}</td>"
            f"<td>{float(row['score']):g}</td>"
            f"<td>{html.escape(row['provider'])}</td>"
            f"<td>{html.escape(row['label'])}</td>"
            f"<td>{html.escape(row.get('reasoning') or '')}</td>"
            "</tr>"
        )

    champion = rows[0]
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>HandsomeBench</title>
<style>
:root {{ --ink:#1f1f1f; --muted:#5f6368; --grid:#dddddd; --accent:#8b5cf6; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#fff; color:var(--ink); font-family: Arial, Helvetica, sans-serif; }}
main {{ max-width:980px; margin:0 auto; padding:14px 24px 28px; }}
.topline {{ display:flex; justify-content:flex-end; align-items:center; gap:7px; padding:0 0 6px; font-family: Georgia, "Times New Roman", serif; font-size:15px; }}
.spark {{ width:14px; height:14px; color:var(--accent); }}
.rule {{ border-top:2px dotted #dadce0; margin-bottom:16px; }}
h1 {{ margin:0; font-size:22px; letter-spacing:-.02em; font-weight:700; }}
.subtitle {{ margin:4px 0 10px; color:var(--muted); font-size:13px; }}
.chart-wrap {{ overflow-x:auto; padding-bottom:4px; }}
svg {{ display:block; min-width:{width}px; }}
.grid {{ stroke:var(--grid); stroke-width:1.25; stroke-dasharray:1 4; stroke-linecap:round; }}
.axis {{ stroke:#e5e7eb; stroke-width:1; }}
.score {{ fill:#fff; font-size:10px; font-weight:700; pointer-events:none; }}
.badge-text {{ fill:#111; font-size:9px; font-weight:800; font-family: Arial, Helvetica, sans-serif; }}
.model-label {{ fill:#111; font-size:10px; font-weight:600; }}
.bar rect {{ transition:opacity .15s ease; }}
.bar:hover rect {{ opacity:.72; }}
.summary {{ display:flex; flex-wrap:wrap; gap:8px 16px; margin:8px 0 10px; color:var(--muted); font-size:12px; }}
.summary b {{ color:var(--ink); }}
.table-wrap {{ margin-top:6px; overflow-x:auto; border-top:1px solid #e5e7eb; }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th, td {{ padding:6px 8px; border-bottom:1px solid #eeeeee; text-align:left; white-space:nowrap; }}
th {{ color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:.05em; }}
td:nth-child(2) {{ font-weight:800; }}
footer {{ margin-top:8px; color:var(--muted); font-size:11px; }}
</style>
</head>
<body>
<main>
  <div class="topline">
    <svg class="spark" viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M10.9 1.8 8.7 7h5.5l-8.9 7.2L7.5 9H1.8l9.1-7.2Z"/></svg>
    <span>Artificial Analysis</span>
  </div>
  <div class="rule"></div>
  <h1>HandsomeBench</h1>
  <p class="subtitle">Which model rates Entropy the most handsome, on a scale from 1 to 100?</p>
  <div class="summary">
    <span>Champion: <b>{html.escape(champion['label'])}</b></span>
    <span>Score: <b>{float(champion['score']):g}</b></span>
    <span>Valid scored rows: <b>{len(rows)}</b></span>
  </div>
  <section class="chart-wrap" aria-label="HandsomeBench leaderboard chart">
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-title chart-desc">
      <title id="chart-title">HandsomeBench</title>
      <desc id="chart-desc">Bars are sorted by score from highest on the left to lowest on the right.</desc>
      {''.join(grid)}
      <line x1="{left}" y1="{baseline}" x2="{width - right}" y2="{baseline}" class="axis" />
      {''.join(bars)}
      {''.join(labels)}
    </svg>
  </section>
  <section class="table-wrap">
    <table>
      <thead><tr><th>Rank</th><th>Score</th><th>Provider</th><th>Model</th><th>Reasoning</th></tr></thead>
      <tbody>{''.join(table_rows)}</tbody>
    </table>
  </section>
  <footer>Source: {html.escape(str(SRC))}. {invalid} invalid/error rows omitted from chart.</footer>
</main>
</body>
</html>
"""
    OUT.write_text(document, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    render()
