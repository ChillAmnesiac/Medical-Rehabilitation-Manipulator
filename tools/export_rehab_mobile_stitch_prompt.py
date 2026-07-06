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
DEFAULT_UI_CONTRACT = "docs/stitch/rehab-mobile-l1-ui-contract-20260707.json"

EXACT_VISIBLE_COPY = {
    "home.html": ("查看康复师建议", "问康复师"),
    "profile.html": ("我的康复档案", "手机号", "绑定手机号", "验证码"),
    "device.html": ("绑定设备", "打开康复设备电源"),
    "ai-plan.html": ("问康复师",),
}


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bullet(items: list[Any], *, indent: str = "- ") -> list[str]:
    return [f"{indent}{item}" for item in items]


def _inline_list(items: list[Any]) -> str:
    return ", ".join(str(item) for item in items) if items else "none"


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


def _html_entity_text(term: str) -> str:
    return "".join(f"&#x{ord(char):X};" for char in term)


def _exact_visible_copy_section() -> list[str]:
    lines = [
        "## Exact Release-Gated Visible Copy",
        "Do not paraphrase, translate, rename, or replace these strings with synonyms.",
        "They must appear verbatim as visible HTML text on the listed page:",
    ]
    for page, terms in EXACT_VISIBLE_COPY.items():
        lines.append(f"- {page}: {', '.join(terms)}")
    lines.extend(
        [
            "",
            "Stitch must reject its own output if any generated page replaces these strings with softer copy such as 开始康复训练, 康复助手, 咨询治疗师, or 设备连接.",
            "",
            "HTML entity fallback snippets tested through Stitch MCP:",
            "Use these snippets when Stitch starts rewriting Chinese labels. Browser-visible text still decodes to the required Chinese copy.",
        ]
    )
    for page, terms in EXACT_VISIBLE_COPY.items():
        lines.append(f"- {page}:")
        for term in terms:
            entity_text = _html_entity_text(term)
            if term == "问康复师":
                lines.append(f'  - `<button type="button" aria-label="{entity_text}">{entity_text}</button>`')
            else:
                lines.append(f"  - `<span>{entity_text}</span>`")
    return lines


def _source_scope_section(packet: dict[str, Any]) -> list[str]:
    target = packet.get("target") or {}
    required_pages = target.get("required_frontend_pages") or []
    lines = [
        "## Source Scope",
        f"- Source branch: {target.get('frontend_branch') or 'app/rehab-arm-mobile-stitch'}",
    ]
    source_commit = target.get("frontend_source_commit")
    if source_commit:
        lines.append(f"- Source commit verified by Codex: {source_commit}")
    lines.extend(
        [
            f"- Web frontend edit path: {target.get('frontend_edit_scope') or 'apps/web/public/rehab-arm-mobile/'}",
            f"- APK WebView mirror path: {target.get('android_webview_mirror_scope') or 'apps/mobile/rehab-arm-android/www/'}",
            f"- APK WebView mirror required: {str(bool(target.get('apk_webview_mirror_required'))).lower()}",
        ]
    )
    if required_pages:
        lines.append(f"- Required mobile pages: {', '.join(str(page) for page in required_pages)}")
    lines.append("")
    lines.append(
        "Stitch must make the web pages pass first. Before APK packaging, the accepted web assets must be mirrored into the APK WebView path so installed APK behavior matches the deployed web app."
    )
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


def _deployed_browser_qa_section(packet: dict[str, Any]) -> list[str]:
    deployed = packet.get("deployed_browser_qa")
    if not isinstance(deployed, dict) or not deployed:
        return []
    lines = [
        "## Current Deployed Browser QA Blockers",
        "These are the latest in-app browser QA failures from the deployed cloud frontend. Fix these, not just the older candidate screenshots.",
        f"- metrics: {deployed.get('metrics_path')}",
        f"- raw metrics/screenshots: {deployed.get('raw_path')}",
        f"- status: {deployed.get('status')}",
        f"- checked_pages: {_inline_list(deployed.get('checked_pages') or [])}",
        f"- missing_pages: {_inline_list(deployed.get('missing_pages') or [])}",
    ]
    screenshots = deployed.get("screenshots") if isinstance(deployed.get("screenshots"), dict) else {}
    if screenshots:
        lines.append("- deployed screenshots:")
        for page, screenshot in screenshots.items():
            lines.append(f"  - {page}: {screenshot}")
    fake_hits = deployed.get("fake_hits") if isinstance(deployed.get("fake_hits"), list) else []
    if fake_hits:
        lines.append("- remove visible fake/debug copy from normal patient screens:")
        for item in fake_hits:
            if isinstance(item, dict):
                lines.append(f"  - fake/debug copy: {item.get('page')} -> {item.get('term')}")
    touch_issues = deployed.get("touch_issues") if isinstance(deployed.get("touch_issues"), list) else []
    if touch_issues:
        lines.append("- fix undersized touch targets:")
        for item in touch_issues:
            if not isinstance(item, dict):
                continue
            lines.append(
                "  - touch target: "
                f"{item.get('page')} {item.get('tag')} {item.get('text')} "
                f"{item.get('width')}x{item.get('height')} at ({item.get('x')},{item.get('y')})"
            )
    issue_counts = deployed.get("issue_counts") if isinstance(deployed.get("issue_counts"), dict) else {}
    if issue_counts:
        lines.append(f"- issue_counts: {json.dumps(issue_counts, ensure_ascii=False, sort_keys=True)}")
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


