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
