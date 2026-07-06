#!/usr/bin/env python3
"""Validate rehab mobile browser QA metrics.

The source L1 gate catches copy/API contract regressions. This browser-metrics
gate catches rendered mobile UX failures that only exist after layout, such as
undersized tap targets or fixed inputs overlapping the bottom nav.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ISSUE_FIELDS = {
    "fakeHits": "fake_hits",
    "touchIssues": "touch_issues",
    "inputIssues": "input_issues",
    "overflows": "overflow_issues",
    "verticalTextIssues": "vertical_text_issues",
}


def _entries(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("results"), list):
            return [item for item in payload["results"] if isinstance(item, dict)]
        if isinstance(payload.get("pages"), list):
            return [item for item in payload["pages"] if isinstance(item, dict)]
    return []


def _with_page(page: str, issue: Any) -> dict[str, Any]:
    if isinstance(issue, dict):
        return {"page": page, **issue}
    return {"page": page, "value": issue}


def evaluate_browser_metrics(payload: Any) -> dict[str, Any]:
    detail = {name: [] for name in ISSUE_FIELDS.values()}
    checked_pages: list[str] = []

    for entry in _entries(payload):
        page = str(entry.get("page") or entry.get("name") or "unknown")
        checked_pages.append(page)
        metrics = entry.get("metrics") if isinstance(entry.get("metrics"), dict) else entry
        for source_name, output_name in ISSUE_FIELDS.items():
            issues = metrics.get(source_name) if isinstance(metrics, dict) else None
            if isinstance(issues, list):
                detail[output_name].extend(_with_page(page, issue) for issue in issues)

    failures = sum(len(items) for items in detail.values())
    result = {
        "gate": "L1-BROWSER-METRICS-001",
        "level": "L1",
        "status": "FAIL" if failures else "PASS",
        "summary": "Rendered mobile browser QA has no fake copy, small touch targets, input overlap, overflow, or vertical text.",
        "detail": {
            "checked_pages": checked_pages,
            **detail,
        },
    }
    return {
        "summary": {
            "overall": result["status"],
            "failed": 1 if failures else 0,
            "total": 1,
        },
        "results": [result],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = evaluate_browser_metrics(payload)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
