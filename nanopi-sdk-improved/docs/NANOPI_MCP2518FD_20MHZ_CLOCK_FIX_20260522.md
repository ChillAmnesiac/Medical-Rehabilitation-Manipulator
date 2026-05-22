# NanoPi M5 MCP2518FD 20 MHz Clock Fix Note

Date: 2026-05-22
Owner: Codex
Target branch: nanopi-sdk

## Summary

The NanoPi M5 currently detects the MCP2518FD as `can0`, and Linux loopback
works, so SPI, chip select, IRQ, SocketCAN, and the `mcp251xfd` driver are
basically alive.

The remaining failure is on the real CAN bus: sending frames causes repeated
`bus-off` and no ACK from the Infineon M33 / CAN bus. The strongest mismatch
found is the MCP2518FD oscillator frequency in the NanoPi device tree.

The current device tree patch sets:

```dts
mcp2518fd_osc: mcp2518fd-osc {
	compatible = "fixed-clock";
	#clock-cells = <0>;
	clock-frequency = <40000000>;
};
```

But the provided local schematic for this specific SPI-CANFD module shows:

```text
X1 ... 20MHZ 20PF 10PPM SMD3225-4P
```

Therefore this board should very likely use:

```dts
clock-frequency = <20000000>;
```

If Linux thinks the MCP2518FD clock is 40 MHz while the actual crystal is
20 MHz, all calculated CAN bit timing is off by 2x. For example, configuring
`bitrate 1000000` will physically transmit at about 500 kbit/s, so the M33 and
motor CAN bus will not ACK the frame and NanoPi will enter bus-off.

## Important Hardware Notes

The user reported that this module has `P2`, not `JP4`.

From the extracted schematic:

- `P2` is a 2-pin header near `VCC_3V3` and `VCC5V0_BASE`.
- `P2` is not the 20/40 MHz clock selector.
- Do not short `P2` to fix CAN timing.
- NanoPi GPIO/SPI logic is 3.3 V, so keep logic at 3.3 V.
- `P3` is near `R15 120R` and is the 120 ohm termination enable header.
- Shorting `P3` enables the module-side 120 ohm CAN termination.

The transceiver is `ATA6563-GAQW1`. Normal mode requires:

```text
STBY = LOW
TXD  = HIGH when idle
```

The user already measured STBY low, and the bus termination measured about
60 ohm after wiring was corrected, so STBY and termination are not the first
suspects now.

## Runtime Evidence From NanoPi

Board:

```text
hostname: NanoPi-M5
kernel: Linux NanoPi-M5 6.1.141 #1 SMP Tue May 19 16:47:36 CST 2026 aarch64
```

Live device tree / can0:

```text
can0 parentdev: spi3.0
driver: mcp251xfd
compatible: microchip,mcp2518fd
spi-max-frequency: 10000000
clock: 40000000
```

Live DT node:

```dts
spi@2ad20000 {
	status = "okay";

	can@0 {
		compatible = "microchip,mcp2518fd";
		reg = <0x00>;
		spi-max-frequency = <0x989680>;
		clocks = <0x17d>;
		interrupts-extended = <0xee 0x0b 0x08>;
	};
};

mcp2518fd-osc {
	#clock-cells = <0x00>;
	clock-frequency = <0x2625a00>; /* 40000000 */
	compatible = "fixed-clock";
};
```

Loopback test passed:

```bash
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 1000000 sample-point 0.8 loopback on berr-reporting on restart-ms 100
sudo ip link set can0 up
candump -L can0 &
cansend can0 321#11223344
```

Observed result:

```text
(...) can0 321#11223344
(...) can0 321#11223344
```

This means the Linux CAN stack and MCP2518FD SPI control path are working.

## Required Source Change

In the NanoPi kernel source, update the MCP2518FD oscillator fixed-clock node
in:

```text
arch/arm64/boot/dts/rockchip/rk3576-nanopi5-rev01.dts
```

Change:

```dts
clock-frequency = <40000000>;
```

To:

```dts
clock-frequency = <20000000>;
```

The repository patch has been updated so new builds use the 20 MHz value:

```text
nanopi-sdk-improved/kernel-patches/0001-arm64-dts-enable-MCP2518FD-CAN-on-NanoPi-M5-SPI3.patch
```

If the other computer applies patches from this repository after this note, it
should no longer need a separate follow-up patch for the oscillator value.

## Deployment Result On NanoPi

Status on 2026-05-22:

- Target board: `NanoPi-M5`
- Target IP during deployment: `192.168.2.66`
- Kernel: `Linux NanoPi-M5 6.1.141 #1 SMP Tue May 19 16:47:36 CST 2026 aarch64`
- WiFi after reboot: `wlan0` connected to `GDUT-HOME`
- CAN parent device: `spi3.0`
- CAN device: `can0`

The board does not boot the active DTB from `/boot`; `/boot` is empty in this
image. The active DTB is packed inside the Rockchip `resource` partition:

```text
/dev/disk/by-partlabel/resource
```

The old resource image was backed up before writing the new one:

```text
NanoPi: /tmp/resource-before-20mhz.img
Host:   /home/cal/friendlywrt24-rk3576/patches/resource-before-20mhz-192.168.2.66.img
```

The new resource image was generated from the SDK `resource.img` by replacing
`rk3576-nanopi5-rev01.dtb` with the rebuilt 20 MHz DTB, then written to the
resource partition and rebooted.

Post-reboot validation:

```text
ip -details link show can0
...
clock 20000000 ... parentbus spi parentdev spi3.0
```

Driver initialization after reboot:

```text
mcp251xfd spi3.0 can0: MCP2518FD rev0.0 (... o:20.00MHz c:20.00MHz m:10.00MHz rs:8.50MHz ... rf:8.50MHz ...) successfully initialized.
```

