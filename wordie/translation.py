from __future__ import annotations

from typing import Iterable

try:
    from deep_translator import GoogleTranslator
except Exception:  # pragma: no cover - optional dependency runtime issue
    GoogleTranslator = None


class Translator:
    def __init__(self) -> None:
        self.cache: dict[str, str] = {}
        self.enabled = GoogleTranslator is not None

    def translate_word(self, word: str) -> str:
        if word in self.cache:
            return self.cache[word]

        if not self.enabled:
            self.cache[word] = ""
            return ""

        try:
            zh = GoogleTranslator(source="en", target="zh-CN").translate(word) or ""
        except Exception:
            zh = ""

        self.cache[word] = zh
        return zh

    def fill_translations(self, words: Iterable[str], existing: dict[str, str]) -> dict[str, str]:
        result = dict(existing)
        for word in words:
            if word not in result or not result[word]:
                result[word] = self.translate_word(word)
        return result
