from __future__ import annotations

import argparse
from pathlib import Path


PHONE_BLOCK_ANCHOR = '''            "phone_verification": {
                "start_endpoint": "/api/rehab-arm/app/v1/account/phone-verifications",
                "confirm_endpoint_template": "/api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm",
                "resend_cooldown_seconds": get_settings().rehab_arm_phone_verification_resend_cooldown_seconds,
                "delivery_status": _phone_delivery_status(),
            },
            "m33_legacy_spp_profile": LEGACY_M33_SPP_PROFILE,
'''

PHONE_BLOCK_WITH_DEVICE_BINDING = '''            "phone_verification": {
                "start_endpoint": "/api/rehab-arm/app/v1/account/phone-verifications",
                "confirm_endpoint_template": "/api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm",
                "resend_cooldown_seconds": get_settings().rehab_arm_phone_verification_resend_cooldown_seconds,
                "delivery_status": _phone_delivery_status(),
            },
            "device_binding": {
                "bind_endpoint": "/api/rehab-arm/app/v1/devices/bind",
                "list_endpoint": "/api/rehab-arm/app/v1/devices",
                "native_bluetooth_bridge": {
                    "status": "missing_in_current_apk",
                    "required_for_real_pairing": True,
                    "expected_bridge_names": [
                        "window.RehabArmBluetoothBridge",
                        "window.Capacitor.Plugins.RehabArmBluetooth",
                    ],
                    "required_methods": [
                        "requestBluetoothPermissions",
                        "scanDevices",
                        "connect",
                    ],
                },
                "web_fallback": "show_unavailable_state_do_not_fake_devices",
                "control_boundary": "backend_binding_requires_real_user_selected_native_bluetooth_device",
            },
            "m33_legacy_spp_profile": LEGACY_M33_SPP_PROFILE,
'''

REPLACEMENTS = {
    '"debug_apk_status": "backend_connected_workflow_action_timeline_ai_training_planner_training_library_backend_plan_binding_stitch_bluetooth_debug_spp_pairing_backend_bind_frame_ack_sensor_debug_build_current_m33_confirmation_pending"': (
        '"debug_apk_status": "backend_connected_workflow_action_timeline_ai_training_planner_training_library_backend_plan_binding_device_binding_ui_static_blocked_until_native_bridge_and_stitch_runtime_wiring"'
    ),
    '"reason": "debug_apk_connects_backend_and_has_legacy_spp_native_bridge_but_current_m33_firmware_confirmation_and_physical_pairing_validation_are_still_required"': (
        '"reason": "debug_apk_connects_backend_but_current_user_device_pairing_ui_is_static_and_native_bluetooth_bridge_is_not_exposed_to_stitch_runtime"'
    ),
    '''                    {
                        "code": "APK_FRONTEND_API_WIRING",
                        "status": "pass",''': '''                    {
                        "code": "APK_FRONTEND_API_WIRING",
                        "status": "partial_static_device_binding_blocked",''',
    '"description": "Debug APK 1.0.10 loads public-config/catalog/workflow, uses Bearer token login, overlays backend workflow/readiness, renders backend care timeline/daily care plan, binds the training library to backend plans after AI draft acceptance, can execute safe workflow actions through /me/workflow/actions, and includes a Stitch-designed Bluetooth debug page for Android SPP pairing, backend device binding, backend-approved frame send, and inbound ACK/sensor evidence upload."': (
        '"description": "Debug APK 1.0.10 loads the backend API contract, but the current user-facing Device page still shows static demo search results. Real pairing remains blocked until Stitch runtime UI calls the native Bluetooth bridge and backend /devices/bind only after a user-selected hardware device."'
    ),
    '"status": "debug_bridge_available"': '"status": "missing_in_current_apk"',
    '"description": "APK 1.0.10 includes a Capacitor/Android Bluetooth Classic SPP bridge plus a Stitch-designed Bluetooth debug page for listing paired devices, binding one as a backend trusted device, connecting SPP, sending backend-approved legacy frames, and uploading inbound ACK/sensor evidence. User release still needs physical validation with current M33 firmware."': (
        '"description": "Browser QA shows the current Stitch Device page does not expose window.RehabArmBluetoothBridge or window.Capacitor.Plugins.RehabArmBluetooth and still renders a static demo device. The app must show an unavailable state instead of fake devices until the native bridge is present."'
    ),
    '"use the legacy SPP profile through the Android native bridge for phone-to-M33 Bluetooth Classic transport instead of Web Bluetooth GATT"': (
        '"use a native Bluetooth bridge exposed as window.RehabArmBluetoothBridge or window.Capacitor.Plugins.RehabArmBluetooth; when missing, show unavailable state and never fake devices"'
    ),
}


def patch_public_config_text(source: str) -> tuple[str, bool]:
    patched = source
    if PHONE_BLOCK_ANCHOR in patched and '"device_binding": {' not in patched:
        patched = patched.replace(PHONE_BLOCK_ANCHOR, PHONE_BLOCK_WITH_DEVICE_BINDING, 1)

    for old, new in REPLACEMENTS.items():
        patched = patched.replace(old, new)

    return patched, patched != source


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch live rehab app public-config device binding status.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = args.input.read_text(encoding="utf-8")
    patched, changed = patch_public_config_text(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(patched, encoding="utf-8")
    print("changed" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
