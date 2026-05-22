# NanoPi M5 USB-CAN SLCAN Deployment Note

Date: 2026-05-22
Owner: Codex
Target branch: nanopi-sdk

## Summary

The current fallback CAN plan uses a USB-CAN adapter instead of the SPI
MCP2518FD module.

The adapter currently connected to the NanoPi enumerates as a CH340 USB serial
device:

```text
1a86:7523 QinHeng Electronics CH340 serial converter
/dev/ttyUSB0
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0
```

This type of adapter may be exposed through the Linux `slcan` driver and the
`slcand` userspace daemon if its firmware implements the LAWICEL/SLCAN command
set. It is not a native `gs_usb` / candleLight style SocketCAN USB device.

## 2026-05-22 Follow-up: SLCAN Not Verified

Further testing from the Windows bring-up machine found that the current CH340
adapter does not respond to standard LAWICEL/SLCAN commands on `/dev/ttyUSB0`.

Test method:

```bash
sudo systemctl stop usbcan-slcan.service
sudo chmod 666 /dev/ttyUSB0
for rate in 2000000 1000000 921600 460800 230400 115200 57600 38400 9600; do
  stty -F /dev/ttyUSB0 $rate raw -echo -icanon min 0 time 5
  # send V, N, F, C, S8, O, t321101 with CR terminators
done
```

Observed result:

```text
0 bytes returned at every tested UART speed.
```

`candump -x -L can_usb0` shows NanoPi-originated frames with the `T` flag:

```text
can_usb0 321#AB T
```

That is a local transmit echo from SocketCAN, not proof that the adapter put a
frame on the CAN bus or received anything from another node. Interface counters
also stayed at:

```text
RX packets 0
```

The M33 side was independently verified over KitProg3 serial:

```text
cmd_can_init_min
cmd_can_send_probe 0x01
txbto=0x00000001

cmd_can_poll_once
fifo0 fill=0
```

M33 CAN filters accept both non-matching standard and extended frames into
FIFO0, so `0x321` is not being rejected by M33 software filtering.

Current conclusion: the live `slcand`/`can_usb0` path creates a SocketCAN
interface, but this alone is not sufficient evidence that the CH340 USB-CAN
adapter firmware is SLCAN-compatible. Treat the adapter protocol as unverified
until either raw serial commands return valid LAWICEL/SLCAN responses, a vendor
protocol/driver for this exact adapter is used, or the adapter is replaced with
a known `gs_usb`/candleLight/CANable-compatible device.

## Runtime Status

Target board:

```text
hostname: NanoPi-M5
ip: 192.168.2.66
kernel: Linux 6.1.141
```

The board already had `slcand`, `slcan_attach`, `candump`, and `cansend`, but
the installed `slcan.ko` module did not match the running kernel and failed
with:

```text
modprobe: ERROR: could not insert 'slcan': Exec format error
slcan: disagrees about version of symbol module_layout
```

The matching kernel modules were copied from the SDK build output to the board:

```text
/lib/modules/6.1.141/kernel/drivers/net/can/slcan/slcan.ko
/lib/modules/6.1.141/kernel/drivers/net/can/usb/gs_usb.ko
/lib/modules/6.1.141/kernel/drivers/net/can/usb/peak_usb/peak_usb.ko
/lib/modules/6.1.141/kernel/drivers/net/can/usb/kvaser_usb/kvaser_usb.ko
```

After `depmod -a`, `modprobe slcan` succeeds.

## Service Status

The NanoPi has this systemd service file:

```text
/etc/systemd/system/usbcan-slcan.service
```

It can create a SocketCAN interface named:

```text
can_usb0
```

with:

```text
CAN bitrate: 1000000 bit/s  # slcand -s8
UART speed:  2000000 baud   # slcand -S 2000000
```

Service commands:

```bash
sudo systemctl status usbcan-slcan.service
sudo systemctl restart usbcan-slcan.service
sudo systemctl stop usbcan-slcan.service
```

