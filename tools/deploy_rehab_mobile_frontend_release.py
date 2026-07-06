#!/usr/bin/env python3
"""Deploy a verified rehab mobile frontend release manifest to staging.

The tool is intentionally conservative:
- it verifies the manifest before any deploy command is exposed as executable,
- it defaults to dry-run,
- --execute is required before scp/ssh commands are run,
- --run-post-verify is required whenever --execute is used.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import verify_rehab_mobile_frontend_release  # noqa: E402


EXPECTED_REMOTE_WEB_ROOT = "/home/ubuntu/apps/ai-collab/apps/web/public/rehab-arm-mobile"
CommandRunner = Callable[[str], Any]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _default_runner(command: str) -> None:
    subprocess.run(command, shell=True, check=True)


def _safe_remote_web_root(value: Any) -> bool:
    return isinstance(value, str) and value == EXPECTED_REMOTE_WEB_ROOT


def _manifest_deploy(manifest: dict[str, Any]) -> dict[str, Any]:
    deploy = manifest.get("deploy") if isinstance(manifest.get("deploy"), dict) else {}
    return deploy


def _manifest_verification(manifest: dict[str, Any]) -> dict[str, Any]:
    verification = manifest.get("verification") if isinstance(manifest.get("verification"), dict) else {}
    return verification


def plan_deployment(manifest_path: Path) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    manifest = _load_json(manifest_path)
    verification_payload = verify_rehab_mobile_frontend_release.verify_release_manifest(manifest_path)
    manifest_summary = verification_payload.get("summary") if isinstance(verification_payload.get("summary"), dict) else {}
    deploy = _manifest_deploy(manifest)
    verification = _manifest_verification(manifest)
    remote_web_root = deploy.get("remote_web_root")
    if not _safe_remote_web_root(remote_web_root):
        raise ValueError("unsafe_remote_web_root")

    deploy_commands = deploy.get("commands") if isinstance(deploy.get("commands"), list) else []
    post_commands = verification.get("powershell") if isinstance(verification.get("powershell"), list) else []
    return {
        "manifest_path": str(manifest_path),
        "manifest_verification": manifest_summary,
        "remote_web_root": remote_web_root,
        "deploy_commands": [str(command) for command in deploy_commands],
        "post_deploy_verification": {
            "commands": [str(command) for command in post_commands],
            "required_browser_screenshots": verification.get("required_browser_screenshots") or [],
        },
    }


def _execute_commands(commands: list[str], command_runner: CommandRunner) -> list[str]:
    executed: list[str] = []
    for command in commands:
        command_runner(command)
        executed.append(command)
    return executed


def _powershell_encoded_command(commands: list[str]) -> str:
    script = "$ErrorActionPreference = 'Stop'\n" + "\n".join(commands)
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    return f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded}"


def run(argv: list[str], command_runner: CommandRunner = _default_runner) -> tuple[int, dict[str, Any]]:
    args = parse_args(argv)
    executed: list[str] = []
    try:
        plan = plan_deployment(args.manifest)
    except ValueError as exc:
        return 2, {"error": str(exc), "executed": executed}
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        return 2, {"error": str(exc), "executed": executed}

    summary: dict[str, Any] = {
        **plan,
        "dry_run": not args.execute,
        "run_post_verify": bool(args.run_post_verify),
        "executed": executed,
    }
    if plan["manifest_verification"].get("overall") != "PASS":
        return 2, summary
    if not args.execute:
        return 0, summary
    if not args.run_post_verify:
        summary["error"] = "post_deploy_verification_required"
        return 2, summary

    executed.extend(_execute_commands(plan["deploy_commands"], command_runner))
    if args.run_post_verify:
        post_verify_command = _powershell_encoded_command(plan["post_deploy_verification"]["commands"])
        command_runner(post_verify_command)
        executed.append(post_verify_command)
    return 0, summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("artifacts/rehab-mobile-frontend-release/rehab-mobile-frontend-release-manifest.json"),
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--run-post-verify", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    exit_code, payload = run(argv)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
