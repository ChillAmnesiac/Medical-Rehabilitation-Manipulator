# NanoPi M5 MCP2518FD CAN Bring-up Handoff

Date: 2026-05-21
Board: NanoPi M5
OS: Ubuntu 24.04.4 LTS
Kernel: 6.1.141
CAN module: MCP2518FD on SPI3

## Current Status

The MCP2518FD hardware wiring has been fixed and the Linux driver now detects
the chip successfully.

Observed on the NanoPi:

```text
pi@192.168.2.66
hostname: NanoPi-M5
uname -r: 6.1.141
```

Successful driver probe:

```text
mcp251xfd spi3.0 can0: MCP2518FD rev0.0 (-RX_INT -PLL -MAB_NO_WARN +CRC_REG +CRC_RX +CRC_TX +ECC -HD o:40.00MHz c:40.00MHz m:10.00MHz rs:10.00MHz es:0.00MHz rf:10.00MHz ef:0.00MHz) successfully initialized.
```

`can0` is present and can be brought up:

```text
6: can0: <NOARP,UP,LOWER_UP,ECHO> mtu 16 qdisc pfifo_fast state UP mode DEFAULT group default qlen 10
    can <BERR-REPORTING> state ERROR-ACTIVE (berr-counter tx 0 rx 0) restart-ms 100
      bitrate 1000000 sample-point 0.750
      clock 40000000
```

This means the SPI3 wiring, MCP2518FD power, chip select, MISO/MOSI/SCK, and
device-tree binding are now basically correct.

## Remaining Blocker

`candump` and `cansend` currently fail because the SocketCAN raw protocol module
does not load:

```text
sudo modprobe can_raw
modprobe: ERROR: could not insert 'can_raw': Exec format error
```

Kernel log:

```text
can: disagrees about version of symbol module_layout
```

`candump can0` then reports:

```text
socket: Address family not supported by protocol
```

This is not a CAN wiring or bitrate problem. It means the installed CAN protocol
module files do not match the running kernel build. At minimum, these modules
must come from the same exact kernel build as the booted `6.1.141` image:

```text
/lib/modules/6.1.141/kernel/net/can/can.ko
/lib/modules/6.1.141/kernel/net/can/can-raw.ko
/lib/modules/6.1.141/kernel/drivers/net/can/dev/can-dev.ko
/lib/modules/6.1.141/kernel/drivers/net/can/spi/mcp251xfd/mcp251xfd.ko
```

The board currently has a working `mcp251xfd.ko`, but `can_raw` is version
incompatible. Reinstall the full matching module tree, not just one module, to
avoid mixed-symbol problems.

## Kernel Patch In This Branch

The current `nanopi-sdk` branch contains the intended kernel patch:

```text
nanopi-sdk-improved/kernel-patches/0001-arm64-dts-enable-MCP2518FD-CAN-on-NanoPi-M5-SPI3.patch
```

It changes:

```text
arch/arm64/boot/dts/rockchip/rk3576-nanopi5-rev01.dts
arch/arm64/configs/nanopi5_linux_defconfig
```

Important DTS choices:

```text
SPI bus: &spi3
Runtime node: /spi@2ad20000/can@0
Compatible: microchip,mcp2518fd
Clock: 40 MHz
SPI max frequency: 10 MHz
Interrupt: GPIO4_B3, IRQ_TYPE_LEVEL_LOW
```

Important defconfig option:

```text
CONFIG_CAN_MCP251XFD=m
```

## Correct Wiring

Use the SPI3 pins from the NanoPi M5 30-pin header. Do not use the older SPI4
notes based on pins 19/21/23/24.

| NanoPi M5 Pin | RK3576 Signal | MCP2518FD Module |
| --- | --- | --- |
| 17 or 1 | 3.3V | VCC / VIO |
| 20 or 30 | GND | GND |
| 27 | GPIO4_A7 / SPI3_CLK | SCK |
| 28 | GPIO4_A4 / SPI3_MOSI | SI / MOSI |
| 26 | GPIO4_A6 / SPI3_MISO | SO / MISO |
| 29 | GPIO4_A3 / SPI3_CSN0 | CS |
| 24 | GPIO4_B3 | INT |

If the module has a `RESET` / `RST` pin, keep it pulled high. The module IO must
be 3.3 V compatible.

## Rebuild And Deploy On The Other Computer

From the FriendlyElec/FriendlyWrt kernel tree, apply the patch:

```bash
git am /path/to/Medical-Rehabilitation-Manipulator/nanopi-sdk-improved/kernel-patches/0001-arm64-dts-enable-MCP2518FD-CAN-on-NanoPi-M5-SPI3.patch
```

Build the matching DTB and modules using the same kernel tree and config:

```bash
export PATH=/home/cal/friendlywrt24-rk3576/.local-toolchain/11.3-aarch64/bin:$PATH
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- nanopi5_linux_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- rockchip/rk3576-nanopi5-rev01.dtb modules
```

Deploy the new DTB and the full matching module tree to the NanoPi. The safest
route is to use the normal SDK image/update flow. If copying manually, make sure
the booted kernel image, DTB, and `/lib/modules/6.1.141/` all come from the same
build.

After copying modules:

```bash
sudo depmod -a
sudo reboot
```

## Validation Commands On NanoPi

After reboot:

```bash
uname -r
sudo modprobe can
sudo modprobe can_raw
sudo modprobe mcp251xfd
dmesg | grep -iE 'mcp251|spi|can|raw|module_layout' | tail -120
ip -details -statistics link show can0
```

Expected:

```text
mcp251xfd spi3.0 can0: MCP2518FD ... successfully initialized.
can_raw loads without Exec format error.
```

Bring CAN up at 1 Mbps:

```bash
sudo ip link set can0 down 2>/dev/null || true
sudo ip link set can0 type can bitrate 1000000 restart-ms 100 berr-reporting on
sudo ip link set can0 up
ip -details -statistics link show can0
```

Listen first; do not send motor commands until the bus is understood:

```bash
candump -tz can0
```

## System Integration Notes

The physical CAN bus contains:

- NanoPi M5 with MCP2518FD
- Infineon PSoC Edge M33
- STM32C8T6 sensor node
- 7 motor controllers

All nodes must use the same CAN bitrate. The current NanoPi test used
`1000000` bps because the motor bus is likely 1 Mbps. If C8T6 or Infineon is
configured for 500 kbps, it must be changed before bus-level communication will
work reliably.

Known project CAN IDs from the current local code/docs:

```text
C8T6 sensor reports:
0x300 EMG
0x301 heart rate / SpO2
0x302 IMU accel
0x303 IMU gyro
0x304 sensor status
0x310 sensor command

M33 ROS command bridge:
0x320 ROS command
```

There are older M33 definitions that still mention `0x200` series sensor IDs.
Those should be cleaned up later so C8T6, NanoPi, and Infineon all agree on one
CAN protocol table.

## Quick Diagnosis Matrix

If `can0` does not exist:

```bash
dmesg | grep -iE 'mcp251|spi|can'
```

- `Failed to read Oscillator Configuration Register (osc=0xffffffff)` usually
  means MISO floating, bad CS, missing power, missing ground, reset held low, or
  the wrong SPI pins.
- `Failed to read Oscillator Configuration Register (osc=0x00000000)` often
  means the SPI lines are pulled low, the chip is not responding, or the wrong
  SPI bus is selected.

If `can0` exists but `candump` fails with:

```text
socket: Address family not supported by protocol
```

check:

```bash
sudo modprobe can_raw
dmesg | grep -i module_layout
```

If `module_layout` disagrees, reinstall a matching kernel/module set.

