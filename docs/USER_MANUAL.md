# User Manual

## Build

```powershell
$env:RTT_EXEC_PATH='D:\RT-ThreadStudio\repo\Extract\ToolChain_Support_Packages\ARM\GNU_Tools_for_ARM_Embedded_Processors\13.3\bin'
python -m SCons -j8
```

Flash `rtthread.hex` together with the matching WHD resource image using the existing `program_with_resources.bat` workflow. Confirm KitProg3 is physically present before flashing.

## Latency validation

Use the matching M33 shell command `m55qa_xz_latency` and benchmark script. A valid record is emitted only after M55 successfully writes the first audio block to `sound0`.

If 900 ms EOU clips speech, change `XIAOZHI_EOU_SILENCE_MS` to 1100 ms and rebuild. If 1 slot/80 ms causes underrun or queue loss, use 2 slots/120 ms. Never accept faster timing with truncation, `tts_send_timeout`, queue loss, I2S underrun, WebSocket failure, or wake failure.

Do not run motor or motion commands during voice latency QA. Do not request a CM55 restart while M33 BLE is active.

## Persistent provisioning check

After setting WiFi and the scoped XiaoZhi relay token, require this status before treating provisioning as complete:

```text
saved=1 storage=0 wlan=1
xz_token=1 xz_ws=1 xz_stage=70
tx_pending=0
```

Perform one no-erase board reset and check the same fields again. `wifi_save ret=0` by itself is not proof of persistence. Never place a vendor model API key on the board; use only a scoped `rehab-relay.v1` token bound to the intended project and device.

Application-only flashing at `0x60580400` does not erase the configuration sectors at `0x60FF0000-0x60FFFFFF`. Do not use a chip erase when updating M55 unless configuration loss is intentional and reprovisioning is planned.

## End-of-utterance behavior

Both wake-word and manual/LVGL turns use the same rule: after speech has been confirmed, 900 ms of continuous silence ends listening and starts the next processing stage. The 12-second recording limit is a fault cap, not the normal interaction delay.

Validate with short and long sentences. Pass requires listening to end near 900 ms after the last syllable with no clipped ending. If real speech endings are clipped, use 1100 ms; do not raise the room-noise activity sensitivity. PCM probe mode intentionally bypasses auto EOU for deterministic QA audio injection.
