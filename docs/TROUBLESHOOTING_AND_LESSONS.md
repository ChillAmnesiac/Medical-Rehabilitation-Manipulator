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
