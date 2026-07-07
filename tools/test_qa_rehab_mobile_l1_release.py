import importlib.util
import io
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("qa_rehab_mobile_l1_release.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_l1_release", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_release_summary_fails_when_frontend_gate_fails():
    module = _load_module()

    api_payload = {"summary": {"overall": "PASS", "p0_failed": 0, "total": 14}}
    frontend_payload = {"summary": {"overall": "FAIL", "failed": 4, "total": 4}}

    exit_code, payload = module.summarize_release(api_payload, frontend_payload)

    assert exit_code == 1
    assert payload["summary"]["overall"] == "FAIL"
    assert payload["summary"]["api_overall"] == "PASS"
    assert payload["summary"]["frontend_overall"] == "FAIL"
    assert "frontend_l1_gate" in payload["summary"]["blocking_gates"]


def test_release_summary_passes_when_api_and_frontend_pass():
    module = _load_module()

    api_payload = {
        "summary": {"overall": "PASS", "p0_failed": 0, "total": 14},
        "results": [
            {"gate": "P1-AGENT-CONFIG-001", "status": "PASS"},
            {"gate": "P1-AGENT-MODEL-001", "status": "PASS"},
        ],
    }
    frontend_payload = {"summary": {"overall": "PASS", "failed": 0, "total": 4}}
    apk_webview_payload = {"summary": {"overall": "PASS", "failed": 0, "total": 3}}

    exit_code, payload = module.summarize_release(api_payload, frontend_payload, apk_webview_payload)

    assert exit_code == 0
    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["blocking_gates"] == []
    assert payload["summary"]["apk_webview_assets_overall"] == "PASS"


def test_release_summary_blocks_l1_when_rehab_agent_uses_fallback_rules():
    module = _load_module()

    api_payload = {
        "summary": {"overall": "PASS", "p0_failed": 0, "total": 22},
        "results": [
            {"gate": "P1-AGENT-CONFIG-001", "status": "WARN"},
            {"gate": "P1-AGENT-MODEL-001", "status": "WARN"},
        ],
    }
    frontend_payload = {"summary": {"overall": "PASS", "failed": 0, "total": 5}}
    apk_webview_payload = {"summary": {"overall": "PASS", "failed": 0, "total": 3}}

    exit_code, payload = module.summarize_release(api_payload, frontend_payload, apk_webview_payload)

    assert exit_code == 1
    assert payload["summary"]["overall"] == "FAIL"
    assert "agent_cloud_model" in payload["summary"]["blocking_gates"]


def test_release_summary_blocks_l1_when_apk_webview_assets_fail():
    module = _load_module()

    api_payload = {
        "summary": {"overall": "PASS", "p0_failed": 0, "total": 22},
        "results": [
            {"gate": "P1-AGENT-CONFIG-001", "status": "PASS"},
            {"gate": "P1-AGENT-MODEL-001", "status": "PASS"},
        ],
    }
    frontend_payload = {"summary": {"overall": "PASS", "failed": 0, "total": 5}}
    apk_webview_payload = {"summary": {"overall": "FAIL", "failed": 3, "total": 3}}

    exit_code, payload = module.summarize_release(api_payload, frontend_payload, apk_webview_payload)

    assert exit_code == 1
    assert payload["summary"]["overall"] == "FAIL"
    assert payload["summary"]["apk_webview_assets_overall"] == "FAIL"
    assert "apk_webview_assets" in payload["summary"]["blocking_gates"]
    assert payload["apk_webview_assets"] == apk_webview_payload


def test_release_summary_blocks_l1_without_apk_webview_assets_evidence():
    module = _load_module()

    api_payload = {
        "summary": {"overall": "PASS", "p0_failed": 0, "total": 22},
        "results": [
            {"gate": "P1-AGENT-CONFIG-001", "status": "PASS"},
            {"gate": "P1-AGENT-MODEL-001", "status": "PASS"},
        ],
    }
    frontend_payload = {"summary": {"overall": "PASS", "failed": 0, "total": 5}}

    exit_code, payload = module.summarize_release(api_payload, frontend_payload)

    assert exit_code == 1
    assert payload["summary"]["overall"] == "FAIL"
    assert payload["summary"]["apk_webview_assets_overall"] is None
    assert "apk_webview_assets" in payload["summary"]["blocking_gates"]


def test_emit_json_writes_utf8_when_console_encoding_cannot_represent_text():
    module = _load_module()

    class GbkLikeStdout:
        def __init__(self):
            self.buffer = io.BytesIO()

        def write(self, text):
            raise UnicodeEncodeError("gbk", text, 0, 1, "illegal multibyte sequence")

    payload = {"summary": {"overall": "FAIL"}, "text": "‹ 问康复师"}
    stdout = GbkLikeStdout()

    module.emit_json(payload, stdout=stdout)

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    assert stdout.buffer.getvalue() == rendered.encode("utf-8")
