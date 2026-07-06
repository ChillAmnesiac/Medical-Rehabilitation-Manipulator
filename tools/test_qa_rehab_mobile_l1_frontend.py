import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("qa_rehab_mobile_l1_frontend.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_l1_frontend", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_patient_page_without_raw_terms_passes_gate():
    module = _load_module()

    page = "\n".join(
        [
            "康复用户，今天按步骤来",
            "绑定康复设备",
            "问康复师",
            "手机号已验证",
            "待完善",
        ]
    )

    result = module.check_page(
        "home",
        page,
        required_terms=["问康复师", "绑定康复设备"],
        forbidden_terms=module.L1_FORBIDDEN_TERMS,
    )

    assert result.status == "PASS"
    assert result.detail["missing_terms"] == []
    assert result.detail["forbidden_hits"] == []


def test_engineering_page_with_raw_terms_fails_gate():
    module = _load_module()

    page = "\n".join(
        [
            "网络未连接，请检查后端服务",
            "康复工作流",
            "setup_required",
            "M33 BLE",
            "动作队列",
        ]
    )

    result = module.check_page(
        "home",
        page,
        required_terms=["问康复师", "绑定康复设备"],
        forbidden_terms=module.L1_FORBIDDEN_TERMS,
    )

    assert result.status == "FAIL"
    assert "问康复师" in result.detail["missing_terms"]
    assert "setup_required" in result.detail["forbidden_hits"]
    assert "M33" in result.detail["forbidden_hits"]
