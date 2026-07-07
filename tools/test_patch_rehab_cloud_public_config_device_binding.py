import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("patch_rehab_cloud_public_config_device_binding.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("patch_rehab_cloud_public_config_device_binding", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_patch_public_config_marks_static_device_binding_as_blocked():
    module = _load_module()
    source = '''
            "phone_verification": {
                "start_endpoint": "/api/rehab-arm/app/v1/account/phone-verifications",
                "confirm_endpoint_template": "/api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm",
                "resend_cooldown_seconds": get_settings().rehab_arm_phone_verification_resend_cooldown_seconds,
                "delivery_status": _phone_delivery_status(),
            },
            "m33_legacy_spp_profile": LEGACY_M33_SPP_PROFILE,
            "downloads": {
                "debug_apk_status": "backend_connected_workflow_action_timeline_ai_training_planner_training_library_backend_plan_binding_stitch_bluetooth_debug_spp_pairing_backend_bind_frame_ack_sensor_debug_build_current_m33_confirmation_pending",
            },
            "release_gate": {
                "status": "blocked",
                "reason": "debug_apk_connects_backend_and_has_legacy_spp_native_bridge_but_current_m33_firmware_confirmation_and_physical_pairing_validation_are_still_required",
                "checks": [
                    {
                        "code": "APK_FRONTEND_API_WIRING",
                        "status": "pass",
                        "description": "Debug APK 1.0.10 loads public-config/catalog/workflow, uses Bearer token login, overlays backend workflow/readiness, renders backend care timeline/daily care plan, binds the training library to backend plans after AI draft acceptance, can execute safe workflow actions through /me/workflow/actions, and includes a Stitch-designed Bluetooth debug page for Android SPP pairing, backend device binding, backend-approved frame send, and inbound ACK/sensor evidence upload.",
                    },
                    {
                        "code": "PHONE_NATIVE_BLUETOOTH_BRIDGE",
                        "status": "debug_bridge_available",
                        "description": "APK 1.0.10 includes a Capacitor/Android Bluetooth Classic SPP bridge plus a Stitch-designed Bluetooth debug page for listing paired devices, binding one as a backend trusted device, connecting SPP, sending backend-approved legacy frames, and uploading inbound ACK/sensor evidence. User release still needs physical validation with current M33 firmware.",
                    },
                ],
                "required_frontend_work": [
                    "use the legacy SPP profile through the Android native bridge for phone-to-M33 Bluetooth Classic transport instead of Web Bluetooth GATT",
                ],
            },
'''

    patched, changed = module.patch_public_config_text(source)

    assert changed is True
    assert '"device_binding": {' in patched
    assert '"bind_endpoint": "/api/rehab-arm/app/v1/devices/bind"' in patched
    assert '"status": "missing_in_current_apk"' in patched
    assert '"status": "partial_static_device_binding_blocked"' in patched
    assert '"required_for_real_pairing": True' in patched
    assert '"window.RehabArmBluetoothBridge"' in patched
    assert '"window.Capacitor.Plugins.RehabArmBluetooth"' in patched
    assert '"web_fallback": "show_unavailable_state_do_not_fake_devices"' in patched
    assert "debug_bridge_available" not in patched
    assert "stitch_bluetooth_debug_spp_pairing_backend_bind_frame_ack_sensor_debug_build" not in patched