Loaded CAN modules after reboot:

```text
mcp251xfd
can_dev
can_raw
can
```

This confirms that the deployed runtime device tree now matches the module's
20 MHz crystal. The remaining verification is a real CAN bus test against the
M33 / motor CAN network at the intended bitrate.

## 2026-05-22 Regression: SPI Reads All Ones

After the USB-CAN side was brought up on another machine, the MCP2518FD path was
checked again on NanoPi `192.168.2.66`.

Current runtime device tree is still correct:

```text
/spi@2ad20000/status                         okay
/spi@2ad20000/can@0/compatible               microchip,mcp2518fd
/spi@2ad20000/can@0/spi-max-frequency        10000000
/mcp2518fd-osc/clock-frequency               20000000
/spi@2ad20000/can@0/interrupts-extended      gpio4 pin 11, level-low
```

Pinmux also matches the intended NanoPi M5 30-pin SPI3 wiring:

```text
pin 131 (gpio4-3 / PIN_29): spi3m2-csn0
pin 132 (gpio4-4 / PIN_28): spi3m2-pins
pin 134 (gpio4-6 / PIN_26): spi3m2-pins
pin 135 (gpio4-7 / PIN_27): spi3m2-pins
```

The kernel probe now fails again:

```text
mcp251xfd spi3.0: Failed to read Oscillator Configuration Register (osc=0xffffffff).
mcp251xfd spi3.0: error -ENODEV: Failed to detect MCP2518FD.
```

To bypass the CAN driver, `spi3.0` was temporarily rebound to `spidev`, and the
MCP2518FD `READ` instruction was used directly:

```text
READ instruction = 0x03
OSC register     = 0xE00
SPI bytes        = 3E 00 <dummy bytes>
```

Raw register reads at all tested SPI clock rates returned all ones:

```text
100 kHz, 250 kHz, 500 kHz, 1 MHz, 2 MHz, 5 MHz, 10 MHz
OSC read: FF FF FF...
CRC read: FF FF FF...
```

That means the failure is below the Linux CAN driver: the NanoPi SPI controller
is clocking the configured pins, but the master is not receiving driven data
from the MCP2518FD. The highest-probability checks are now physical/electrical:

- MCP2518FD module VCC and GND, measured at the module while NanoPi is on.
- Common GND between NanoPi and the MCP2518FD module.
- NanoPi PIN_26 really goes to MCP SO/MISO, not SI/MOSI.
- NanoPi PIN_28 really goes to MCP SI/MOSI.
- NanoPi PIN_29 really goes to MCP CS, and CS toggles low during the raw probe.
- NanoPi PIN_27 really goes to MCP SCK, and SCK toggles during the raw probe.
- No 5 V logic is driving NanoPi SPI pins.
- The module's MCP2518FD chip is populated/powered, not only the CAN
  transceiver side.

The low-level helper committed for future checks is:

```text
nanopi-sdk-improved/scripts/mcp2518fd-spi-probe.py
```

Use it only after temporarily binding `spi3.0` to `spidev`; restore the
`mcp251xfd` driver afterwards.

Suggested follow-up patch content:

```diff
diff --git a/arch/arm64/boot/dts/rockchip/rk3576-nanopi5-rev01.dts b/arch/arm64/boot/dts/rockchip/rk3576-nanopi5-rev01.dts
--- a/arch/arm64/boot/dts/rockchip/rk3576-nanopi5-rev01.dts
+++ b/arch/arm64/boot/dts/rockchip/rk3576-nanopi5-rev01.dts
@@
  mcp2518fd_osc: mcp2518fd-osc {
    compatible = "fixed-clock";
    #clock-cells = <0>;
-		clock-frequency = <40000000>;
+		clock-frequency = <20000000>;
  };
```

## Temporary Confirmation Test

Before rebuilding the device tree, there is a quick sanity test.

If the hardware crystal is really 20 MHz but the live device tree says 40 MHz,
then asking Linux for 2 Mbit/s should produce about 1 Mbit/s on the physical
CAN bus:

```bash
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 2000000 sample-point 0.8 restart-ms 100 berr-reporting on
sudo ip link set can0 up
cansend can0 321#01
```

Expected if the diagnosis is correct:

- M33 may receive the frame at its normal 1 Mbit/s setting.
- Bus-off should stop or reduce dramatically.

If this works, rebuild and deploy the DTB with `clock-frequency = <20000000>;`.
Do not keep using 2 Mbit/s as the final configuration; it is only a diagnostic
workaround for the wrong oscillator value.

## Post-Fix Test Plan

After deploying the corrected DTB:

```bash
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 1000000 sample-point 0.8 restart-ms 100 berr-reporting on
sudo ip link set can0 up
ip -details -statistics link show can0
cansend can0 321#01
```

On the Infineon M33 side:

```text
cmd_can_init_min
cmd_can_poll_once
```

Expected:

- M33 FIFO fill becomes non-zero after NanoPi sends.
- NanoPi does not enter repeated bus-off.
- Later heartbeat / protocol response can be tested on ID `0x322`.

## If It Still Fails After 20 MHz Fix

Check in this order:

1. Scope MCP2518FD `TXCAN` pin while sending.
2. Scope ATA6563 `TXD` pin; it should follow `TXCAN`.
3. Confirm ATA6563 `STBY` is LOW during transmit.
4. Confirm ATA6563 `VCC` is 5 V and `VIO` is 3.3 V.
5. Confirm `CANH/CANL` move differentially during transmit.
6. Keep exactly two 120 ohm terminators on the bus; measured H-L should be
   about 60 ohm when unpowered.
7. If `TXCAN` toggles but CANH/CANL do not, suspect the transceiver/module.
