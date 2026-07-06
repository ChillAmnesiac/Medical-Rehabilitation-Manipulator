import importlib.util
import sys
from pathlib import Path


def test_frontend_integration_contract_passes_when_stitch_uses_required_api_contracts():
    module = _load_module()

    sources = {
        "home.html": """
          localStorage.setItem('access_token', token);
          fetch('/api/auth/session');
          fetch('/api/rehab-arm/app/v1/me', { headers: { Authorization: `Bearer ${token}` } });
          const home = response.data.patient_view.home;
          const agent = response.data.patient_view.agent;
          <button aria-label="问康复师">问康复师</button>
        """,
        "profile.html": """
          const profile = response.data.patient_view.profile;
          fetch('/api/rehab-arm/app/v1/account/phone-verifications');
          fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`);
          if (error.code === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(error.retry_after);
          if (error.code === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
          if (error.code === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
        """,
        "device.html": """
          const device = response.data.patient_view.device;
          fetch('/api/rehab-arm/app/v1/devices/bind');
          if (error.code === 'DEVICE_ALREADY_BOUND') showAlreadyBound();
        """,
        "ai-plan.html": """
          const agent = response.data.patient_view.agent;
          fetch('/api/rehab-arm/app/v1/agent/messages');
          if (error.code === 'UNSAFE_MOTION_REQUEST') showSafeRefusal();
          renderModelStatus(response.data.model_status);
        """,
    }

    result = module.check_frontend_integration_contract(sources)

    assert result.status == "PASS"
    assert result.detail["missing_requirements"] == []


def test_frontend_integration_contract_fails_when_pages_only_change_copy():
    module = _load_module()

    sources = {
        "home.html": "<h1>Ask therapist</h1><p>Review plan</p>",
        "profile.html": "<h1>Profile</h1><p>Phone verified</p>",
        "device.html": "<h1>Bind device</h1><p>Power on device</p>",
        "ai-plan.html": "<h1>Ask therapist</h1>",
    }

    result = module.check_frontend_integration_contract(sources)

    assert result.status == "FAIL"
    assert "auth_session" in result.detail["missing_requirements"]
    assert "patient_view_profile" in result.detail["missing_requirements"]
    assert "agent_messages" in result.detail["missing_requirements"]


def test_frontend_integration_contract_requires_l1_interaction_states():
    module = _load_module()

    sources = {
        "home.html": """
          localStorage.setItem('access_token', token);
          fetch('/api/auth/session');
          fetch('/api/rehab-arm/app/v1/me', { headers: { Authorization: `Bearer ${token}` } });
          const home = response.data.patient_view.home;
          const agent = response.data.patient_view.agent;
        """,
        "profile.html": """
          const profile = response.data.patient_view.profile;
          fetch('/api/rehab-arm/app/v1/account/phone-verifications', { method: 'POST' });
          fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`, { method: 'POST' });
        """,
        "device.html": """
          const device = response.data.patient_view.device;
          fetch('/api/rehab-arm/app/v1/devices/bind', { method: 'POST' });
        """,
        "ai-plan.html": """
          const agent = response.data.patient_view.agent;
          fetch('/api/rehab-arm/app/v1/agent/messages', { method: 'POST' });
        """,
    }

    result = module.check_frontend_integration_contract(sources)

    assert result.status == "FAIL"
    assert "agent_unsafe_refusal" in result.detail["missing_requirements"]
    assert "agent_model_status" in result.detail["missing_requirements"]
    assert "device_already_bound" in result.detail["missing_requirements"]
    assert "phone_resend_cooldown" in result.detail["missing_requirements"]
    assert "ask_therapist_accessibility" in result.detail["missing_requirements"]


def test_frontend_integration_contract_accepts_html_entity_accessibility_label():
    module = _load_module()

    sources = {
        "home.html": """
          localStorage.setItem('access_token', token);
          fetch('/api/auth/session');
          fetch('/api/rehab-arm/app/v1/me', { headers: { Authorization: `Bearer ${token}` } });
          const home = response.data.patient_view.home;
          const agent = response.data.patient_view.agent;
          <button aria-label="&#38382;&#24247;&#22797;&#24072;">&#38382;&#24247;&#22797;&#24072;</button>
        """,
        "profile.html": """
          const profile = response.data.patient_view.profile;
          fetch('/api/rehab-arm/app/v1/account/phone-verifications');
          fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`);
          if (error.code === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(error.retry_after);
          if (error.code === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
          if (error.code === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
        """,
        "device.html": """
          const device = response.data.patient_view.device;
          fetch('/api/rehab-arm/app/v1/devices/bind');
          if (error.code === 'DEVICE_ALREADY_BOUND') showAlreadyBound();
        """,
        "ai-plan.html": """
          const agent = response.data.patient_view.agent;
          fetch('/api/rehab-arm/app/v1/agent/messages');
          if (error.code === 'UNSAFE_MOTION_REQUEST') showSafeRefusal();
          renderModelStatus(response.data.model_status);
        """,
    }

    result = module.check_frontend_integration_contract(sources)

    assert "ask_therapist_accessibility" not in result.detail["missing_requirements"]


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


def test_profile_gate_requires_phone_binding_and_code_copy():
    module = _load_module()

    required_terms = module.PAGE_GATES["profile.html"]["required_terms"]

    assert "手机号" in required_terms
    assert "绑定手机号" in required_terms
    assert "验证码" in required_terms


def test_device_gate_requires_patient_binding_wizard_copy():
    module = _load_module()

    required_terms = module.PAGE_GATES["device.html"]["required_terms"]

    assert "设备" in required_terms
    assert "绑定设备" in required_terms
    assert "打开康复设备电源" in required_terms


def test_home_gate_requires_clear_therapist_next_action_copy():
    module = _load_module()

    required_terms = module.PAGE_GATES["home.html"]["required_terms"]

    assert "查看康复师建议" in required_terms
    assert "问康复师" in required_terms
