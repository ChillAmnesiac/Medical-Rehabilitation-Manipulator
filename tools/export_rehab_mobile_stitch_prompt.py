#!/usr/bin/env python3
"""Render a Google Stitch execution prompt from a rehab mobile repair packet."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_REPAIR_PACKET = Path("docs/stitch/rehab-mobile-l1-repair-packet-20260706.json")


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bullet(items: list[Any], *, indent: str = "- ") -> list[str]:
    return [f"{indent}{item}" for item in items]


def _front_failures_section(packet: dict[str, Any]) -> list[str]:
    lines = ["## Frontend Failures To Fix"]
    for failure in packet.get("frontend_failures") or []:
        lines.extend(
            [
                "",
                f"### {failure.get('gate')}",
                f"Summary: {failure.get('summary')}",
            ]
        )
        must_add = failure.get("must_add") or []
        must_remove = failure.get("must_remove") or []
        missing_requirements = failure.get("missing_requirements") or []
        if must_add:
            lines.append("Must add visible/user-facing evidence:")
            lines.extend(_bullet(must_add))
        if must_remove:
            lines.append("Must remove from normal user screens:")
            lines.extend(_bullet(must_remove))
        if missing_requirements:
            lines.append("Missing source/API requirements:")
            lines.extend(_bullet(missing_requirements))
        sample = failure.get("visible_text_sample")
        if sample:
            lines.append("Current visible text sample to replace:")
            lines.append(f"> {sample[:500]}")
    return lines


def _current_fail_section(packet: dict[str, Any]) -> list[str]:
    evidence = packet.get("current_fail_evidence") or []
    lines = ["## Current In-App Browser Failure Evidence"]
    if not evidence:
        lines.append("- No current-fail screenshots are attached in the packet.")
        return lines
    lines.append("Use these screenshots as visual references for what must change. They are not L1 success evidence.")
    for item in evidence:
        dimensions = item.get("dimensions") or {}
        lines.append(
            f"- {item.get('screen')}: {item.get('file')} "
            f"({dimensions.get('width')}x{dimensions.get('height')}), "
            f"counts_for_l1_success = {str(item.get('counts_for_l1_success')).lower()}"
        )
    return lines


def _required_browser_qa_section(packet: dict[str, Any]) -> list[str]:
    lines = ["## Required Final Browser QA Evidence"]
    current = packet.get("browser_evidence_current") or {}
    missing = current.get("missing") or []
    if missing:
        lines.append("Currently missing exact L1 success screenshots:")
        lines.extend(_bullet(missing))
    lines.append("After Stitch deploys the frontend, Codex must capture these exact final screenshots:")
    for item in packet.get("browser_qa_required") or []:
        lines.append(
            f"- {item.get('name')}: {item.get('expected_filename')} at {item.get('viewport')} "
            f"showing {', '.join(item.get('must_show') or [])}"
        )
    return lines


def _verification_section(packet: dict[str, Any]) -> list[str]:
    lines = ["## Codex Verification Commands"]
    lines.append("Codex will reject the frontend until these pass:")
    lines.append("```powershell")
    lines.extend(packet.get("verification_commands", {}).get("powershell") or [])
    lines.append("```")
    return lines


def _post_stitch_bundle_section(packet: dict[str, Any]) -> list[str]:
    artifacts = packet.get("required_artifacts") or {}
    tool = artifacts.get("frontend_release_tool") or "tools/prepare_rehab_mobile_frontend_release.py"
    verifier = artifacts.get("frontend_release_verifier") or "tools/verify_rehab_mobile_frontend_release.py"
    deployer = artifacts.get("frontend_release_deployer") or "tools/deploy_rehab_mobile_frontend_release.py"
    source_dir = (packet.get("target") or {}).get("frontend_edit_scope", "apps/web/public/rehab-arm-mobile/")
    source_arg = source_dir.rstrip("/")
    return [
        "## After Stitch Hands Back Frontend Files",
        "Codex will run the local frontend L1 preflight and package the generated assets before cloud deployment:",
        "```powershell",
        (
            ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe "
            f"tools\\qa_rehab_mobile_l1_frontend.py --source-dir {source_arg} "
            "--output artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json"
        ),
        (
            ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe "
            f"{tool} --source-dir {source_arg} --output-dir artifacts/rehab-mobile-frontend-release"
        ),
        (
            ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe "
            f"{verifier} "
            "--manifest artifacts/rehab-mobile-frontend-release/rehab-mobile-frontend-release-manifest.json "
            "--output artifacts/rehab-mobile-frontend-release/frontend-release-verification.json"
        ),
        (
            ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe "
            f"{deployer} --manifest artifacts/rehab-mobile-frontend-release/rehab-mobile-frontend-release-manifest.json"
        ),
        "```",
    ]


def render_prompt(packet: dict[str, Any], *, generated_at: str | None = None) -> str:
    target = packet.get("target") or {}
    artifacts = packet.get("required_artifacts") or {}
    summary = packet.get("summary") or {}
    lines = [
        "# Stitch Execution Prompt V4 - Rehab Mobile L1 Closure",
        "",
        f"Generated: {generated_at or _utc_now()}",
        "",
        "Repository: https://github.com/wenjunyong666/ai-",
        "Branch: app/rehab-arm-mobile-stitch",
        f"Frontend path: {target.get('frontend_edit_scope', 'apps/web/public/rehab-arm-mobile/')}",
        "",
        "Edit only frontend files. Do not change backend code.",
        "",
        f"Live API base: {target.get('api_base')}",
        f"Deployed web base: {target.get('web_base')}",
        f"Sanitized API fixture: {artifacts.get('api_fixture')}",
        f"Runbook: {artifacts.get('stitch_runbook')}",
        "",
        "Do not hard-code fixture values. Use the fixture only to understand response shape and required field names.",
        "",
        "## Current Status",
        f"- Stitch blockers: {', '.join(summary.get('stitch_blockers') or [])}",
        f"- Non-Stitch blockers: {', '.join(summary.get('non_stitch_blockers') or [])}",
        "",
        "Important: Stitch cannot clear agent_cloud_model by UI work alone. The frontend must still render model readiness honestly.",
        "",
    ]
    lines.extend(_current_fail_section(packet))
    lines.append("")
    lines.extend(_front_failures_section(packet))
    lines.append("")
    lines.append("## Integration Gaps")
    lines.extend(_bullet(packet.get("integration_gaps") or []))
    lines.append("")
    lines.extend(_required_browser_qa_section(packet))
    lines.append("")
    lines.extend(_post_stitch_bundle_section(packet))
    lines.append("")
    lines.extend(_verification_section(packet))
    lines.append("")
    lines.append("Deliver a patient-facing mobile app first screen, not a debug console or engineering workflow.")
    lines.append("")
    return "\n".join(lines)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repair-packet", type=Path, default=DEFAULT_REPAIR_PACKET)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--generated-at")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    packet = _load_json(args.repair_packet)
    prompt = render_prompt(packet, generated_at=args.generated_at)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(prompt, encoding="utf-8")
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
