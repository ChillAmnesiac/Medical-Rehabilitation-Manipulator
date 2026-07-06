#!/usr/bin/env python3
"""Export a Stitch repair packet from the current rehab mobile L1 gates."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qa_rehab_mobile_l1_objective_audit  # noqa: E402
import qa_rehab_mobile_l1_release  # noqa: E402


DEFAULT_REQUIRED_ARTIFACTS = {
    "stitch_prompt": "docs/stitch/rehab-mobile-l1-stitch-execution-v3-20260706.md",
    "stitch_runbook": "docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md",
    "api_fixture": "docs/stitch/rehab-mobile-l1-api-fixture-20260706.json",
    "scorecard": "docs/qa/rehab-mobile-20260706/APP_COMPLETION_SCORECARD.md",
    "qa_report": "docs/qa/rehab-mobile-20260706/QA_REPORT.md",
    "model_relay_runbook": "docs/deployments/rehab-mobile-agent-model-relay-runbook-20260706.md",
}

NON_STITCH_REQUIREMENTS = {"agent_cloud_model"}
META_REQUIREMENTS = {"combined_l1_release"}

BROWSER_QA_REQUIRED = [
    {
        "name": "home_first_screen",
        "expected_filename": "l1-home-390.png",
        "viewport": "390x844",
        "must_show": ["one clear next action"],
    },
    {
        "name": "ask_therapist_chat",
        "expected_filename": "l1-ask-therapist-chat-390.png",
        "viewport": "390x844",
        "must_show": ["问康复师", "chat input", "safe answer"],
    },
    {
        "name": "unsafe_agent_refusal",
        "expected_filename": "l1-unsafe-agent-refusal-390.png",
        "viewport": "390x844",
        "must_show": ["protective Chinese refusal", "no direct motion control"],
    },
    {
        "name": "device_binding_wizard",
        "expected_filename": "l1-device-binding-wizard-390.png",
        "viewport": "390x844",
        "must_show": ["绑定设备", "打开康复设备电源"],
    },
    {
        "name": "profile_phone_medical",
        "expected_filename": "l1-profile-phone-medical-390.png",
        "viewport": "390x844",
        "must_show": ["cloud account", "verified phone", "safe medical empty state"],
    },
]


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _failed_requirements(objective_payload: dict[str, Any]) -> list[str]:
    summary = objective_payload.get("summary") or {}
    blockers = summary.get("blocking_requirements")
    if isinstance(blockers, list):
        return [item for item in blockers if isinstance(item, str)]
    return [
        item.get("requirement")
        for item in objective_payload.get("requirements") or []
        if isinstance(item, dict) and item.get("status") != "PASS" and isinstance(item.get("requirement"), str)
    ]


def _frontend_failures(release_payload: dict[str, Any]) -> list[dict[str, Any]]:
    failures = []
    for result in (release_payload.get("frontend") or {}).get("results") or []:
        if not isinstance(result, dict) or result.get("status") == "PASS":
            continue
        detail = result.get("detail") if isinstance(result.get("detail"), dict) else {}
        failures.append(
            {
                "gate": result.get("gate"),
                "status": result.get("status"),
                "summary": result.get("summary"),
                "page_url": detail.get("url"),
                "must_add": detail.get("missing_terms") or [],
                "must_remove": detail.get("forbidden_hits") or [],
                "missing_requirements": detail.get("missing_requirements") or [],
                "checked_pages": detail.get("checked_pages") or [],
                "visible_text_sample": detail.get("text_prefix"),
            }
        )
    return failures


def _integration_gaps(frontend_failures: list[dict[str, Any]]) -> list[str]:
    gaps: list[str] = []
    for failure in frontend_failures:
        for requirement in failure.get("missing_requirements") or []:
            if isinstance(requirement, str):
                gaps.append(requirement)
    return _dedupe(gaps)


def _release_blockers(release_payload: dict[str, Any]) -> list[str]:
    blockers = (release_payload.get("summary") or {}).get("blocking_gates")
    return [item for item in blockers if isinstance(item, str)] if isinstance(blockers, list) else []


def _split_blockers(
    objective_payload: dict[str, Any], release_payload: dict[str, Any]
) -> tuple[list[str], list[str], list[str]]:
    failed_requirements = _failed_requirements(objective_payload)
    non_stitch = [item for item in failed_requirements if item in NON_STITCH_REQUIREMENTS]
    meta = [item for item in failed_requirements if item in META_REQUIREMENTS]
    stitch = [
        item for item in failed_requirements if item not in NON_STITCH_REQUIREMENTS and item not in META_REQUIREMENTS
    ]
    for blocker in _release_blockers(release_payload):
        if blocker == "agent_cloud_model":
            non_stitch.append(blocker)
        elif blocker == "frontend_l1_gate":
            stitch.append(blocker)
    return _dedupe(stitch), _dedupe(non_stitch), _dedupe(meta)


def build_repair_packet(
    release_payload: dict[str, Any],
    objective_payload: dict[str, Any],
    *,
    generated_at: str | None = None,
    api_base: str = "http://106.55.62.122:8011",
    web_base: str = "http://106.55.62.122:3001/rehab-arm-mobile",
    apk_url: str = "http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk",
    required_artifacts: dict[str, str] | None = None,
    ) -> dict[str, Any]:
    frontend_failures = _frontend_failures(release_payload)
    stitch_blockers, non_stitch_blockers, meta_blockers = _split_blockers(objective_payload, release_payload)
    artifacts = dict(DEFAULT_REQUIRED_ARTIFACTS)
    if required_artifacts:
        artifacts.update(required_artifacts)
    return {
        "schema": "rehab-mobile-stitch-repair-packet/v1",
        "generated_at": generated_at or _utc_now(),
        "target": {
            "api_base": api_base,
            "web_base": web_base,
            "apk_url": apk_url,
            "frontend_edit_scope": "apps/web/public/rehab-arm-mobile/",
        },
        "summary": {
            "overall": (objective_payload.get("summary") or {}).get("overall")
            or (release_payload.get("summary") or {}).get("overall"),
            "release_overall": (release_payload.get("summary") or {}).get("overall"),
            "objective_overall": (objective_payload.get("summary") or {}).get("overall"),
            "stitch_blockers": stitch_blockers,
            "non_stitch_blockers": non_stitch_blockers,
            "meta_blockers": meta_blockers,
        },
        "required_artifacts": artifacts,
        "stitch_rules": [
            "Use the live API contract and sanitized fixture; do not hard-code fixture values.",
            "Only change frontend assets under apps/web/public/rehab-arm-mobile/.",
            "Normal patient screens must not expose raw engineering terms such as M33, M55, UUID, Gatekeeper, setup_required, or direct motor control copy.",
            "Ask Therapist must call /api/rehab-arm/app/v1/agent/messages with the bearer token and must render unsafe refusals.",
        ],
        "frontend_failures": frontend_failures,
        "integration_gaps": _integration_gaps(frontend_failures),
        "non_stitch_actions": [
            {
                "blocker": "agent_cloud_model",
                "owner": "Codex/backend ops once a real model endpoint and key are available",
                "runbook": artifacts["model_relay_runbook"],
                "command": "python tools/configure_rehab_model_relay.py --base-url <OPENAI_COMPATIBLE_BASE_URL> --model <MODEL> --api-key <API_KEY>",
            }
        ]
        if "agent_cloud_model" in non_stitch_blockers
        else [],
        "browser_qa_required": BROWSER_QA_REQUIRED,
        "verification_commands": {
            "powershell": [
                "$env:REHAB_QA_EMAIL='3245056131@qq.com'",
                "$env:REHAB_QA_PASSWORD='1234'",
                ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe tools\\qa_rehab_mobile_l1_release.py",
                ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe tools\\qa_rehab_mobile_l1_objective_audit.py",
                "curl.exe -I -sS http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk",
            ]
        },
        "raw_summaries": {
            "release": release_payload.get("summary") or {},
            "objective": objective_payload.get("summary") or {},
        },
    }


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _run_release_gate(args: argparse.Namespace) -> dict[str, Any]:
    release_args = qa_rehab_mobile_l1_release.parse_args(
        [
            "--api-base",
            args.api_base,
            "--web-base",
            args.web_base,
            "--web-origin",
            args.web_origin,
            "--apk-url",
            args.apk_url,
            "--timeout",
            str(args.timeout),
        ]
        + (["--email", args.email] if args.email else [])
        + (["--password", args.password] if args.password else [])
    )
    _, payload = qa_rehab_mobile_l1_release.run(release_args)
    return payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-json", type=Path)
    parser.add_argument("--objective-json", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--generated-at")
    parser.add_argument("--screenshots-dir", type=Path, default=Path("docs/qa/rehab-mobile-20260706/screenshots"))
    parser.add_argument("--api-base", default=os.getenv("REHAB_QA_API_BASE", "http://106.55.62.122:8011"))
    parser.add_argument("--web-base", default=os.getenv("REHAB_QA_WEB_BASE", "http://106.55.62.122:3001/rehab-arm-mobile"))
    parser.add_argument("--web-origin", default=os.getenv("REHAB_QA_WEB_ORIGIN", "http://106.55.62.122:3001"))
    parser.add_argument(
        "--apk-url",
        default=os.getenv(
            "REHAB_QA_APK_URL",
            "http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk",
        ),
    )
    parser.add_argument("--email", default=os.getenv("REHAB_QA_EMAIL"))
    parser.add_argument("--password", default=os.getenv("REHAB_QA_PASSWORD"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    release_payload = _load_json(args.release_json) if args.release_json else _run_release_gate(args)
    objective_payload = (
        _load_json(args.objective_json)
        if args.objective_json
        else qa_rehab_mobile_l1_objective_audit.audit_objective(release_payload, args.screenshots_dir)
    )
    packet = build_repair_packet(
        release_payload,
        objective_payload,
        generated_at=args.generated_at,
        api_base=args.api_base,
        web_base=args.web_base,
        apk_url=args.apk_url,
    )
    rendered = json.dumps(packet, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
