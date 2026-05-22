# RobStride CH340 USB-CAN AT Protocol Note

Date: 2026-05-22
Owner: Codex
Target branch: nanopi-sdk

## Why This Exists

The CH340 USB-CAN adapter currently on the NanoPi did not respond to
LAWICEL/SLCAN commands at the tested UART rates. A `slcand`-created `can_usb0`
interface can still show local TX echo, but that does not prove the adapter
sent or received anything on the CAN wires.

The Windows upper-computer package at:

```text
D:\电机上位机\CAN-USB-data-conversion\switch\mainwindow.cpp
D:\电机上位机\CAN-USB-data-conversion\switch\mainwindow.h
```

shows a different binary serial protocol. This note extracts the useful part so
the NanoPi can test the adapter directly through `/dev/ttyUSB0`.

## Frame Format

Serial packet:

```text
41 54 <encoded_addr_be32> <dlc> <0..8 data bytes> 0D 0A
 A  T
```

The Qt source builds the logical extended CAN id fields first:

```text
logical_can_id = (id << 24) | (data << 8) | (mode << 3) | res
encoded_addr   = (logical_can_id << 3) | 0x00000004
```

The receive parser reverses this:

```text
logical_can_id = (encoded_addr & ~0x00000004) >> 3
res            = logical_can_id & 0x07
mode           = (logical_can_id >> 3) & 0x1F
data           = (logical_can_id >> 8) & 0xFFFF
id             = (logical_can_id >> 24) & 0xFF
```

For the known RobStride Get_ID-style probe:

```text
logical_can_id = 0x0000FD01
payload        = 00
serial packet  = 41 54 00 07 E8 0C 01 00 0D 0A
```

## NanoPi Test Tool

This repo now includes:

```text
nanopi-sdk-improved/scripts/robstride_usbcan_at.py
```

It uses only Python standard library modules on Linux. No `pyserial` package is
required.

Before using it, make sure `slcand` is not holding the port:

```bash
sudo systemctl stop usbcan-slcan.service
sudo pkill -x slcand || true
sudo chmod 666 /dev/ttyUSB0
```

Local encoder self-check:

```bash
python3 nanopi-sdk-improved/scripts/robstride_usbcan_at.py encode --id 0x0000fd01 --data 00
```

Expected output:

```text
41 54 00 07 E8 0C 01 00 0D 0A
```

Send the probe through the adapter:

```bash
python3 nanopi-sdk-improved/scripts/robstride_usbcan_at.py probe-motor \
  --port /dev/ttyUSB0 --baud 2000000 --motor-id 0x01 --master-id 0xfd --wait 1.0
```

Equivalent raw extended-id send:

```bash
python3 nanopi-sdk-improved/scripts/robstride_usbcan_at.py send-ext \
  --port /dev/ttyUSB0 --baud 2000000 --id 0x0000fd01 --data 00 --wait 1.0
```

Listen for frames from the adapter:

```bash
python3 nanopi-sdk-improved/scripts/robstride_usbcan_at.py monitor \
  --port /dev/ttyUSB0 --baud 2000000
```

## Isolation Procedure

Use USB-CAN first to isolate the M33 side from the NanoPi SPI MCP2518FD path.

1. On NanoPi, stop `usbcan-slcan.service`.
2. On M33 serial, run:

```text
cmd_control_init can0
cmd_can_init_min
```

3. On NanoPi, send:

```bash
python3 nanopi-sdk-improved/scripts/robstride_usbcan_at.py send-ext \
  --port /dev/ttyUSB0 --baud 2000000 --id 0x0000fd01 --data 00 --wait 1.0
```

4. On M33 serial, run:

```text
cmd_can_poll_once
```

If M33 FIFO0 receives the frame, the Infineon CAN peripheral, transceiver,
termination, and wiring path are likely usable. Continue debugging the NanoPi
MCP2518FD path separately.

If M33 FIFO0 still stays empty, the remaining suspects are:

- the USB adapter expects a different UART speed or mode setting,
- this CH340 firmware is not the same AT protocol despite the similar package,
- CANH/CANL/termination/common-ground/power is still wrong under live traffic,
- the adapter is not actually transmitting dominant/recessive CAN levels.

## 2026-05-22 Live Test Result

The helper script was copied to the NanoPi at:

```text
/home/pi/nanopi-sdk-improved/scripts/robstride_usbcan_at.py
```

Local encode/decode self-check passed on Windows and NanoPi:

```text
0x0000fd01 + 00 -> 41 54 00 07 E8 0C 01 00 0D 0A
```

After stopping `usbcan-slcan.service`, the AT frame was sent through
`/dev/ttyUSB0` and then M33 FIFO0 was polled:

```text
TX raw=41 54 00 07 E8 0C 01 00 0D 0A can_id=0x0000FD01
cmd_can_poll_once
[can_min] fifo0 status=0x00000000 fill=0
```

The same send was retried at UART baud rates:

```text
2000000, 1000000, 921600, 460800, 230400, 115200
```

M33 still reported `fill=0`.

