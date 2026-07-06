import argparse
import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("smoke_rehab_model_provider.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("smoke_rehab_model_provider", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _args(**overrides):
    values = {
        "provider": "gemini",
        "base_url": "",
        "model": "gemini-test-model",
        "api_key": "secret-provider-key",
        "message": "My shoulder feels sore after training. Can I continue tomorrow?",
        "timeout": 3,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_gemini_smoke_posts_generate_content_and_redacts_secret():
    module = _load_module()
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse(
            200,
            {
                "candidates": [
                    {"content": {"parts": [{"text": "Lower intensity first; pause and contact a therapist if pain worsens."}]}}
                ]
            },
        )

    exit_code, summary = module.run(_args(), opener=fake_urlopen)

    assert exit_code == 0
    assert captured["timeout"] == 3
    assert captured["request"].full_url == (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-test-model:generateContent"
    )
    assert captured["request"].get_header("X-goog-api-key") == "secret-provider-key"
    payload = json.loads(captured["request"].data.decode("utf-8"))
    assert payload["contents"][0]["parts"][0]["text"] == "My shoulder feels sore after training. Can I continue tomorrow?"
    assert summary["request"]["api_key"] == "<redacted>"
    assert "secret-provider-key" not in json.dumps(summary, ensure_ascii=False)
    assert summary["answer_present"] is True
    assert "Lower intensity" in summary["answer_preview"]


def test_openai_compatible_smoke_posts_chat_completions_and_parses_answer():
    module = _load_module()
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        return FakeResponse(200, {"choices": [{"message": {"content": "Warm up first, control pain, and pause if needed."}}]})

    exit_code, summary = module.run(
        _args(
            provider="openai_compatible",
            base_url="https://model.example/v1/",
            model="rehab-chat",
        ),
        opener=fake_urlopen,
    )

    assert exit_code == 0
    assert captured["request"].full_url == "https://model.example/v1/chat/completions"
    assert captured["request"].get_header("Authorization") == "Bearer secret-provider-key"
    payload = json.loads(captured["request"].data.decode("utf-8"))
    assert payload["model"] == "rehab-chat"
    assert payload["messages"][0]["role"] == "user"
    assert summary["request"]["base_url"] == "https://model.example/v1"
    assert summary["answer_present"] is True


def test_smoke_fails_when_provider_returns_no_answer():
    module = _load_module()

    def fake_urlopen(request, timeout):
        return FakeResponse(200, {"candidates": [{"content": {"parts": [{"text": ""}]}}]})

    exit_code, summary = module.run(_args(), opener=fake_urlopen)

    assert exit_code == 3
    assert summary["status"] == "provider_invalid_response"
    assert summary["answer_present"] is False


def test_main_redacts_secret_when_required_field_missing(capsys):
    module = _load_module()

    exit_code = module.main(["--provider", "gemini", "--model", "gemini-test-model", "--api-key", "secret-provider-key"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "secret-provider-key" not in captured.out
    assert "message" in captured.out
