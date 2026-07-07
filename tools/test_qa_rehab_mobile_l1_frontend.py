import importlib.util
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace


def test_frontend_integration_contract_passes_when_stitch_uses_required_api_contracts():
    module = _load_module()

    sources = {
        "home.html": """
          localStorage.setItem('access_token', token);
          fetch('/api/auth/session');
          fetch('/api/rehab-arm/app/v1/me', { headers: { Authorization: `Bearer ${token}` } });
          const home = response.data.patient_view.home;
          const agent = response.data.patient_view.agent;
          <button class="primary-action" data-nav-target="ai-plan.html">Review therapist suggestion</button>
          <button class="ask-therapist-action" data-nav-target="ai-plan.html">Ask therapist</button>
          document.querySelectorAll('[data-nav-target]').forEach((control) => {
            control.addEventListener('click', () => {
              window.location.href = control.getAttribute('data-nav-target');
            });
          });
          <button aria-label="问康复师">问康复师</button>
        """,
        "profile.html": """
          const profile = response.data.patient_view.profile;
          fetch('/api/rehab-arm/app/v1/account/phone-verifications', { method: 'POST' });
          fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`, { method: 'POST' });
          if (error.code === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(error.retry_after);
          if (error.code === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
          if (error.code === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
        """,
        "device.html": """
          const device = response.data.patient_view.device;
          fetch('/api/rehab-arm/app/v1/devices/bind', { method: 'POST' });
          if (error.code === 'DEVICE_ALREADY_BOUND') showAlreadyBound();
        """,
        "ai-plan.html": """
          const agent = response.data.patient_view.agent;
          fetch('/api/rehab-arm/app/v1/agent/messages', { method: 'POST' });
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


def test_frontend_integration_contract_requires_home_actions_to_leave_first_screen():
    module = _load_module()

    sources = {
        "home.html": """
          localStorage.setItem('access_token', token);
          fetch('/api/auth/session');
          fetch('/api/rehab-arm/app/v1/me', { headers: { Authorization: `Bearer ${token}` } });
          const home = response.data.patient_view.home;
          const agent = response.data.patient_view.agent;
          <button class="primary-action">Review therapist suggestion</button>
          <button class="ask-therapist-action" aria-label="&#38382;&#24247;&#22797;&#24072;">Ask therapist</button>
        """,
        "profile.html": """
          const profile = response.data.patient_view.profile;
          fetch('/api/rehab-arm/app/v1/account/phone-verifications', { method: 'POST' });
          fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`, { method: 'POST' });
          if (error.code === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(error.retry_after);
          if (error.code === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
          if (error.code === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
        """,
        "device.html": """
          const device = response.data.patient_view.device;
          fetch('/api/rehab-arm/app/v1/devices/bind', { method: 'POST' });
          if (error.code === 'DEVICE_ALREADY_BOUND') showAlreadyBound();
        """,
        "ai-plan.html": """
          const agent = response.data.patient_view.agent;
          fetch('/api/rehab-arm/app/v1/agent/messages', { method: 'POST' });
          if (error.code === 'UNSAFE_MOTION_REQUEST') showSafeRefusal();
          renderModelStatus(response.data.model_status);
        """,
    }

    result = module.check_frontend_integration_contract(sources)

    assert result.status == "FAIL"
    assert "home_primary_action_navigation" in result.detail["missing_requirements"]
    assert "home_ask_therapist_navigation" in result.detail["missing_requirements"]
    assert "home_navigation_click_handler" in result.detail["missing_requirements"]


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
          fetch('/api/rehab-arm/app/v1/account/phone-verifications', { method: 'POST' });
          fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`, { method: 'POST' });
          if (error.code === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(error.retry_after);
          if (error.code === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
          if (error.code === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
        """,
        "device.html": """
          const device = response.data.patient_view.device;
          fetch('/api/rehab-arm/app/v1/devices/bind', { method: 'POST' });
          if (error.code === 'DEVICE_ALREADY_BOUND') showAlreadyBound();
        """,
        "ai-plan.html": """
          const agent = response.data.patient_view.agent;
          fetch('/api/rehab-arm/app/v1/agent/messages', { method: 'POST' });
          if (error.code === 'UNSAFE_MOTION_REQUEST') showSafeRefusal();
          renderModelStatus(response.data.model_status);
        """,
    }

    result = module.check_frontend_integration_contract(sources)

    assert "ask_therapist_accessibility" not in result.detail["missing_requirements"]


def test_frontend_integration_contract_rejects_mocked_api_behavior():
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
          const mockData = { error: 'PHONE_CODE_RESEND_TOO_SOON', retry_after: 59 };
          const data = mockData; // In real app: await response.json()
          if (data.error === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(data.retry_after);
          if (data.error === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
          if (data.error === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
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

    assert result.status == "FAIL"
    assert "no_mock_api_behavior" in result.detail["missing_requirements"]
    assert "mockData" in result.detail["forbidden_source_hits"]


def test_frontend_integration_contract_rejects_action_endpoints_without_post_methods():
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

    assert result.status == "FAIL"
    assert "phone_verification_start_post" in result.detail["missing_requirements"]
    assert "phone_verification_confirm_post" in result.detail["missing_requirements"]
    assert "device_bind_post" in result.detail["missing_requirements"]
    assert "agent_messages_post" in result.detail["missing_requirements"]


def test_frontend_privacy_gate_rejects_hardcoded_credentials_and_tokens():
    module = _load_module()
    qa_email = "".join(["3245056131", "@", "qq.com"])
    qa_password = "REHAB_QA_PASSWORD='" + "".join(["12", "34"]) + "'"
    bearer_token = "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" + ".fixed-token"
    model_key = "".join(["s", "k", "-"]) + "live-rehab-mobile-hardcoded-key"

    sources = {
        "home.html": f"""
          const stagingEmail = '{qa_email}';
          const token = '{bearer_token}';
        """,
        "profile.html": f"""
          const qaPassword = "{qa_password}";
          const verification = {{ debug_code: "123456" }};
        """,
        "device.html": """
          const stitchApiKey = 'X-Goog-Api-Key: AQ.Ab8RN6LAEbdSD6c938v6w0';
        """,
        "ai-plan.html": f"""
          const modelKey = '{model_key}';
        """,
    }

    result = module.check_frontend_privacy_contract(sources)

    assert result.status == "FAIL"
    assert "hardcoded_email" in result.detail["privacy_hits"]
    assert "hardcoded_bearer_token" in result.detail["privacy_hits"]
    assert "hardcoded_debug_code" in result.detail["privacy_hits"]
    assert "staging_env_secret" in result.detail["privacy_hits"]
    assert "hardcoded_api_key" in result.detail["privacy_hits"]


def test_frontend_privacy_gate_allows_runtime_token_and_debug_code_handling():
    module = _load_module()

    sources = {
        "home.html": """
          const token = session.access_token;
          fetch('/api/rehab-arm/app/v1/me', { headers: { Authorization: `Bearer ${token}` } });
        """,
        "profile.html": """
          if (response.delivery_channel === 'debug_sms' && response.debug_code) {
            renderStagingHelper(response.debug_code);
          }
        """,
        "device.html": "const device = response.data.patient_view.device;",
        "ai-plan.html": "const screenshotName = 'l1-ask-therapist-chat-390.png'; const modelStatus = response.data.model_status;",
    }

    result = module.check_frontend_privacy_contract(sources)

    assert result.status == "PASS"
    assert result.detail["privacy_hits"] == []


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


def test_patient_page_with_demo_identity_fails_gate():
    module = _load_module()

    page = "\n".join(
        [
            "下午好，李先生",
            "今天感觉如何？",
            "查看康复师建议",
            "问康复师",
        ]
    )

    result = module.check_page(
        "home",
        page,
        required_terms=module.PAGE_GATES["home.html"]["required_terms"],
        forbidden_terms=module.L1_FORBIDDEN_TERMS,
    )

    assert result.status == "FAIL"
    assert "李先生" in result.detail["forbidden_hits"]


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


def test_emit_json_writes_utf8_when_console_encoding_cannot_represent_text():
    module = _load_module()

    class GbkLikeStdout:
        def __init__(self):
            self.buffer = io.BytesIO()

        def write(self, text):
            raise UnicodeEncodeError("gbk", text, 0, 1, "illegal multibyte sequence")

    payload = {"summary": {"overall": "PASS"}, "text": "‹康复师›"}
    stdout = GbkLikeStdout()

    module.emit_json(payload, stdout=stdout)

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    assert stdout.buffer.getvalue() == rendered.encode("utf-8")


def test_run_web_base_fails_when_root_entry_serves_404_shell():
    module = _load_module()
    base = "http://example.test/rehab-arm-mobile"
    contract_sources = {
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
          fetch('/api/rehab-arm/app/v1/account/phone-verifications', { method: 'POST' });
          fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`, { method: 'POST' });
          if (error.code === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(error.retry_after);
          if (error.code === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
          if (error.code === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
        """,
        "device.html": """
          const device = response.data.patient_view.device;
          fetch('/api/rehab-arm/app/v1/devices/bind', { method: 'POST' });
          if (error.code === 'DEVICE_ALREADY_BOUND') showAlreadyBound();
        """,
        "ai-plan.html": """
          const agent = response.data.patient_view.agent;
          fetch('/api/rehab-arm/app/v1/agent/messages', { method: 'POST' });
          if (error.code === 'UNSAFE_MOTION_REQUEST') showSafeRefusal();
          renderModelStatus(response.data.model_status);
        """,
    }

    def fake_fetch_source_bundle(url, timeout):
        page = url.rsplit("/", 1)[-1]
        return contract_sources[page]

    def fake_fetch_text(url, timeout):
        if url == base:
            return 404, "页面未找到", {"x-nextjs-page": "/_not-found"}
        page = url.rsplit("/", 1)[-1]
        return 200, " ".join(module.PAGE_GATES[page]["required_terms"]), {}

    module.fetch_source_bundle = fake_fetch_source_bundle
    module.fetch_text = fake_fetch_text

    exit_code, payload = module.run(SimpleNamespace(web_base=base, source_dir=None, timeout=1))

    assert exit_code == 1
    root_result = next(result for result in payload["results"] if result["gate"] == "L1-FRONTEND-ROOT-001")
    assert root_result["status"] == "FAIL"
    assert root_result["detail"]["status_code"] == 404
