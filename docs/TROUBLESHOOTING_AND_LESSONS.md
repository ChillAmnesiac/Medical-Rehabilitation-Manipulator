# Troubleshooting And Lessons

## 2026-07-12 - Measure the first real speaker write, not first packet processing

Symptoms:
- The first implementation published latency after processing the first TTS queue item.
- A packet smaller than the 4096-byte `sound0` write block could return from the decoder while PCM was still only buffered, making the reported first-audio time artificially early.

Root cause:
- Queue/decode completion is not the product metric. The required endpoint is the first successful non-zero `rt_device_write(sound0, ...)`.

Fix / trick:
- Set `latency_first_packet_tick` only after the payload is accepted into the bounded queue.
- Publish `VOICE_LATENCY` immediately after the first successful `sound0` write, including the final partial-block flush path.
- Keep QA text, manual/probe, and real-wake turns distinguishable with flags.

Status:
- Fixed in code and protected by a static regression test; hardware timing remains unverified.

## 2026-07-12 - SCons can return zero after rejecting a placeholder toolchain

- `rtconfig.py` defaults to `C:\Users\XXYYZZ`; set `RTT_EXEC_PATH` to the RT-Thread Studio GCC 13.3 `bin` directory.
- Require fresh ELF/HEX timestamps and `arm-none-eabi-size` output. Do not treat the process exit code alone as a successful build.

## 2026-07-12 - WiFi/token appeared writable but disappeared after reset

Symptoms:
- `m55qa_wifi_save` returned zero, but voice status stayed at `saved=0 storage=-255`.
- A token worked in RAM, then `xz_token=0 token_len=0` after firmware reset or flash.
- Temporarily flashing an older M55 image also made the LVGL layout appear shifted.

Root cause:
- `wifi_config_service.c` and `xiaozhi_voice_relay.c` used FAL partitions named `wifi_cfg` and `xiaozhi_cfg`, but `fal_cfg.h` did not define either partition.
- The file fallback was unavailable, so both values were volatile despite the M33 bridge reporting only that the IPC request was accepted.
- An initial attempted placement at offsets `0x200000` and above was invalid because `norflash0` starts at `0x60E00000` and is only 2 MB. That invalidated the FAL table and produced WHD stage 11/result 4002 (`FILE_OPEN_FAIL`).

Fix / trick:
- Keep all FAL offsets relative to `FLASH_START_ADDRESS`, not the full SMIF base.
- Reserve the final 64 KB inside the 2 MB window: 960 KB filesystem, 32 KB WiFi config, and 32 KB XiaoZhi token config.
- Treat `saved=1 storage=0` plus a no-erase reset and automatic `xz_token=1` reload as the persistence acceptance test.
- Never print WiFi credentials, relay tokens, or token chunks in logs.

Status:
- Fixed and hardware-validated on KitProg3 `1C161868022E2400`.