After the 2026-05-22 diagnostics, this service was disabled on the live NanoPi
because the CH340 adapter is not verified as a real SLCAN adapter:

```bash
sudo systemctl disable --now usbcan-slcan.service
```

Expected current service state:

```text
disabled
inactive
```

Keep it disabled until one of these is true:

- the CH340 adapter protocol is positively identified and tested,
- raw serial diagnostics show real receive frames,
- or the adapter is replaced with a known SocketCAN-compatible USB-CAN device.

Validation:

```bash
ip -details -statistics link show can_usb0
```

Expected current state:

```text
can_usb0: <NOARP,UP,LOWER_UP>
can state ERROR-ACTIVE
```

## Manual Bring-Up Command

If the service is disabled or the adapter path changes, bring it up manually:

```bash
sudo modprobe slcan
sudo pkill -x slcand || true
sudo ip link delete can_usb0 2>/dev/null || true
sudo slcand -o -c -f -s8 -S 2000000 /dev/ttyUSB0 can_usb0
sleep 1
sudo ip link set can_usb0 up
ip -details -statistics link show can_usb0
```

SLCAN speed index:

```text
-s6 = 500 kbit/s
-s7 = 800 kbit/s
-s8 = 1000 kbit/s
```

## Test Commands

Listen only:

```bash
candump -tz can_usb0
```

Send a minimal test frame after the bus wiring and target device are confirmed:

```bash
cansend can_usb0 321#01
```

For the medical manipulator platform, detect CAN interfaces through SocketCAN
(`ip -details link show type can`) but do not blindly trust `can_usb0` on this
CH340 adapter. Mark CH340/SLCAN adapters as `unverified` until
`diagnose-usbcan.sh` proves real RX/TX, or until a known native SocketCAN
adapter is installed. The platform should not assume that CAN devices are
always named `can0`.

## Diagnostic Script Added

The repository now includes:

```text
nanopi-sdk-improved/scripts/diagnose-usbcan.sh
nanopi-sdk-improved/scripts/test-m33-can-heartbeat.sh
```

Use the diagnostic script before accepting a CH340 adapter as usable:

```bash
PORT=/dev/ttyUSB0 nanopi-sdk-improved/scripts/diagnose-usbcan.sh
```

It checks:

- USB descriptor and stable serial path.
- LAWICEL/SLCAN responses at common UART speeds.
- RobStride AT packet encode/decode.
- RobStride AT transport probe at common UART speeds.

Live NanoPi spot check on 2026-05-22:

```text
baud 2000000: no LAWICEL/SLCAN reply
baud 115200: no LAWICEL/SLCAN reply
TX raw=41 54 00 07 E8 0C 01 00 0D 0A ...
no RX packet returned
```

This confirms the current CH340 adapter is still vendor/firmware-unknown. The
`can_usb0` interface can be useful for service wiring tests, but it must not be
treated as proof of real CAN bus transmission until the adapter protocol is
identified or the hardware is replaced with a known SocketCAN-compatible
adapter.

Live NanoPi containment action:

```text
usbcan-slcan.service disabled
usbcan-slcan.service inactive
no can_usb0 interface present after stop
```

## Notes For The Next AI / Developer

- CH340 USB-CAN adapters are only SLCAN devices when their firmware implements
  the LAWICEL/SLCAN command set. A CH340 USB VID/PID only proves "USB serial",
  not CAN protocol compatibility.
- Native candleLight / CANable-style adapters usually bind to `gs_usb` and
  appear directly as `can0` without `slcand`.
- This NanoPi image has a mixed `/lib/modules/6.1.141` tree. If another CAN or
  USB module reports `Exec format error`, copy the matching module from the SDK
  build output and run `sudo depmod -a`.
- The previous SPI MCP2518FD path still exists in source, but the USB-CAN path
  should be treated as the simpler runtime integration path for now.
