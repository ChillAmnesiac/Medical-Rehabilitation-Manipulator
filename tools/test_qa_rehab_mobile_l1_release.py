import importlib.util
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

    api_payload = {"summary": {"overall": "PASS", "p0_failed": 0, "total": 14}}
    frontend_payload = {"summary": {"overall": "PASS", "failed": 0, "total": 4}}

    exit_code, payload = module.summarize_release(api_payload, frontend_payload)

    assert exit_code == 0
    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["blocking_gates"] == []
