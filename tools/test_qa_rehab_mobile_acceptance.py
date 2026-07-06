import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("qa_rehab_mobile_acceptance.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_acceptance", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_agent_model_status_accepts_cloud_and_fallback_modes():
    module = _load_module()

    assert module.agent_model_status_ok(
        {
            "data": {
                "answer": "patient answer",
                "model_status": {
                    "mode": "cloud_model",
                    "configured": True,
                    "provider": "openai_compatible",
                    "model": "rehab-cloud-model",
                },
            }
        }
    )
    assert module.agent_model_status_ok(
        {
            "data": {
                "answer": "patient answer",
                "model_status": {
                    "mode": "fallback_rule_based",
                    "configured": False,
                    "fallback_reason": "external_model_not_configured",
                },
            }
        }
    )


def test_agent_model_status_rejects_missing_or_ambiguous_status():
    module = _load_module()

    assert not module.agent_model_status_ok({"data": {"answer": "patient answer"}})
    assert not module.agent_model_status_ok({"data": {"model_status": {"mode": "unknown"}}})
