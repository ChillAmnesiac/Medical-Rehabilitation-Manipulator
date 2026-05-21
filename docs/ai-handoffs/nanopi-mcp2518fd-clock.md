# NanoPi MCP2518FD Clock Handoff

AI identity: Codex
Role: NanoPi MCP2518FD CAN bring-up handoff
Date: 2026-05-22

## Current Status

The NanoPi M5 at `192.168.2.66` detects MCP2518FD as `can0` on `spi3.0`.
SocketCAN loopback passed, so the driver and SPI control path are alive.

Real-bus transmission still goes bus-off. The most likely issue is an
oscillator mismatch: the live device tree says 40 MHz, but the local schematic
for the user's actual module shows a 20 MHz crystal.

## Changed Files

- `nanopi-sdk-improved/docs/NANOPI_MCP2518FD_20MHZ_CLOCK_FIX_20260522.md`
- `docs/ai-handoffs/nanopi-mcp2518fd-clock.md`

## Key Finding

`P2` on the module is not a 20/40 MHz jumper. Extracted schematic text places
`P2 Header 2` near `VCC_3V3` and `VCC5V0_BASE`, so it should not be shorted as
a CAN timing fix.

`P3` is near `R15 120R` and is the termination enable header.

The device tree should probably change:

```dts
clock-frequency = <40000000>;
```

to:

```dts
clock-frequency = <20000000>;
```

## Verification Already Done

NanoPi runtime:

- `hostname`: `NanoPi-M5`
- kernel: `6.1.141`
- `can0` parent: `spi3.0`
- driver: `mcp251xfd`
- live DT clock: `40000000`
- SPI max frequency: `10000000`

Loopback command succeeded:

```bash
sudo ip link set can0 type can bitrate 1000000 sample-point 0.8 loopback on berr-reporting on restart-ms 100
cansend can0 321#11223344
```

`candump -L can0` saw the frame.

## Source Patch Update

The `nanopi-sdk` branch source patch has been updated to use 20 MHz:

```text
nanopi-sdk-improved/kernel-patches/0001-arm64-dts-enable-MCP2518FD-CAN-on-NanoPi-M5-SPI3.patch
```

The other computer should pull this branch, apply the updated patch, rebuild
and deploy the DTB, then test real CAN at:

```bash
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 1000000 sample-point 0.8 restart-ms 100 berr-reporting on
sudo ip link set can0 up
cansend can0 321#01
```

Temporary diagnostic before DTB rebuild:

```bash
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 2000000 sample-point 0.8 restart-ms 100 berr-reporting on
sudo ip link set can0 up
cansend can0 321#01
```

If M33 receives at this setting, it confirms the live 40 MHz DT value is wrong
for a 20 MHz crystal.

## Risks

If the physical module actually has a 40 MHz oscillator variant, changing to
20 MHz would make timing wrong in the other direction. The user should confirm
the crystal marking if possible. The provided schematic text says `20MHZ`.
