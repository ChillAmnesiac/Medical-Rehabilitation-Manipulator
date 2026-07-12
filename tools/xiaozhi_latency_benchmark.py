#!/usr/bin/env python3
import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import re
import time
from typing import Any


LATENCY_RE = re.compile(
    r"xz_latency seq=(?P<seq>\d+) turn=(?P<turn>\d+) flags=(?P<flags>0x[0-9a-fA-F]+) "
    r"wake_listen=(?P<wake_listen>\d+) eou=(?P<eou>\d+) stop_stt=(?P<stop_stt>\d+) "
    r"stt_llm=(?P<stt_llm>\d+) llm_tts=(?P<llm_tts>\d+) tts_packet=(?P<tts_packet>\d+) "
    r"packet_write=(?P<packet_write>\d+) speech_audio=(?P<speech_audio>\d+) "
    r"wake_audio=(?P<wake_audio>\d+) age_ticks=(?P<age_ticks>\d+)"
)
FIELDS = [
    "seq", "turn", "flags", "wake_listen", "eou", "stop_stt", "stt_llm",
    "llm_tts", "tts_packet", "packet_write", "stop_audio", "speech_audio", "wake_audio", "age_ticks",
]
STAGE_FIELDS = ("eou", "stop_stt", "stt_llm", "llm_tts", "tts_packet", "packet_write")


def parse_latency_line(line: str) -> dict[str, int] | None:
    match = LATENCY_RE.search(line)
    if not match:
        return None
    values = match.groupdict()
    row = {
        key: int(value, 16) if key == "flags" else int(value)
        for key, value in values.items()
    }
    row["stop_audio"] = sum(row[field] for field in STAGE_FIELDS if field != "eou")
    return row


def percentile(values: list[int], percent: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) * percent + 99) // 100) - 1))
    return ordered[index]


def summarize(rows: list[dict[str, int]], failures: int = 0) -> dict[str, Any]:
    attempts = len(rows) + failures
    summary: dict[str, Any] = {
        "count": len(rows),
        "failures": failures,
        "failure_rate_pct": round((failures * 100.0 / attempts), 2) if attempts else 0.0,
    }
    for field in (*STAGE_FIELDS, "stop_audio", "speech_audio", "wake_audio"):
        values = [row[field] for row in rows]
        summary[f"{field}_ms"] = {
            "p50": percentile(values, 50),
            "p95": percentile(values, 95),
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
        }
    total_latency = sum(row["speech_audio"] for row in rows)
    summary["stage_share_pct"] = {
        field: round(sum(row[field] for row in rows) * 100.0 / total_latency, 2) if total_latency else 0.0
        for field in STAGE_FIELDS
    }
    return summary


def wait_for_output(port: Any, pattern: str, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    matcher = re.compile(pattern)
    buffer = ""
    while time.monotonic() < deadline:
        waiting = port.in_waiting
        if waiting:
            buffer += port.read(waiting).decode("utf-8", errors="replace")
            if matcher.search(buffer):
                return True
            buffer = buffer[-4096:]
        time.sleep(0.05)
    return False


def run_probe_turn(port: Any, probe_ms: int, timeout_s: float) -> bool:
    steps = (
        ("m55qa_probe_pcm_on", r"probe_pcm_on ret=0 ack=0"),
        ("m55qa_capture_on", r"capture_on ret=0 ack=0"),
        (f"m33qa_xz_probe {probe_ms}", r"xiaozhi probe done .*tx_pending=0"),
        ("m55qa_capture_off", r"capture_off ret=0 ack=0"),
    )
    ok = True
    capture_started = False
    try:
        for command, pattern in steps:
            port.write(f"{command}\r\n".encode("ascii"))
            if not wait_for_output(port, pattern, timeout_s):
                print(f"probe step failed: {command}")
                ok = False
                break
            if command == "m55qa_capture_on":
                capture_started = True
            elif command == "m55qa_capture_off":
                capture_started = False
    finally:
        if capture_started:
            port.write(b"m55qa_capture_off\r\n")
            if not wait_for_output(port, r"capture_off ret=0 ack=0", timeout_s):
                print("probe cleanup failed: m55qa_capture_off")
                ok = False
        port.write(b"m55qa_probe_pcm_off\r\n")
        if not wait_for_output(port, r"probe_pcm_off ret=0 ack=0", timeout_s):
            print("probe cleanup failed: m55qa_probe_pcm_off")
            ok = False
    return ok


def read_until_latency(port: Any, after_turn: int, timeout_s: float) -> dict[str, int] | None:
    deadline = time.monotonic() + timeout_s
    buffer = ""
    next_poll = 0.0
    while time.monotonic() < deadline:
        if time.monotonic() >= next_poll:
            port.write(b"m55qa_xz_latency\r\n")
            next_poll = time.monotonic() + 0.5
        waiting = port.in_waiting
        if waiting:
            buffer += port.read(waiting).decode("utf-8", errors="replace")
            lines = buffer.replace("\r", "\n").split("\n")
            buffer = lines.pop()
            for line in lines:
                row = parse_latency_line(line)
                if row and row["turn"] > after_turn:
                    return row
        time.sleep(0.05)
    return None


def run_benchmark(args: argparse.Namespace) -> tuple[list[dict[str, int]], int]:
    import serial

    rows: list[dict[str, int]] = []
    failures = 0
    last_turn = 0
    with serial.Serial(args.port, args.baud, timeout=0.1, write_timeout=1.0) as port:
        port.reset_input_buffer()
        for index in range(args.iterations):
            if args.mode == "text":
                port.write(f"m55qa_xz_text {args.prompt}\r\n".encode("utf-8"))
            elif args.mode == "probe" and not run_probe_turn(port, args.probe_ms, args.timeout):
                failures += 1
                continue
            row = read_until_latency(port, last_turn, args.timeout)
            if row is None:
                failures += 1
                print(f"turn {index + 1}: timeout")
                continue
            last_turn = row["turn"]
            row["sample"] = index + 1
            rows.append(row)
            print(f"turn {last_turn}: speech_audio={row['speech_audio']}ms eou={row['eou']}ms")
            time.sleep(args.interval)
    return rows, failures


def write_results(output_dir: Path, rows: list[dict[str, int]], failures: int, metadata: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "turns.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample", *FIELDS])
        writer.writeheader()
        writer.writerows(rows)
    payload = {"metadata": metadata, "summary": summarize(rows, failures), "turns": rows}
    (output_dir / "report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure M55 XiaoZhi stage latency through the M33 shell.")
    parser.add_argument("--port", default="COM26")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--mode", choices=("text", "probe", "observe"), default="text")
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--prompt", default="请用一句话介绍你自己")
    parser.add_argument("--probe-ms", type=int, default=1200)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path("xiaozhi_latency_results") / datetime.now().strftime("%Y%m%d-%H%M%S")
    rows, failures = run_benchmark(args)
    write_results(output, rows, failures, vars(args) | {"output": str(output)})
    print(json.dumps(summarize(rows, failures), ensure_ascii=False, indent=2))
    return 0 if rows and failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
