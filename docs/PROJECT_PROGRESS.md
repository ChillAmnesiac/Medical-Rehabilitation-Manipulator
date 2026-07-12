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
