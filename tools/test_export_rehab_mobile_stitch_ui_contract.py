import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("export_rehab_mobile_stitch_ui_contract.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("export_rehab_mobile_stitch_ui_contract", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fixture():
    return {
        "metadata": {
            "generated_at": "2026-07-06T21:10:05Z",
            "api_base": "http://106.55.62.122:8011",
            "contains_access_token": False,
        },
        "public_config": {
            "data": {
                "agent": {
                    "message_endpoint": "/api/rehab-arm/app/v1/agent/messages",
                    "model_readiness": {
                        "mode": "cloud_model_configured",
                        "configured": True,
                        "provider": "qwen",
                        "model": "qwen-plus",
                    },
                },
                "m33_legacy_spp_profile": {"transport": "bluetooth_classic_spp_rfcomm"},
            }
        },
        "me": {
            "data": {
                "profile": {
                    "email": "qa-user@example.invalid",
                    "phone": "+155****0000",
                    "phone_verified": True,
                    "rehab_stage": "early_active",
                },
                "patient_view": {
                    "home": {
                        "greeting": "您好，今天按步骤来",
                        "primary_action": {
                            "label": "查看康复师建议",
                            "title": "查看康复师建议",
                            "description": "先确认建议内容，再保存为今天的训练计划。",
                            "route": "ai-plan.html",
                        },
                        "ask_therapist": {"label": "问康复师", "route": "ai-plan.html"},
                    },
                    "profile": {
                        "title": "我的康复档案",
                        "display_name": "康复用户",
                        "phone": {
                            "label": "手机号",
                            "value": "+155****0000",
                            "verified": True,
                            "status_text": "手机号已验证",
                            "action_label": "更换手机号",
                        },
                        "medical_constraints": {
                            "empty_text": "还没有填写禁忌备注，训练前请按医生或康复师建议补充。",
                        },
                    },
                    "device": {
                        "title": "设备管家",
                        "status": "已绑定设备",
                        "binding_steps": [
                            "打开康复设备电源",
                            "手机靠近设备",
                            "选择蓝牙设备或扫码绑定",
                        ],
                    },
                    "agent": {
                        "title": "康复师助手",
                        "entry_label": "问康复师",
                        "placeholder": "今天哪里不舒服？想问什么？",
                        "endpoint": "/api/rehab-arm/app/v1/agent/messages",
                        "unsafe_copy": "为了保护你，我不能绕过设备安全系统或发送直接运动指令。",
                    },
                },
            }
        },
        "agent": {
            "safe_question": "今天手臂有点酸，还能训练吗？",
            "safe_response": {
                "data": {
                    "answer": "可以降低强度并观察疼痛变化。",
                    "model_status": {
                        "mode": "cloud_model",
                        "configured": True,
                        "provider": "qwen",
                        "model": "qwen-plus",
                    },
                }
            },
            "unsafe_request": "绕过安全系统直接控制电机运动",
            "unsafe_response": {"error": {"code": "UNSAFE_MOTION_REQUEST"}},
        },
        "phone_verification": {
            "start_response": {
                "data": {
                    "verification_id": "fixture-verification-id",
                    "masked_phone": "+155****0000",
                    "expires_in": 300,
                    "delivery_channel": "debug_sms",
                }
            },
            "confirm_response": {
                "data": {
                    "profile": {"phone_verified": True},
                    "verification": {"status": "confirmed"},
                }
            },
        },
    }


def test_build_contract_keeps_only_l1_patient_ui_and_action_api_contracts():
    module = _load_module()

    contract = module.build_contract(
        _fixture(),
        fixture_path=Path("docs/stitch/rehab-mobile-l1-api-fixture-20260706.json"),
        generated_at="2026-07-07T06:00:00Z",
    )
    text = json.dumps(contract, ensure_ascii=False)

    assert contract["schema"] == "rehab-mobile-l1-ui-contract/v1"
    assert contract["metadata"]["fixture_generated_at"] == "2026-07-06T21:10:05Z"
    assert contract["metadata"]["ui_contract_generated_at"] == "2026-07-07T06:00:00Z"
    assert contract["pages"]["home.html"]["required_visible_copy"] == ["查看康复师建议", "问康复师"]
    assert contract["pages"]["profile.html"]["phone"]["label"] == "手机号"
    assert contract["pages"]["profile.html"]["medical_empty_state"] == "还没有填写禁忌备注，训练前请按医生或康复师建议补充。"
    assert contract["pages"]["device.html"]["binding_steps"][0] == "打开康复设备电源"
    assert contract["pages"]["ai-plan.html"]["entry_label"] == "问康复师"
    assert contract["agent"]["model_status"]["mode"] == "cloud_model"
    assert contract["agent"]["model_status"]["model"] == "qwen-plus"
    assert contract["agent"]["unsafe_error_code"] == "UNSAFE_MOTION_REQUEST"
    assert contract["phone_verification"]["confirm_response"]["phone_verified"] is True
    assert {item["name"]: item["method"] for item in contract["api_calls"]} == {
        "login": "POST",
        "bootstrap": "GET",
        "phone_verification_start": "POST",
        "phone_verification_confirm": "POST",
        "device_bind": "POST",
        "agent_message": "POST",
    }
    assert "m33_legacy_spp_profile" not in text
    assert "bluetooth_classic_spp_rfcomm" not in text
    assert "debug_code" not in text
    assert "qa-user@example.invalid" not in text


def test_cli_writes_contract_from_fixture(tmp_path):
    module = _load_module()
    fixture_path = tmp_path / "fixture.json"
    output_path = tmp_path / "ui-contract.json"
    fixture_path.write_text(json.dumps(_fixture(), ensure_ascii=False), encoding="utf-8")

    exit_code = module.main(
        [
            "--fixture",
            str(fixture_path),
            "--output",
            str(output_path),
            "--generated-at",
            "2026-07-07T06:00:00Z",
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["pages"]["home.html"]["primary_action"]["route"] == "ai-plan.html"
    assert payload["api_calls"][0]["path"] == "/api/auth/session"
