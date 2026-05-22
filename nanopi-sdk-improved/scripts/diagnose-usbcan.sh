#!/bin/bash
# Diagnose whether a CH340 USB-CAN adapter is SLCAN, RobStride AT, or unknown.

set -euo pipefail

PORT="${PORT:-/dev/ttyUSB0}"
AT_HELPER="${AT_HELPER:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/robstride_usbcan_at.py}"
BAUDS="${BAUDS:-2000000 1000000 921600 460800 230400 115200 57600 38400 9600}"

if [ ! -e "$PORT" ]; then
    echo "error: serial port not found: $PORT"
    echo "hint: lsusb; ls -l /dev/ttyUSB* /dev/serial/by-id/*"
    exit 1
fi

echo "=== USB-CAN descriptor ==="
lsusb | grep -iE '1a86|can|ch340|usb serial' || true
udevadm info -q property -n "$PORT" 2>/dev/null | grep -E 'ID_VENDOR_ID|ID_MODEL_ID|ID_SERIAL|ID_PATH|DEVLINKS' || true
echo ""

echo "=== Stop slcand users ==="
sudo systemctl stop usbcan-slcan.service 2>/dev/null || true
sudo pkill -x slcand 2>/dev/null || true
sudo chmod 666 "$PORT"
echo ""

echo "=== Test LAWICEL/SLCAN responses ==="
python3 - "$PORT" $BAUDS <<'PY'
import os
import select
import subprocess
import sys
import time

port = sys.argv[1]
bauds = [int(x) for x in sys.argv[2:]]
commands = [b"V\r", b"N\r", b"F\r", b"C\r", b"S8\r", b"O\r", b"t321101\r"]

for baud in bauds:
    subprocess.run(["stty", "-F", port, str(baud), "raw", "-echo", "-icanon", "min", "0", "time", "5"], check=True)
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        os.read(fd, 4096)
    except BlockingIOError:
        pass
    replies = []
    try:
        for command in commands:
            os.write(fd, command)
            end = time.monotonic() + 0.25
            data = bytearray()
            while time.monotonic() < end:
                readable, _, _ = select.select([fd], [], [], 0.05)
                if readable:
                    try:
                        data.extend(os.read(fd, 4096))
                    except BlockingIOError:
                        pass
            if data:
                replies.append((command, bytes(data)))
    finally:
        os.close(fd)
    if replies:
        print(f"baud {baud}: SLCAN-like replies found")
        for command, data in replies:
            print(f"  {command!r} -> {data.hex(' ').upper()}")
    else:
        print(f"baud {baud}: no LAWICEL/SLCAN reply")
PY
echo ""

echo "=== Test RobStride AT helper encode/decode ==="
python3 "$AT_HELPER" encode --id 0x0000fd01 --data 00
python3 "$AT_HELPER" decode "41 54 00 07 E8 0C 01 00 0D 0A"
echo ""

echo "=== Probe RobStride AT transport ==="
for baud in $BAUDS; do
    echo "--- baud $baud ---"
    python3 "$AT_HELPER" send-ext --port "$PORT" --baud "$baud" --id 0x0000fd01 --data 00 --wait 0.5 || true
done
echo ""

echo "Diagnosis complete."
echo "If all SLCAN commands and AT probes return no RX, treat this adapter as vendor/firmware-unknown."
