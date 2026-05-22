#!/usr/bin/env python3
"""RobStride/WitMotion-style CH340 USB-CAN AT protocol helper.

This adapter protocol is a binary serial protocol:

    41 54 <encoded 29-bit CAN id, big endian> <dlc> <0..8 data bytes> 0d 0a

It is not LAWICEL/SLCAN. Use this script with /dev/ttyUSB0 directly after
stopping any slcand service that may have opened the same serial port.
"""

from __future__ import annotations

import argparse
import os
import select
import sys
import time
from dataclasses import dataclass


DEFAULT_PORT = "/dev/ttyUSB0"
DEFAULT_BAUD = 921_600

@dataclass(frozen=True)
class AtFrame:
    can_id: int
    data: bytes

    @property
    def id_field(self) -> int:
        return (self.can_id >> 24) & 0xFF

    @property
    def data_field(self) -> int:
        return (self.can_id >> 8) & 0xFFFF

    @property
    def mode_field(self) -> int:
        return (self.can_id >> 3) & 0x1F

    @property
    def res_field(self) -> int:
        return self.can_id & 0x07


def parse_int(value: str) -> int:
    return int(value, 0)


def parse_hex_bytes(value: str) -> bytes:
    text = value.replace(" ", "").replace(":", "").replace("-", "")
    if len(text) % 2:
        text = "0" + text
    if not text:
        return b""
    return bytes.fromhex(text)


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def build_can_id(id_field: int, data_field: int, mode_field: int, res_field: int) -> int:
    if not 0 <= id_field <= 0xFF:
        raise ValueError("id field must fit in 8 bits")
    if not 0 <= data_field <= 0xFFFF:
        raise ValueError("data field must fit in 16 bits")
    if not 0 <= mode_field <= 0x1F:
        raise ValueError("mode field must fit in 5 bits")
    if not 0 <= res_field <= 0x07:
        raise ValueError("res field must fit in 3 bits")
    return (id_field << 24) | (data_field << 8) | (mode_field << 3) | res_field


def encode_frame(can_id: int, data: bytes) -> bytes:
    if not 0 <= can_id <= 0x1FFFFFFF:
        raise ValueError("extended CAN id must fit in 29 bits")
    if len(data) > 8:
        raise ValueError("CAN data length must be 0..8 bytes")
    if len(data) < 1:
        data = b"\x00"

    adapter_addr = ((can_id & 0x1FFFFFFF) << 3) | 0x04
    return b"AT" + adapter_addr.to_bytes(4, "big") + bytes([len(data)]) + data + b"\r\n"


def decode_frame(packet: bytes) -> AtFrame:
    if len(packet) < 9:
        raise ValueError("AT packet is too short")
    if not packet.startswith(b"AT"):
        raise ValueError("AT packet must start with 41 54")
    dlc = packet[6]
    expected_len = 9 + dlc
    if len(packet) != expected_len:
        raise ValueError(f"AT packet length {len(packet)} != expected {expected_len}")
    if packet[-2:] != b"\r\n":
        raise ValueError("AT packet must end with 0d 0a")
    if dlc > 8:
        raise ValueError("AT packet DLC must be 0..8")

    adapter_addr = int.from_bytes(packet[2:6], "big")
    can_id = ((adapter_addr & ~0x04) >> 3) & 0x1FFFFFFF
    return AtFrame(can_id=can_id, data=packet[7 : 7 + dlc])


def extract_frames(buffer: bytearray) -> list[bytes]:
    frames: list[bytes] = []
    while True:
        start = buffer.find(b"AT")
        if start < 0:
            del buffer[:]
            return frames
        if start:
            del buffer[:start]
        if len(buffer) < 7:
            return frames
        dlc = buffer[6]
        if dlc > 8:
            del buffer[0]
            continue
        packet_len = 9 + dlc
        if len(buffer) < packet_len:
            return frames
        packet = bytes(buffer[:packet_len])
        del buffer[:packet_len]
        if packet[-2:] == b"\r\n":
            frames.append(packet)