def _browser_candidate_blockers_section() -> list[str]:
    return [
        "## Stitch Browser Candidate QA Blockers",
        "The 2026-07-07 four-page entity candidate passed source gates but is still rejected until browser QA blockers are fixed:",
        "- Do not use fake/demo personal names, patient IDs, or mock identities on normal patient screens.",
        "  Do not show 李先生, 张先生, 王女士, 患者A, ID: 8829, or equivalent placeholders. Use neutral 您好 or the authenticated cloud account state only.",
        "- Every interactive element must render at least 48px wide and 48px high at the 390x844 mobile viewport.",
        "  This includes button, a, input, textarea, and any element with role=\"button\".",
        "- Back buttons must render at least 48px by 48px, not icon-size plus small padding.",
        "- Each bottom navigation item must render at least 64px wide and 48px high; do not let links shrink to label/icon content width.",
        "- The Ask Therapist / 问康复师 entry must be an actual button or link with an aria-label and a minimum 48px touch target in both width and height.",
        "  Rejected candidate measurements included a 64x24 header action, a 40x40 back button, and 28x48 bottom-nav links.",
        "- Generated JavaScript must call the real backend endpoints. Do not use mockData, mock response objects, Simulate API response comments, In real app comments, or console-only behavior for phone verification, device binding, or Ask Therapist messages.",
        "  Profile must POST phone verification start/confirm requests with method: 'POST', Device must POST /api/rehab-arm/app/v1/devices/bind with method: 'POST', and Ask Therapist must POST /api/rehab-arm/app/v1/agent/messages with method: 'POST'.",
        "- L1-FRONTEND-PRIVACY-001: Do not hard-code staging email, staging password, Bearer tokens, SMS debug codes, or API keys in generated HTML, JavaScript, comments, or fixtures.",
        "  Read runtime credentials from user input/session storage and read debug_code only from backend responses in staging mode.",
        "- Candidate screenshots are QA evidence only. Do not treat them as final L1 screenshots until the files are applied to the real App branch, mirrored into the APK WebView assets, deployed, and re-captured at exactly 390x844.",
    ]


def _verification_section(packet: dict[str, Any]) -> list[str]:
    lines = ["## Codex Verification Commands"]
    lines.append("Codex will reject the frontend until these pass:")
    lines.append("```powershell")
    lines.extend(packet.get("verification_commands", {}).get("powershell") or [])
    lines.append("```")
    return lines


def _ops_readiness_section(packet: dict[str, Any]) -> list[str]:
    lines = ["## Non-Stitch Ops Readiness"]
    warnings = packet.get("ops_readiness_warnings") or []
    actions = packet.get("non_stitch_actions") or []
    if not warnings and not actions:
        lines.append("- No backend/provider ops warnings are recorded in this packet.")
        return lines
    if warnings:
        lines.append("These items cannot be fixed by frontend UI alone, but the UI must render their states honestly:")
        for item in warnings:
            lines.append(f"- {item.get('warning')}: {item.get('gate')} {item.get('status')} - {item.get('summary')}")
    if actions:
        lines.append("")
        lines.append("Backend/Ops follow-up commands:")
        for action in actions:
            lines.extend(
                [
                    f"- {action.get('blocker')}",
                    f"  Runbook: {action.get('runbook')}",
                    f"  Preflight: `{action.get('preflight_command')}`",
                    f"  Configure: `{action.get('configure_command')}`",
                ]
            )
    return lines


