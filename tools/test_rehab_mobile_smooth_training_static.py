import unittest
from pathlib import Path


WEB = Path(r"F:\wt\platform-ai-latest\apps\web\public\rehab-arm-mobile")
MOBILE = Path(r"F:\wt\platform-ai-latest\apps\mobile\rehab-arm-android\www")

FORBIDDEN_TEXT = [
    "电机",
    "4号",
    "5号",
    "6号",
    "raw",
    "rad",
    "电流",
    "速度",
    "S曲线",
    "LADRC",
    "ADRC",
    "CSP",
    "协议",
    "调试",
    "工程模式",
    "AI方案",
    "助力",
    "阻力",
    "自由轨迹",
    "云端",
    "ROS",
    "NanoPi",
    "MuJoCo",
]

FORBIDDEN_COMMAND_KEYS = [
    '"target"',
    '"points"',
    '"velocity"',
    '"current"',
    '"raw"',
    '"repeat_count"',
]


class RehabMobileSmoothTrainingStaticTest(unittest.TestCase):
    def test_page_copy_and_forbidden_words(self):
        text = (WEB / "smooth-training.html").read_text(encoding="utf-8")

        for required in [
            "平稳动作训练",
            "选择一个固定动作，设备会按平缓节奏完成被动训练",
            "设备已连接 / 可以开始训练",
            "肘部屈伸",
            "肩部平转",
            "协同训练",
            "肩部前后",
            "尚未完成校准，暂不可用",
            "3次往返",
            "开始训练",
            "第 2 / 3 次",
            "平稳运行中",
            "暂停",
            "停止训练",
            "离开页面、蓝牙断开或设备异常时，训练会自动停止；恢复训练需要重新确认。",
        ]:
            self.assertIn(required, text)

        for forbidden in FORBIDDEN_TEXT:
            self.assertNotIn(forbidden, text)

    def test_page_sends_only_fixed_profiles(self):
        text = (WEB / "smooth-training.html").read_text(encoding="utf-8")

        for profile in [
            "fixed_elbow_flex_extend_v1",
            "fixed_shoulder_planar_v1",
            "fixed_coordinated_elbow_shoulder_v1",
        ]:
            self.assertIn(profile, text)

        self.assertNotIn("fixed_shoulder_fore_aft_v1", text)
        for forbidden_key in FORBIDDEN_COMMAND_KEYS:
            self.assertNotIn(forbidden_key, text)

    def test_home_links_to_smooth_training_without_debug_terms(self):
        text = (WEB / "home.html").read_text(encoding="utf-8")

        self.assertIn("smooth-training.html", text)
        self.assertIn("平稳动作训练", text)

    def test_webview_mirror_matches_web_page(self):
        self.assertEqual(
            (WEB / "smooth-training.html").read_text(encoding="utf-8"),
            (MOBILE / "smooth-training.html").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
