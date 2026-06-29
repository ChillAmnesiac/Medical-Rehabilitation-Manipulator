from __future__ import annotations

from .loop_contracts import LanguageIntent, RehabMode


FETCH_KEYWORDS = [
    "口渴",
    "喝水",
    "拿",
    "取",
    "递给我",
    "水杯",
    "杯子",
    "瓶子",
    "bottle",
    "cup",
]

TRAINING_KEYWORDS = [
    "训练",
    "康复",
    "开始今天",
    "今日训练",
    "动作训练",
    "training",
]

ASSISTIVE_KEYWORDS = [
    "助力",
    "辅助",
    "肌电",
    "发力",
    "emg",
    "assist",
]


def classify_language_intent(text: str) -> LanguageIntent:
    normalized = (text or "").strip().lower()
    if not normalized:
        return LanguageIntent(raw_text=text, mode=RehabMode.CHAT, confidence=0.2)

    if any(keyword in normalized for keyword in TRAINING_KEYWORDS):
        return LanguageIntent(raw_text=text, mode=RehabMode.TRAINING, confidence=0.85)

    if any(keyword in normalized for keyword in ASSISTIVE_KEYWORDS):
        return LanguageIntent(raw_text=text, mode=RehabMode.ASSISTIVE_EMG, confidence=0.80)

    if any(keyword in normalized for keyword in FETCH_KEYWORDS):
        target_label = "target_bottle" if "瓶" in normalized or "bottle" in normalized else "target_cup"
        return LanguageIntent(
            raw_text=text,
            mode=RehabMode.FETCH_OBJECT,
            target_label=target_label,
            confidence=0.85,
        )

    return LanguageIntent(raw_text=text, mode=RehabMode.CHAT, confidence=0.65)
