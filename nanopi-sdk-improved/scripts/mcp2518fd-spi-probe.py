#!/usr/bin/env python3
"""Low-level MCP2518FD SPI register probe for NanoPi bring-up.

This bypasses the Linux mcp251xfd CAN driver and talks to /dev/spidevX.Y
directly. It is useful when the kernel reports:

    Failed to read Oscillator Configuration Register (osc=0xffffffff)

Expected use on NanoPi:

    sudo modprobe -r mcp251xfd
    sudo modprobe spidev
    echo spidev | sudo tee /sys/bus/spi/devices/spi3.0/driver_override
    echo spi3.0 | sudo tee /sys/bus/spi/drivers/spidev/bind
    sudo python3 mcp2518fd-spi-probe.py --device /dev/spidev3.0

Restore afterwards:

    echo spi3.0 | sudo tee /sys/bus/spi/drivers/spidev/unbind
    echo '' | sudo tee /sys/bus/spi/devices/spi3.0/driver_override
    sudo modprobe mcp251xfd
"""

from __future__ import annotations

import argparse
import ctypes
import fcntl
import os


SPI_IOC_MESSAGE_1 = 0x40206B00
MCP251XFD_INSTRUCTION_READ = 0x03
MCP251XFD_REG_OSC = 0xE00
MCP251XFD_REG_CRC = 0xE08


class SpiIocTransfer(ctypes.Structure):
    _fields_ = [
        ("tx_buf", ctypes.c_uint64),
        ("rx_buf", ctypes.c_uint64),
        ("len", ctypes.c_uint32),
        ("speed_hz", ctypes.c_uint32),
        ("delay_usecs", ctypes.c_uint16),
        ("bits_per_word", ctypes.c_uint8),
        ("cs_change", ctypes.c_uint8),
        ("tx_nbits", ctypes.c_uint8),
        ("rx_nbits", ctypes.c_uint8),
        ("word_delay_usecs", ctypes.c_uint8),
        ("pad", ctypes.c_uint8),
    ]


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def read_command(address: int, data_len: int) -> bytes:
    return bytes(
        [
            (MCP251XFD_INSTRUCTION_READ << 4) | ((address >> 8) & 0x0F),
            address & 0xFF,
            *([0x00] * data_len),
        ]
    )


def spi_transfer(device: str, speed_hz: int, tx: bytes) -> bytes:
    fd = os.open(device, os.O_RDWR)
    try:
        tx_buf = (ctypes.c_ubyte * len(tx))(*tx)
        rx_buf = (ctypes.c_ubyte * len(tx))()
        transfer = SpiIocTransfer(
            ctypes.addressof(tx_buf),
            ctypes.addressof(rx_buf),
            len(tx),
            speed_hz,
            0,
            8,
            0,
            0,
            0,
            0,
            0,
        )
        fcntl.ioctl(fd, SPI_IOC_MESSAGE_1, transfer)
        return bytes(rx_buf)
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read MCP2518FD registers through spidev")
    parser.add_argument("--device", default="/dev/spidev3.0")
    parser.add_argument(
        "--speeds",
        nargs="+",
        type=int,
        default=[100000, 250000, 500000, 1000000, 2000000, 5000000, 10000000],
    )
    args = parser.parse_args()

    commands = {
        "osc_byte": read_command(MCP251XFD_REG_OSC, 1),
        "osc_u32": read_command(MCP251XFD_REG_OSC, 4),
        "crc_u32": read_command(MCP251XFD_REG_CRC, 4),
    }

    for speed in args.speeds:
        print(f"=== {speed} Hz ===")
        for name, tx in commands.items():
            rx = spi_transfer(args.device, speed, tx)
            print(f"{name}: tx={hex_bytes(tx)} rx={hex_bytes(rx)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