Reverse direction was also tested: NanoPi monitored the AT serial stream while
M33 sent `cmd_can_send_probe 0x01`. M33 reported:

```text
[can_min] send probe motor=0x01 ext=0x0000fd01 buf=0 ret=0
[can_min] after_send ... txbto=0x00000001
```

NanoPi received no AT packet from the USB adapter during that monitor window.

Current conclusion: the extracted AT frame format is implemented and verified
against the upper-computer source, but the live CH340 module has not yet been
proven to forward between serial and CAN in either direction. The next check
should be the exact adapter model/firmware mode and its required UART speed or
configuration sequence. If this module is actually the CANHUB described in the
PDF, it should appear as native SocketCAN `canX`; the present CH340 serial
enumeration suggests it is a different adapter or a different firmware mode.

## 2026-05-22 Windows Local Retest

The user moved the same RobStride/Lingzu-era CH340 USB-CAN debugger to the
Windows development PC. Windows enumerated it as:

```text
USB\VID_1A86&PID_7523\6&1abc947c&0&2
USB-SERIAL CH340 (COM3)
```

M33 KitProg3 serial was `COM26` at 115200. M33 raw CAN was initialized with:

```text
cmd_can_init_min
[can_min] init ret=0
[can_min] pclk0=20000000 pclk1=20000000
[can_min] after_init ... nbtp=0x06000e03
```

When M33 transmitted `cmd_can_send_probe 0x01`, COM3 received a clean AT packet
at UART `921600`:

```text
41 54 00 07 e8 0c 08 00 00 00 00 00 00 00 00 0d 0a
```

Decoded, this is CAN extended ID `0x0000FD01`, DLC 8, all-zero payload. The
same capture at other UART speeds produced garbage, so this adapter's verified
serial speed is `921600`.

The reverse direction is still not working. Writing the same captured packet
back to COM3 at `921600`, with DTR/RTS tried both true and false, did not make
M33 FIFO0 receive anything:

```text
cmd_can_poll_once
[can_min] fifo0 status=0x00010100 fill=0
```

Conclusion after the Windows retest: this exact CH340 debugger is proven for
CAN-to-USB AT monitoring at `921600`, but USB-to-CAN transmit is not yet proven.
Do not debug M33 receive filtering from this result; first find the debugger's
PC-to-CAN enable/config sequence or confirm whether its firmware/tool only
enables transmit after MotorStudio config.

## 2026-05-22 NanoPi Retest At 921600

Remote NanoPi `192.168.2.66` was checked again after the Windows retest. Live
state:

```text
hostname: NanoPi-M5
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0 -> ../../ttyUSB0
/dev/ttyUSB0
usbcan-slcan.service: inactive
```

With `/dev/ttyUSB0` opened in raw termios mode at UART `921600`, NanoPi captured
M33's raw probe frame:

```text
M33: cmd_can_send_probe 0x01
NanoPi RX:
41 54 00 07 e8 0c 08 00 00 00 00 00 00 00 00 0d 0a
```

This matches the Windows capture exactly. Therefore the NanoPi USB serial path,
the adapter's CAN receive path, and M33 CAN transmit are all working at
`921600`.

The reverse direction still failed on NanoPi. NanoPi wrote the same 17-byte AT
packet to `/dev/ttyUSB0` at `921600`:

```text
REMOTE_TX_N=17
41 54 00 07 e8 0c 08 00 00 00 00 00 00 00 00 0d 0a
```

M33 still reported:

```text
cmd_can_poll_once
[can_min] fifo0 status=0x00010100 fill=0
```

Conclusion: the live NanoPi now proves one-way CAN-to-USB monitoring through the
CH340 debugger. USB-to-CAN transmit remains the blocker and is likely a debugger
firmware/mode/configuration issue, not an Infineon M33 receive-filter issue.

## Answer To "Is This A Real CAN Bus?"

The CH340 side is only USB serial, but the module can still contain a real CAN
controller/transceiver behind that serial protocol. If the module firmware
translates `AT` packets into CAN frames, then the bus side is real CAN and can
communicate with M33.

What is not real is the Linux interface shape: this adapter is not currently a
verified SocketCAN device. Treat `/dev/ttyUSB0` as a vendor serial CAN adapter,
not as `can0`/`can_usb0`, unless a matching driver or firmware mode is proven.

## Notes For The Next AI / Developer

- Do not continue testing this CH340 adapter only with `cansend`/`candump`.
- Use UART `921600` for raw AT monitoring; it was verified on Windows by
  capturing M33's `0x0000FD01` extended probe frame, then re-verified on the
  NanoPi through `/dev/ttyUSB0`.
- The useful source of truth is the Qt `txdPack()` and `analysisRxdDatas()`
  logic in `D:\电机上位机\CAN-USB-data-conversion\switch\mainwindow.cpp`.
- Keep the SPI MCP2518FD issue separate. Its current failure,
  `osc=0xffffffff`, still points to SPI/power/CS/MISO/oscillator detection, not
  higher-level CAN frame filtering.
