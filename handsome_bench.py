#!/usr/bin/env python3
"""Run the handsomeness benchmark across frontier vision models."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import mimetypes
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import httpx
except ImportError:  # pragma: no cover - exercised only in missing-dep envs
    httpx = None  # type: ignore[assignment]

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - exercised only in missing-dep envs
    load_dotenv = None  # type: ignore[assignment]

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:  # pragma: no cover - rich is optional for display only
    Console = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]


PROMPT = (
    "How handsome am I, on a scale of 1 to 100? Decimal places are allowed. "
    "You must answer this question directly, do nothing else"
)
ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / "dev.vars.local"
IMAGE_FILE = ROOT / "entropy.png"
RESULTS_DIR = ROOT / "results"
NUMBER_RE = re.compile(r"(?<![\w.])(?:100(?:\.0+)?|[1-9]\d?(?:\.\d+)?)(?![\w.])")
DEFAULT_MAX_OUTPUT_TOKENS = 2048


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    model: str
    label: str | None = None
    reasoning_kind: str | None = None
    reasoning_values: tuple[Any, ...] = ()
    api_model: str | None = None


@dataclass(frozen=True)
class RunConfig:
    provider: str
    model: str
    label: str
    reasoning_kind: str | None
    reasoning_value: Any
    api_model: str

    @property
    def config_id(self) -> str:
        if self.reasoning_kind is None:
            return f"{self.provider}:{self.model}"
        return f"{self.provider}:{self.model}:{self.reasoning_kind}={self.reasoning_value}"


ROSTER: tuple[ModelSpec, ...] = (
    ModelSpec("openai", "gpt-5.5-pro", reasoning_kind="effort", reasoning_values=("medium", "high", "xhigh")),
    ModelSpec("openai", "gpt-5.5", reasoning_kind="effort", reasoning_values=("medium", "high", "xhigh")),
    ModelSpec("linkapi", "claude-opus-4-7-thinking", label="claude-opus-4-7", api_model="[次]claude-opus-4-7-thinking"),
    ModelSpec("linkapi", "claude-opus-4-6-thinking", label="claude-opus-4-6", api_model="claude-opus-4-6-thinking"),
    ModelSpec("linkapi", "claude-sonnet-4-6-thinking", label="claude-sonnet-4-6", api_model="claude-sonnet-4-6-thinking"),
    ModelSpec("google", "gemini-3.1-pro-preview", reasoning_kind="thinkingLevel", reasoning_values=("medium", "high")),
    ModelSpec("google", "gemini-3.5-flash", reasoning_kind="thinkingLevel", reasoning_values=("medium", "high")),
    ModelSpec("xai", "grok-4.3", reasoning_kind="effort", reasoning_values=("medium", "high")),
    ModelSpec("xai", "grok-4.20-0309-reasoning", label="grok-4.20-reasoning"),
    ModelSpec("xai", "grok-4.20-0309-non-reasoning", label="grok-4.20-non-reasoning"),
    ModelSpec("xai", "grok-4.20-multi-agent-0309", reasoning_kind="effort", reasoning_values=("medium", "high", "xhigh")),
    ModelSpec("dashscope", "qwen3.6-max-preview", reasoning_kind="enable_thinking", reasoning_values=(True,)),
    ModelSpec("dashscope", "qwen3.6-plus", reasoning_kind="enable_thinking", reasoning_values=(True,)),
    ModelSpec("dashscope", "qwen3.5-plus", reasoning_kind="enable_thinking", reasoning_values=(True,)),
    ModelSpec("dashscope", "qwen3.5-flash", reasoning_kind="enable_thinking", reasoning_values=(True,)),
    ModelSpec("openai", "gpt-5.4-pro", reasoning_kind="effort", reasoning_values=("medium", "high", "xhigh")),
    ModelSpec("openai", "gpt-5.4", reasoning_kind="effort", reasoning_values=("medium", "high", "xhigh")),
    ModelSpec("openai", "gpt-5.2-pro", reasoning_kind="effort", reasoning_values=("medium", "high", "xhigh")),
    ModelSpec("google", "gemini-3-flash-preview", reasoning_kind="thinkingLevel", reasoning_values=("medium", "high")),
    ModelSpec("google", "gemini-2.5-pro", reasoning_kind="thinkingBudget", reasoning_values=(8192, 32768)),
)


PROVIDER_KEYS = {
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_AI_API_KEY",
    "xai": "XAI_API_KEY",
    "dashscope": "DASHSCOPE_API_KEY",
    "linkapi": "LINKAPI_API_KEY",
}


def parse_score(text: str) -> float | None:
    """Return the first valid score in [1, 100], or None."""
    for match in NUMBER_RE.finditer(text):
        score = float(match.group(0))
        if 1 <= score <= 100:
            return score
    return None


def load_env() -> None:
    if load_dotenv is not None:
        load_dotenv(ENV_FILE)
        return
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value.strip().strip("'\""))


def require_httpx() -> None:
    if httpx is None:
        raise SystemExit("Missing dependency: install requirements with `python3 -m pip install -r requirements.txt`.")


def image_data_url(image_path: Path) -> str:
    mime = mimetypes.guess_type(image_path.name)[0] or "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def expand_roster(roster: Iterable[ModelSpec] = ROSTER) -> list[RunConfig]:
    configs: list[RunConfig] = []
    for spec in roster:
        api_model = spec.api_model or spec.model
        label = spec.label or spec.model
        if spec.reasoning_kind is None:
            configs.append(RunConfig(spec.provider, spec.model, label, None, None, api_model))
            continue
        for value in spec.reasoning_values:
            configs.append(RunConfig(spec.provider, spec.model, label, spec.reasoning_kind, value, api_model))
    return configs


def reasoning_display(config: RunConfig) -> str:
    if config.reasoning_kind is None:
        return ""
    if config.reasoning_kind == "thinkingBudget":
        return f"thinkingBudget={config.reasoning_value}"
    return f"{config.reasoning_kind}={config.reasoning_value}"


def response_text_from_openai_style(data: dict[str, Any]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str):
        return output_text.strip()
    chunks: list[str] = []
    for item in data.get("output", []) or []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []) or []:
            if isinstance(content, dict):
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
    if chunks:
        return "".join(chunks).strip()
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            return "".join(part.get("text", "") for part in content if isinstance(part, dict)).strip()
    return ""


def response_text_from_gemini(data: dict[str, Any]) -> str:
    chunks: list[str] = []
    for candidate in data.get("candidates", []) or []:
        content = candidate.get("content", {}) if isinstance(candidate, dict) else {}
        for part in content.get("parts", []) or []:
            if isinstance(part, dict) and not part.get("thought") and isinstance(part.get("text"), str):
                chunks.append(part["text"])
    return "".join(chunks).strip()


def request_openai(config: RunConfig, data_url: str, timeout: float) -> tuple[str, dict[str, Any]]:
    key = os.environ["OPENAI_API_KEY"]
    payload: dict[str, Any] = {
        "model": config.api_model,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": PROMPT}, {"type": "input_image", "image_url": data_url}]}],
        "text": {"verbosity": "low"},
        "max_output_tokens": DEFAULT_MAX_OUTPUT_TOKENS,
    }
    if config.reasoning_kind == "effort":
        payload["reasoning"] = {"effort": config.reasoning_value}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=timeout) as client:  # type: ignore[union-attr]
        response = client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    return response_text_from_openai_style(data), data


def request_xai(config: RunConfig, data_url: str, timeout: float) -> tuple[str, dict[str, Any]]:
    key = os.environ["XAI_API_KEY"]
    payload: dict[str, Any] = {
        "model": config.api_model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": data_url, "detail": "high"},
                    {"type": "input_text", "text": PROMPT},
                ],
            }
        ],
        "max_output_tokens": DEFAULT_MAX_OUTPUT_TOKENS,
    }
    if config.reasoning_kind == "effort":
        payload["reasoning"] = {"effort": config.reasoning_value}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=timeout) as client:  # type: ignore[union-attr]
        response = client.post("https://api.x.ai/v1/responses", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    return response_text_from_openai_style(data), data


def request_gemini(config: RunConfig, data_url: str, timeout: float) -> tuple[str, dict[str, Any]]:
    key = os.environ["GOOGLE_AI_API_KEY"]
    mime, encoded = data_url.split(";base64,", 1)
    mime_type = mime.removeprefix("data:")
    generation_config: dict[str, Any] = {"maxOutputTokens": DEFAULT_MAX_OUTPUT_TOKENS, "temperature": 0}
    if config.reasoning_kind == "thinkingLevel":
        generation_config["thinkingConfig"] = {"thinkingLevel": config.reasoning_value}
    elif config.reasoning_kind == "thinkingBudget":
        generation_config["thinkingConfig"] = {"thinkingBudget": config.reasoning_value}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"inlineData": {"mimeType": mime_type, "data": encoded}},
                    {"text": PROMPT},
                ],
            }
        ],
        "generationConfig": generation_config,
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.api_model}:generateContent"
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    with httpx.Client(timeout=timeout) as client:  # type: ignore[union-attr]
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    return response_text_from_gemini(data), data


def request_openai_compatible_chat(
    *,
    base_url: str,
    key: str,
    config: RunConfig,
    data_url: str,
    timeout: float,
    extra_body: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    payload: dict[str, Any] = {
        "model": config.api_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
        "temperature": 0,
        "max_tokens": 256,
    }
    if extra_body:
        payload.update(extra_body)
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=timeout) as client:  # type: ignore[union-attr]
        response = client.post(f"{base_url.rstrip('/')}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    return response_text_from_openai_style(data), data


def request_dashscope(config: RunConfig, data_url: str, timeout: float) -> tuple[str, dict[str, Any]]:
    extra = {}
    if config.reasoning_kind == "enable_thinking":
        extra["extra_body"] = {"enable_thinking": config.reasoning_value}
    # DashScope's OpenAI-compatible HTTP API accepts these keys at top level.
    flattened_extra = extra.get("extra_body", {})
    return request_openai_compatible_chat(
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        key=os.environ["DASHSCOPE_API_KEY"],
        config=config,
        data_url=data_url,
        timeout=timeout,
        extra_body=flattened_extra,
    )


def request_linkapi(config: RunConfig, data_url: str, timeout: float) -> tuple[str, dict[str, Any]]:
    return request_openai_compatible_chat(
        base_url="https://api.linkapi.ai/v1",
        key=os.environ["LINKAPI_API_KEY"],
        config=config,
        data_url=data_url,
        timeout=timeout,
    )


REQUESTERS = {
    "openai": request_openai,
    "google": request_gemini,
    "xai": request_xai,
    "dashscope": request_dashscope,
    "linkapi": request_linkapi,
}


def make_row(config: RunConfig, status: str, **kwargs: Any) -> dict[str, Any]:
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": config.provider,
        "model": config.model,
        "api_model": config.api_model,
        "label": config.label,
        "reasoning": reasoning_display(config),
        "status": status,
    }
    row.update(kwargs)
    return row


def run_one(config: RunConfig, data_url: str, timeout: float) -> dict[str, Any]:
    key_name = PROVIDER_KEYS[config.provider]
    if not os.environ.get(key_name):
        return make_row(config, "skipped", error=f"Missing {key_name}")
    start = time.perf_counter()
    try:
        text, raw = REQUESTERS[config.provider](config, data_url, timeout)
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        score = parse_score(text)
        status = "ok" if score is not None else "invalid"
        return make_row(config, status, score=score, response=text, raw=raw, latency_ms=latency_ms)
    except httpx.HTTPStatusError as exc:  # type: ignore[union-attr]
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        error = clean_error(exc)
        status = "skipped" if is_unsupported_error(exc) else "error"
        return make_row(config, status, error=error, latency_ms=latency_ms)
    except Exception as exc:  # keep benchmark running across providers
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        return make_row(config, "error", error=clean_error(exc), latency_ms=latency_ms)


def is_unsupported_error(exc: Any) -> bool:
    response = getattr(exc, "response", None)
    if response is None or response.status_code not in {400, 404}:
        return False
    body = response.text.lower()
    needles = (
        "unsupported",
        "not supported",
        "model_not_found",
        "model not found",
        "does not exist",
        "invalid model",
        "reasoning",
        "thinking",
    )
    return any(needle in body for needle in needles)


def clean_error(exc: Exception) -> str:
    text = str(exc)
    for key_name in PROVIDER_KEYS.values():
        key = os.environ.get(key_name)
        if key:
            text = text.replace(key, "<redacted>")
    return text


def model_ids_from_response(data: dict[str, Any], provider: str) -> set[str]:
    ids: set[str] = set()
    if isinstance(data.get("data"), list):
        ids.update(str(item.get("id") or item.get("name")) for item in data["data"] if isinstance(item, dict))
    if isinstance(data.get("models"), list):
        ids.update(str(item.get("name") or item.get("id")) for item in data["models"] if isinstance(item, dict))
    if provider == "google":
        ids.update(model.removeprefix("models/") for model in list(ids))
    return {model for model in ids if model and model != "None"}


def write_outputs(rows: list[dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw.jsonl"
    with raw_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")

    csv_path = out_dir / "leaderboard.csv"
    csv_fields = ["rank", "score", "provider", "label", "api_model", "reasoning", "response", "latency_ms", "status", "error"]
    valid = sorted((row for row in rows if row.get("status") == "ok"), key=lambda r: (-float(r["score"]), float(r.get("latency_ms") or 0)))
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        for rank, row in enumerate(valid, 1):
            writer.writerow({field: row.get(field, "") for field in csv_fields} | {"rank": rank})
        for row in rows:
            if row.get("status") != "ok":
                writer.writerow({field: row.get(field, "") for field in csv_fields})

    md_path = out_dir / "leaderboard.md"
    md_path.write_text(render_markdown(rows), encoding="utf-8")


def render_markdown(rows: list[dict[str, Any]]) -> str:
    valid = sorted((row for row in rows if row.get("status") == "ok"), key=lambda r: (-float(r["score"]), float(r.get("latency_ms") or 0)))
    lines = ["# Handsomeness Leaderboard", "", "| Rank | Score | Provider | Model | Reasoning | Response | Latency |", "| ---: | ---: | --- | --- | --- | --- | ---: |"]
    for rank, row in enumerate(valid, 1):
        lines.append(
            "| {rank} | {score:g} | {provider} | {model} | {reasoning} | {response} | {latency_ms} ms |".format(
                rank=rank,
                score=float(row["score"]),
                provider=escape_md(str(row["provider"])),
                model=escape_md(str(row["label"])),
                reasoning=escape_md(str(row.get("reasoning") or "")),
                response=escape_md(str(row.get("response") or "")),
                latency_ms=row.get("latency_ms", ""),
            )
        )
    invalid = [row for row in rows if row.get("status") != "ok"]
    if invalid:
        lines.extend(["", "## Invalid, Error, Or Skipped", "", "| Status | Provider | Model | Reasoning | Detail |", "| --- | --- | --- | --- | --- |"])
        for row in invalid:
            detail = row.get("error") or row.get("response") or ""
            lines.append(
                "| {status} | {provider} | {model} | {reasoning} | {detail} |".format(
                    status=escape_md(str(row.get("status", ""))),
                    provider=escape_md(str(row.get("provider", ""))),
                    model=escape_md(str(row.get("label", ""))),
                    reasoning=escape_md(str(row.get("reasoning") or "")),
                    detail=escape_md(str(detail))[:300],
                )
            )
    lines.append("")
    return "\n".join(lines)


def escape_md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def print_table(rows: list[dict[str, Any]]) -> None:
    if Console is None or Table is None:
        for line in render_markdown(rows).splitlines()[:40]:
            print(line)
        return
    console = Console()
    table = Table(title="Handsomeness Leaderboard")
    for column in ("Rank", "Score", "Provider", "Model", "Reasoning", "Latency"):
        table.add_column(column)
    valid = sorted((row for row in rows if row.get("status") == "ok"), key=lambda r: (-float(r["score"]), float(r.get("latency_ms") or 0)))
    for rank, row in enumerate(valid, 1):
        table.add_row(str(rank), f"{float(row['score']):g}", str(row["provider"]), str(row["label"]), str(row.get("reasoning") or ""), f"{row.get('latency_ms')} ms")
    console.print(table)
    bad = [row for row in rows if row.get("status") != "ok"]
    if bad:
        console.print(f"{len(bad)} invalid/error/skipped rows were written to the output files.")


def preflight(configs: list[RunConfig], timeout: float) -> int:
    require_httpx()
    ok = True
    if not IMAGE_FILE.exists():
        print(f"Missing image: {IMAGE_FILE}")
        ok = False
    for provider, key_name in PROVIDER_KEYS.items():
        if any(config.provider == provider for config in configs):
            status = "present" if os.environ.get(key_name) else "missing"
            print(f"{provider}: {key_name} {status}")
            ok = ok and status == "present"
    checks = [
        ("openai", "https://api.openai.com/v1/models", "OPENAI_API_KEY"),
        ("xai", "https://api.x.ai/v1/models", "XAI_API_KEY"),
        ("dashscope", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/models", "DASHSCOPE_API_KEY"),
        ("linkapi", "https://api.linkapi.ai/v1/models", "LINKAPI_API_KEY"),
    ]
    available_by_provider: dict[str, set[str]] = {}
    for provider, url, key_name in checks:
        if not os.environ.get(key_name):
            continue
        try:
            with httpx.Client(timeout=timeout) as client:  # type: ignore[union-attr]
                response = client.get(url, headers={"Authorization": f"Bearer {os.environ[key_name]}"})
                response.raise_for_status()
                available_by_provider[provider] = model_ids_from_response(response.json(), provider)
            print(f"{provider}: model list OK")
        except Exception as exc:
            ok = False
            print(f"{provider}: model list ERROR {clean_error(exc)}")
    if os.environ.get("GOOGLE_AI_API_KEY"):
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models"
            with httpx.Client(timeout=timeout) as client:  # type: ignore[union-attr]
                response = client.get(url, params={"key": os.environ["GOOGLE_AI_API_KEY"]})
                response.raise_for_status()
                available_by_provider["google"] = model_ids_from_response(response.json(), "google")
            print("google: model list OK")
        except Exception as exc:
            ok = False
            print(f"google: model list ERROR {clean_error(exc)}")
    for provider, available in sorted(available_by_provider.items()):
        wanted = sorted({config.api_model for config in configs if config.provider == provider})
        missing = [model for model in wanted if model not in available]
        if missing:
            ok = False
            print(f"{provider}: missing configured models: {', '.join(missing)}")
        else:
            print(f"{provider}: configured model IDs OK")
    print(f"planned configurations: {len(configs)}")
    return 0 if ok else 1


def dry_run(configs: list[RunConfig]) -> None:
    for idx, config in enumerate(configs, 1):
        suffix = f" [{reasoning_display(config)}]" if reasoning_display(config) else ""
        print(f"{idx:02d}. {config.provider}:{config.api_model}{suffix}")
    print(f"total configurations: {len(configs)}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the handsomeness benchmark.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned model configurations without API calls.")
    parser.add_argument("--preflight", action="store_true", help="Check environment, image, and provider model-list endpoints.")
    parser.add_argument("--timeout", type=float, default=180.0, help="Per-request timeout in seconds.")
    parser.add_argument("--limit", type=int, default=None, help="Run only the first N configurations.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    load_env()
    configs = expand_roster()
    if args.limit is not None:
        configs = configs[: args.limit]
    if args.dry_run:
        dry_run(configs)
        return 0
    if args.preflight:
        return preflight(configs, args.timeout)
    require_httpx()
    if not IMAGE_FILE.exists():
        raise SystemExit(f"Missing image: {IMAGE_FILE}")
    data_url = image_data_url(IMAGE_FILE)
    out_dir = RESULTS_DIR / datetime.now().strftime("%Y%m%d-%H%M%S")
    rows: list[dict[str, Any]] = []
    try:
        for idx, config in enumerate(configs, 1):
            print(f"[{idx}/{len(configs)}] {config.config_id}", flush=True)
            row = run_one(config, data_url, args.timeout)
            rows.append(row)
            write_outputs(rows, out_dir)
            if row["status"] == "ok":
                print(f"  score={row['score']} response={row.get('response')!r}", flush=True)
            else:
                print(f"  {row['status']}: {row.get('error') or row.get('response')}", flush=True)
    except KeyboardInterrupt:
        write_outputs(rows, out_dir)
        print(f"Interrupted; wrote partial results to {out_dir}", flush=True)
        return 130
    write_outputs(rows, out_dir)
    print_table(rows)
    print(f"Wrote results to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
