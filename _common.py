# SPDX-License-Identifier: MIT
# AuditReady evidence-puller shared helpers.
"""Shared helpers: dated output folder, CSV writer, retry wrapper, structured
logging, and an API-call counter used for the end-of-run cost estimate."""

import csv
import json
import logging
import os
import sys
import time
from datetime import date
from pathlib import Path


def setup_logging(name: str) -> logging.Logger:
    """Structured (JSON-lines) logging to stderr; INFO by default."""
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get("AUDITREADY_LOG_LEVEL", "INFO"))
    handler = logging.StreamHandler(sys.stderr)

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            payload = {
                "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
                "level": record.levelname,
                "logger": record.name,
                "msg": record.getMessage(),
            }
            if record.exc_info:
                payload["exc"] = self.formatException(record.exc_info)
            return json.dumps(payload)

    handler.setFormatter(JsonFormatter())
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def evidence_dir(subfolder: str) -> Path:
    """evidence-output/YYYY-MM-DD/<subfolder>/ next to the scripts folder."""
    base = Path(os.environ.get("AUDITREADY_OUTPUT_DIR", "evidence-output"))
    out = base / date.today().isoformat() / subfolder
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_csv(path: Path, rows: list[dict], logger: logging.Logger) -> None:
    """Write dict rows to CSV; header is the union of keys in row order."""
    if not rows:
        logger.info(f"no rows for {path.name}; writing header-only file")
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"wrote {len(rows)} rows -> {path}")


class CallCounter:
    """Counts API calls so each script can print a cost estimate at exit."""

    def __init__(self):
        self.calls = 0

    def tick(self, n: int = 1):
        self.calls += n

    def report(self, service: str, per_call_usd: float = 0.0):
        est = self.calls * per_call_usd
        print(
            f"\n[cost] {service}: {self.calls} API calls"
            + (f", estimated ${est:.4f}" if per_call_usd else
               " (covered by free tier / flat plan for typical volumes)")
        )


def with_retries(fn, logger, attempts: int = 4, base_delay: float = 1.5):
    """Run fn() with exponential backoff on any exception."""
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — provider SDKs raise many types
            if attempt == attempts:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"attempt {attempt}/{attempts} failed ({exc}); retrying in {delay:.1f}s")
            time.sleep(delay)


def require_env(*names: str) -> dict:
    """Fetch required env vars; exit with a clear message if any is missing."""
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        sys.exit(
            f"Missing environment variables: {', '.join(missing)}.\n"
            "Copy scripts/.env.example to .env, fill in your keys, and run via:\n"
            "  set -a; source .env; set +a; python3 scripts/<script>.py"
        )
    return {n: os.environ[n] for n in names}
