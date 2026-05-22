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

This type of adapter is normally exposed through the Linux `slcan` driver and
the `slcand` userspace daemon. It is not a native `gs_usb` / candleLight style
SocketCAN USB device.

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

## Deployed Service

The NanoPi now has this systemd service:

```text
/etc/systemd/system/usbcan-slcan.service
```

It creates a SocketCAN interface named:

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
sudo pkill -f "slcand.*can_usb0" || true
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

For the medical manipulator platform, prefer detecting CAN interfaces through
SocketCAN (`ip -details link show type can`) and treat `can_usb0` the same as
any other CAN interface. The platform should not assume that CAN devices are
always named `can0`.

## Notes For The Next AI / Developer

- CH340 USB-CAN adapters are SLCAN devices unless their firmware implements a
  native SocketCAN protocol.
- Native candleLight / CANable-style adapters usually bind to `gs_usb` and
  appear directly as `can0` without `slcand`.
- This NanoPi image has a mixed `/lib/modules/6.1.141` tree. If another CAN or
  USB module reports `Exec format error`, copy the matching module from the SDK
  build output and run `sudo depmod -a`.
- The previous SPI MCP2518FD path still exists in source, but the USB-CAN path
  should be treated as the simpler runtime integration path for now.
