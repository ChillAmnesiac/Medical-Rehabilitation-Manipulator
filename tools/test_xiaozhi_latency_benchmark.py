import unittest

from xiaozhi_latency_benchmark import parse_latency_line, summarize


class XiaoZhiLatencyBenchmarkTests(unittest.TestCase):
    def test_parse_and_summarize(self) -> None:
        row = parse_latency_line(
            "[m55qa] xz_latency seq=8 turn=3 flags=0x3 wake_listen=20 eou=901 "
            "stop_stt=400 stt_llm=500 llm_tts=600 tts_packet=700 packet_write=80 "
            "speech_audio=3181 wake_audio=4200 age_ticks=4"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["turn"], 3)
        self.assertEqual(row["speech_audio"], 3181)
        self.assertEqual(row["stop_audio"], 2280)
        summary = summarize([row, {**row, "speech_audio": 2000}, {**row, "speech_audio": 5000}])
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["speech_audio_ms"]["p50"], 3181)
        self.assertEqual(summary["speech_audio_ms"]["p95"], 5000)
        self.assertEqual(summary["failure_rate_pct"], 0.0)
        self.assertIn("stop_stt", summary["stage_share_pct"])


if __name__ == "__main__":
    unittest.main()