def open_serial(path: str, baud: int) -> int:
    try:
        import termios
        import tty
    except ImportError as exc:
        raise ValueError("raw serial mode requires Linux/Unix termios support") from exc

    baud_constants = {
        9600: termios.B9600,
        38400: termios.B38400,
        57600: termios.B57600,
        115200: termios.B115200,
        230400: getattr(termios, "B230400", None),
        460800: getattr(termios, "B460800", None),
        921600: getattr(termios, "B921600", None),
        1000000: getattr(termios, "B1000000", None),
        2000000: getattr(termios, "B2000000", None),
    }
    baud_const = baud_constants.get(baud)
    if baud_const is None:
        raise ValueError(f"baud {baud} is not supported by this Python/termios build")

    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    attrs[0] = 0
    attrs[1] = 0
    attrs[2] = termios.CLOCAL | termios.CREAD | termios.CS8
    attrs[3] = 0
    attrs[4] = baud_const
    attrs[5] = baud_const
    attrs[6][termios.VMIN] = 0
    attrs[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    tty.setraw(fd)
    termios.tcflush(fd, termios.TCIOFLUSH)
    return fd


def read_frames(fd: int, timeout: float) -> list[bytes]:
    end = time.monotonic() + timeout
    buffer = bytearray()
    packets: list[bytes] = []
    while time.monotonic() < end:
        wait = max(0.0, min(0.1, end - time.monotonic()))
        readable, _, _ = select.select([fd], [], [], wait)
        if not readable:
            continue
        try:
            chunk = os.read(fd, 4096)
        except BlockingIOError:
            continue
        if not chunk:
            continue
        buffer.extend(chunk)
        packets.extend(extract_frames(buffer))
    return packets


def print_decoded(prefix: str, packet: bytes) -> None:
    frame = decode_frame(packet)
    print(
        f"{prefix} raw={hex_bytes(packet)} can_id=0x{frame.can_id:08X} "
        f"id=0x{frame.id_field:02X} data=0x{frame.data_field:04X} "
        f"mode=0x{frame.mode_field:02X} res=0x{frame.res_field:X} "
        f"dlc={len(frame.data)} payload={hex_bytes(frame.data)}"
    )


def cmd_encode(args: argparse.Namespace) -> int:
    can_id = resolve_can_id(args)
    data = parse_hex_bytes(args.data)
    packet = encode_frame(can_id, data)
    print(hex_bytes(packet))
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    packet = parse_hex_bytes(args.packet)
    print_decoded("RX", packet)
    return 0


def resolve_can_id(args: argparse.Namespace) -> int:
    if args.can_id is not None:
        return args.can_id
    return build_can_id(args.id_field, args.data_field, args.mode_field, args.res_field)


def cmd_send(args: argparse.Namespace) -> int:
    can_id = resolve_can_id(args)
    data = parse_hex_bytes(args.data)
    packet = encode_frame(can_id, data)
    fd = open_serial(args.port, args.baud)
    try:
        os.write(fd, packet)
        print_decoded("TX", packet)
        for reply in read_frames(fd, args.wait):
            print_decoded("RX", reply)
    finally:
        os.close(fd)
    return 0


def cmd_probe_motor(args: argparse.Namespace) -> int:
    can_id = build_can_id(0x00, args.master_id, 0x00, args.motor_id)
    args.can_id = can_id
    args.data = "00"
    return cmd_send(args)


def cmd_monitor(args: argparse.Namespace) -> int:
    fd = open_serial(args.port, args.baud)
    buffer = bytearray()
    try:
        while True:
            readable, _, _ = select.select([fd], [], [], 0.5)
            if not readable:
                continue
            chunk = os.read(fd, 4096)
            if not chunk:
                continue
            buffer.extend(chunk)
            for packet in extract_frames(buffer):
                print_decoded("RX", packet)
    except KeyboardInterrupt:
        return 0
    finally:
        os.close(fd)


def add_frame_args(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--id", dest="can_id", type=parse_int, help="raw 29-bit extended CAN id")
    source.add_argument("--fields", action="store_true", help="use split RobStride id/data/mode/res fields")
    parser.add_argument("--id-field", type=parse_int, default=0, help="8-bit id field when --fields is used")
    parser.add_argument("--data-field", type=parse_int, default=0, help="16-bit data field when --fields is used")
    parser.add_argument("--mode-field", type=parse_int, default=0, help="5-bit mode field when --fields is used")
    parser.add_argument("--res-field", type=parse_int, default=0, help="3-bit res field when --fields is used")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RobStride CH340 USB-CAN AT protocol helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode = subparsers.add_parser("encode", help="print the AT serial packet for a CAN frame")
    add_frame_args(encode)
    encode.add_argument("--data", default="00", help="CAN data bytes as hex")
    encode.set_defaults(func=cmd_encode)

    decode = subparsers.add_parser("decode", help="decode one AT packet")
    decode.add_argument("packet", help="AT packet bytes as hex")
    decode.set_defaults(func=cmd_decode)

    send = subparsers.add_parser("send-ext", help="send one extended CAN frame through the serial adapter")
    add_frame_args(send)
    send.add_argument("--data", default="00", help="CAN data bytes as hex")
    send.add_argument("--port", default=DEFAULT_PORT)
    send.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    send.add_argument("--wait", type=float, default=0.5, help="seconds to wait for replies")
    send.set_defaults(func=cmd_send)

    probe = subparsers.add_parser("probe-motor", help="send the known RobStride Get_ID probe frame")
    probe.add_argument("--motor-id", type=parse_int, default=0x01, help="motor id stored in the low res field, 0..7")
    probe.add_argument("--master-id", type=parse_int, default=0xFD, help="master id stored in the 16-bit data field")
    probe.add_argument("--port", default=DEFAULT_PORT)
    probe.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    probe.add_argument("--wait", type=float, default=0.5, help="seconds to wait for replies")
    probe.set_defaults(func=cmd_probe_motor)

    monitor = subparsers.add_parser("monitor", help="listen for AT frames from the serial adapter")
    monitor.add_argument("--port", default=DEFAULT_PORT)
    monitor.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    monitor.set_defaults(func=cmd_monitor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
