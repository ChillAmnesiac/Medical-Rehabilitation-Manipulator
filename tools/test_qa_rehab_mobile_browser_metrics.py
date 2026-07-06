import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("qa_rehab_mobile_browser_metrics.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_browser_metrics", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_browser_metrics_fail_when_touch_target_is_too_small():
    module = _load_module()

    payload = [
        {
            "page": "ai-plan",
            "metrics": {
                "fakeHits": [],
                "touchIssues": [
                    {"tag": "A", "text": "home\n首页", "width": 28, "height": 48, "x": 27, "y": 780}
                ],
                "inputIssues": [],
                "overflows": [],
                "verticalTextIssues": [],
            },
        }
    ]

    result = module.evaluate_browser_metrics(payload)

    assert result["summary"]["overall"] == "FAIL"
    assert result["summary"]["failed"] == 1
    assert result["results"][0]["gate"] == "L1-BROWSER-METRICS-001"
    assert result["results"][0]["detail"]["touch_issues"][0]["page"] == "ai-plan"


def test_browser_metrics_pass_when_all_visual_issue_lists_are_empty():
    module = _load_module()

    payload = [
        {
            "page": "home",
            "metrics": {
                "fakeHits": [],
                "touchIssues": [],
                "inputIssues": [],
                "overflows": [],
                "verticalTextIssues": [],
            },
        },
        {
            "page": "profile",
            "metrics": {
                "fakeHits": [],
                "touchIssues": [],
                "inputIssues": [],
                "overflows": [],
                "verticalTextIssues": [],
            },
        },
    ]

    result = module.evaluate_browser_metrics(payload)

    assert result["summary"]["overall"] == "PASS"
    assert result["summary"]["failed"] == 0
    assert result["results"][0]["status"] == "PASS"


def test_browser_metrics_preserves_existing_failed_gate_report():
    module = _load_module()

    payload = {
        "summary": {"overall": "FAIL", "failed": 1, "total": 1},
        "results": [
            {
                "gate": "L1-BROWSER-METRICS-001",
                "level": "L1",
                "status": "FAIL",
                "summary": "Rendered mobile browser QA has no undersized touch targets.",
                "detail": {
                    "checked_pages": ["ai-plan"],
                    "fake_hits": [],
                    "touch_issues": [{"page": "ai-plan", "width": 40, "height": 40}],
                    "input_issues": [],
                    "overflow_issues": [],
                    "vertical_text_issues": [],
                },
            }
        ],
    }

    result = module.evaluate_browser_metrics(payload)

    assert result["summary"]["overall"] == "FAIL"
    assert result["summary"]["failed"] == 1
    assert result["results"][0]["status"] == "FAIL"
    assert result["results"][0]["detail"]["touch_issues"][0]["page"] == "ai-plan"
