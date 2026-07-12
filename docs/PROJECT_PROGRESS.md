# Project Progress

## 2026-07-12 - XiaoZhi latency instrumentation and first response tuning

Completed:
- Created and pushed `WEN/m55-xiaozhi-latency-20260712@4b7e143` from `origin/M55@7298c28`.
- Replaced the fixed XiaoZhi session id with per-turn ids in the form `m55-<boot_tick>-<turn_seq>`.
- Added monotonic timestamps for wake, listen, last voice, stop, STT, LLM, TTS start, first queued audio packet, and the first successful non-zero `sound0` write.
- Added one `VOICE_LATENCY` IPC record per successful turn. It contains timing/results only, never provider credentials, transcripts, or audio.
- Changed auto EOU silence from 1400 ms to 900 ms and TTS prebuffer from 2 slots/180 ms to 1 slot/80 ms for hardware evaluation.

Validated:
- Static latency contract test passed.
- GCC 13.3 build passed: `text=1720996 data=81472 bss=4531716`.
- `rtthread.hex` SHA256 is `654de32ce1c2d79b02bf1d1230607d728d8c22f5d8f73f11eaa65c09fedc965f`.

Unverified:
- KitProg3 and COM26 were absent, so this image and WHD resources were not flashed.
- EOU truncation, I2S underrun, TTS queue loss, wake re-arm, and 30 real-mic turns still require board validation.

Next:
- Flash this M55 image together with `whd_resources_all.bin`, then flash matching M33 `WEN/m33-xiaozhi-latency-20260712@1451b351` and run the benchmark in the M33 worktree.

## 2026-07-12 - Persisted WiFi and XiaoZhi token after LVGL firmware recovery

Completed:
- Added dedicated FAL partitions `wifi_cfg` and `xiaozhi_cfg` at resource-flash offsets `0x1F0000` and `0x1F8000`, 32 KB each.
- Reduced the unused tail of the existing filesystem partition from 1024 KB to 960 KB so every partition remains inside the 2 MB `norflash0` window at `0x60E00000-0x60FFFFFF`.
- Restored the current M55 image after the old-firmware diagnostic temporarily changed the LVGL presentation.
- Reprovisioned WiFi without logging credentials and issued a new scoped relay token for project `e201f41c-25a6-46e1-baf8-be6dcb83284c`, device `nanopi-m5`.

Validated:
- GCC 13.3 build passed: `text=1721124 data=81472 bss=4531724`.
- Flashed M55 HEX SHA256 `38F0CE5D0C24C773783FA53CFABCDCF46DAAB436103079FC56572DEAA117766F` through KitProg3 `1C161868022E2400`; OpenOCD wrote 1,806,336 bytes and verified 1,802,596 bytes.
- After a no-erase hardware reset, status automatically returned to `saved=1 storage=0 wlan=1 xz_token=1 xz_ws=1 xz_stage=70 tx_pending=0`.
- LVGL flush count continued increasing with `lcd_last=0` and `lvgl_last=0`; current latency branch contains no LVGL layout diff from `origin/M55@7298c28`.
- M33 loop count increased from `0x646` to `0x65A` in two seconds. Secure and Non-secure CFSR/HFSR were all zero.

Unverified:
- Physical panel alignment cannot be machine-observed from the serial/debug interfaces; the operator should confirm the current screen after reset.

Next:
- Continue the planned XiaoZhi latency benchmark without reflashing or erasing the new configuration sectors.
