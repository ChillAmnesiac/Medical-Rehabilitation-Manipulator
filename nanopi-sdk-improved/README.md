# NanoPi M5 SPI3 + MCP2518FD CAN SDK Patch

This directory replaces the older SPI4 overlay experiment. NanoPi M5 on the
current RK3576 kernel should use the main device tree patch in this directory,
not a runtime overlay.

## What This Enables

- Board: FriendlyElec NanoPi M5 / RK3576
- CAN controller: MCP2518FD / MCP2517FD compatible SPI-CAN module
- Linux driver: `mcp251xfd`
- SPI bus: SPI3
- CAN interface expected after successful hardware detection: `can0`

There is also a USB-CAN fallback path documented in:

```text
nanopi-sdk-improved/docs/NANOPI_USB_CAN_SLCAN_20260522.md
nanopi-sdk-improved/docs/ROBSTRIDE_USB_CAN_AT_PROTOCOL_20260522.md
```

The tested CH340 USB-CAN adapter is not yet proven to be standard SLCAN. Use
`diagnose-usbcan.sh` before treating `can_usb0` as a real bus path.

## Kernel Changes

Apply:

```bash
git am nanopi-sdk-improved/kernel-patches/0001-arm64-dts-enable-MCP2518FD-CAN-on-NanoPi-M5-SPI3.patch
```

The patch changes:

- `arch/arm64/boot/dts/rockchip/rk3576-nanopi5-rev01.dts`
- `arch/arm64/configs/nanopi5_linux_defconfig`

It enables:

- `CONFIG_CAN_MCP251XFD=m`
- MCP2518FD on `spi3`
- 20 MHz MCP2518FD oscillator for the currently tested module
- MCP2518FD interrupt on `GPIO4_B3`

## Correct Wiring

Use the SPI3 pins from the NanoPi M5 30-pin header:

| NanoPi M5 Pin | RK3576 Signal | MCP2518FD Module |
| --- | --- | --- |
| 17 or 1 | 3.3V | VCC |
| 20 or 30 | GND | GND |
| 27 | GPIO4_A7 / SPI3_CLK | SCK |
| 28 | GPIO4_A4 / SPI3_MOSI | SI / MOSI |
| 26 | GPIO4_A6 / SPI3_MISO | SO / MISO |
| 29 | GPIO4_A3 / SPI3_CSN0 | CS |
| 24 | GPIO4_B3 | INT |

Do not wire this patch to pins `19/21/23/24` as SPI. Those are the old SPI4
notes and do not match the current kernel patch.

## Build

From the kernel tree:

```bash
export PATH=/home/cal/friendlywrt24-rk3576/.local-toolchain/11.3-aarch64/bin:$PATH
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- nanopi5_linux_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- rockchip/rk3576-nanopi5-rev01.dtb modules
```

If you build with FriendlyWrt/FriendlyElec top-level scripts, apply the patch to
the SDK kernel first, then run the normal SDK build.

## Deploy To Board

Copy the new DTB and modules to the NanoPi using the normal SDK image/update
flow. At minimum the board must boot the patched DTB and have the `mcp251xfd`
module available for the same `uname -r`.

After boot:

```bash
sudo modprobe can
sudo modprobe can_raw
sudo modprobe mcp251xfd
dmesg | grep -iE 'mcp251|spi|can'
ip link show can0
```

If `can0` exists:

```bash
sudo ip link set can0 down 2>/dev/null || true
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
ip -details link show can0
```

For the current USB-CAN fallback, prefer the helper script instead of writing
interface names directly:

```bash
sudo nanopi-sdk-improved/scripts/setup-can.sh 1000000
CAN_INTERFACE=can_usb0 nanopi-sdk-improved/scripts/test-m33-can-heartbeat.sh 01
PORT=/dev/ttyUSB0 nanopi-sdk-improved/scripts/diagnose-usbcan.sh
```

## WiFi Interference Warning

If WiFi works when the MCP2518FD module is disconnected but fails when the
module is connected, debug hardware first:

1. Connect only 3.3V and GND. If WiFi fails, the module is pulling down 3.3V or
   the module power wiring is wrong.
2. Add SCK/MOSI/MISO/CS, but leave INT disconnected. If WiFi fails here, check
   wrong pins, shorts, and IO voltage.
3. Add INT last. If only INT breaks WiFi, move INT to another free GPIO and
   update the DTS.

The MCP2518FD module IO must be 3.3V-compatible. Do not drive NanoPi GPIO pins
with 5V signals.

## Diagnostics

```bash
dmesg | grep -iE 'mcp251|spi|can|rtl8822|wlan|sdio|mmc|voltage|rfkill' | tail -120
cat /sys/firmware/devicetree/base/spi@2ad20000/status
find /sys/bus/spi/devices -maxdepth 2 -type f -name modalias -print -exec cat {} \;
```

Common MCP2518FD error:

```text
Failed to read Oscillator Configuration Register (osc=0xffffffff)
```

This usually means wiring, power, CS, MISO, common GND, or oscillator mismatch.
It is not a NetworkManager/WiFi configuration problem.
