#!/usr/bin/env python3
"""Merge a focused provider rerun into a prior HandsomeBench result set."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from handsome_bench import RESULTS_DIR, write_outputs


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge focused provider results into a prior run.")
    parser.add_argument("--base", required=True, type=Path, help="Existing result directory to preserve from.")
    parser.add_argument("--rerun", required=True, type=Path, help="Focused provider rerun result directory.")
    parser.add_argument("--replace-providers", required=True, help="Comma-separated providers replaced by rerun rows.")
    parser.add_argument("--out", type=Path, help="Output directory. Defaults to results/<timestamp>-merged.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    replace = {provider.strip() for provider in args.replace_providers.split(",") if provider.strip()}
    out_dir = args.out or RESULTS_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-merged"

    base_rows = read_jsonl(args.base / "raw.jsonl")
    rerun_rows = read_jsonl(args.rerun / "raw.jsonl")
    merged = [row for row in base_rows if row.get("provider") not in replace]
    merged.extend(rerun_rows)
    write_outputs(merged, out_dir)

    old_chart = args.base / "HandsomeBench.html"
    if old_chart.exists() and not (out_dir / "HandsomeBench.html").exists():
        shutil.copy2(old_chart, out_dir / "HandsomeBench.html")

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