def _stitch_boundary_note(summary: dict[str, Any]) -> str:
    non_stitch = set(summary.get("non_stitch_blockers") or [])
    ops_warnings = set(summary.get("ops_warnings") or [])
    if "agent_cloud_model" in non_stitch:
        return (
            "Important: Stitch cannot clear agent_cloud_model by UI work alone. "
            "The frontend must still render model/SMS readiness honestly."
        )
    if ops_warnings:
        return (
            "Important: Stitch cannot clear provider-readiness warnings by UI work alone. "
            "The frontend must render those states honestly."
        )
    return "Important: backend/API blockers are clear in this packet; focus Stitch work on frontend L1 behavior and final browser evidence."


def _post_stitch_bundle_section(packet: dict[str, Any]) -> list[str]:
    artifacts = packet.get("required_artifacts") or {}
    tool = artifacts.get("frontend_release_tool") or "tools/prepare_rehab_mobile_frontend_release.py"
    verifier = artifacts.get("frontend_release_verifier") or "tools/verify_rehab_mobile_frontend_release.py"
    mirror_verifier = artifacts.get("webview_mirror_verifier") or "tools/verify_rehab_mobile_webview_mirror.py"
    deployer = artifacts.get("frontend_release_deployer") or "tools/deploy_rehab_mobile_frontend_release.py"
    source_dir = (packet.get("target") or {}).get("frontend_edit_scope", "apps/web/public/rehab-arm-mobile/")
    mirror_dir = (packet.get("target") or {}).get(
        "android_webview_mirror_scope",
        "apps/mobile/rehab-arm-android/www/",
    )
    source_arg = source_dir.rstrip("/")
    mirror_arg = mirror_dir.rstrip("/")
    source_ps = source_arg.replace("/", "\\")
    mirror_ps = mirror_arg.replace("/", "\\")
    return [
        "## After Stitch Hands Back Frontend Files",
        "Codex will run the local frontend L1 preflight and package the generated assets before cloud deployment:",
        "```powershell",
        (
            ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe "
            f"tools\\qa_rehab_mobile_l1_frontend.py --source-dir {source_arg} "
            "--output artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json"
        ),
        f"robocopy {source_ps} {mirror_ps} /MIR",
        "if ($LASTEXITCODE -le 7) { $global:LASTEXITCODE = 0 }",
        (
            ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe "
            f"{tool} --source-dir {source_arg} --output-dir artifacts/rehab-mobile-frontend-release"
        ),
        (
            ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe "
            f"{mirror_verifier} --web-dir {source_arg} --android-www-dir {mirror_arg} "
            "--output artifacts/rehab-mobile-frontend-release/webview-mirror-verification.json"
        ),
        (
            ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe "
            "tools\\qa_rehab_mobile_browser_metrics.py "
            "--input artifacts/rehab-mobile-frontend-release/browser-metrics-l1-390x844.json "
            "--output artifacts/rehab-mobile-frontend-release/browser-metrics-gate.json"
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
        f"L1 UI contract: {artifacts.get('ui_contract') or DEFAULT_UI_CONTRACT}",
        f"Runbook: {artifacts.get('stitch_runbook')}",
        "",
        "Use the L1 UI contract for visible copy, page fields, and action API wiring. Use the full fixture only to understand raw response shape and required field names.",
        "Do not hard-code fixture values.",
        "",
    ]
    lines.extend(_exact_visible_copy_section())
    lines.append("")
    lines.extend(_browser_candidate_blockers_section())
    lines.extend(
        [
            "",
            "## Current Status",
            f"- Stitch blockers: {_inline_list(summary.get('stitch_blockers') or [])}",
            f"- Non-Stitch blockers: {_inline_list(summary.get('non_stitch_blockers') or [])}",
            f"- Ops warnings: {_inline_list(summary.get('ops_warnings') or [])}",
            "",
            _stitch_boundary_note(summary),
            "",
        ]
    )
    lines.extend(_source_scope_section(packet))
    lines.append("")
    lines.extend(_current_fail_section(packet))
    lines.append("")
    deployed_lines = _deployed_browser_qa_section(packet)
    if deployed_lines:
        lines.extend(deployed_lines)
        lines.append("")
    lines.extend(_front_failures_section(packet))
    lines.append("")
    lines.append("## Integration Gaps")
    lines.extend(_bullet(packet.get("integration_gaps") or []))
    lines.append("")
    lines.extend(_ops_readiness_section(packet))
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
