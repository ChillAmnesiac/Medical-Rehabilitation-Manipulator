from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CFG = (ROOT / "applications" / "control" / "control_layer_cfg.h").read_text(
    encoding="utf-8"
)
SOURCE = (ROOT / "applications" / "control" / "rehab_resist_strategy.c").read_text(
    encoding="utf-8"
)
HEADER = (ROOT / "applications" / "control" / "rehab_resist_strategy.h").read_text(
    encoding="utf-8"
)


class RehabResistSlewStaticTest(unittest.TestCase):
    def test_resist_current_has_bounded_slew(self):
        self.assertIn(
            "#define CONTROL_REHAB_RESIST_SLEW_A_PER_STEP (0.03f)", CFG
        )
        self.assertIn("float last_current_a;", HEADER)
        self.assertIn("state->last_current_a = 0.0f;", SOURCE)
        self.assertIn("static float rehab_resist_strategy_slew", SOURCE)

        target = SOURCE.index("out->current_a = -params->resist_direction")
        slew = SOURCE.index("out->current_a = rehab_resist_strategy_slew", target)
        store = SOURCE.index("state->last_current_a = out->current_a", slew)
        self.assertLess(target, slew)
        self.assertLess(slew, store)
        self.assertIn("CONTROL_REHAB_RESIST_SLEW_A_PER_STEP", SOURCE[slew:store])


if __name__ == "__main__":
    unittest.main()
