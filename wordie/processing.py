from __future__ import annotations

import io
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import BinaryIO

import pandas as pd

WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


@dataclass
class VocabularyList:
    name: str
    words: set[str]
    translations: dict[str, str]


def normalize_word(word: str) -> str:
    return word.strip().lower()


def tokenize_text(text: str) -> list[str]:
    tokens = [normalize_word(m.group(0)) for m in WORD_PATTERN.finditer(text)]
    return [t for t in tokens if t]


def extract_words_from_pdf_bytes(pdf_bytes: bytes) -> tuple[Counter, str]:
    import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text_parts: list[str] = []
    for page in doc:
        full_text_parts.append(page.get_text("text"))
    doc.close()

    full_text = "\n".join(full_text_parts)
    tokens = tokenize_text(full_text)
    return Counter(tokens), full_text


def _resolve_column(columns: list[str], candidates: list[str]) -> str | None:
    lowered = {c.lower().strip(): c for c in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def parse_vocabulary_file(file_name: str, file_obj: BinaryIO) -> VocabularyList:
    suffix = file_name.lower().split(".")[-1]
    list_name = file_name.rsplit(".", 1)[0]

    if suffix == "txt":
        content = file_obj.read().decode("utf-8", errors="ignore")
        words: set[str] = set()
        translations: dict[str, str] = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "\t" in line:
                raw_word, raw_zh = line.split("\t", 1)
            elif "," in line:
                raw_word, raw_zh = line.split(",", 1)
            else:
                raw_word, raw_zh = line, ""

            word = normalize_word(raw_word)
            zh = raw_zh.strip()
            if word:
                words.add(word)
                if zh:
                    translations[word] = zh

        return VocabularyList(name=list_name, words=words, translations=translations)

    data = file_obj.read()
    if suffix in {"csv"}:
        df = pd.read_csv(io.BytesIO(data))
    elif suffix in {"xlsx", "xls"}:
        df = pd.read_excel(io.BytesIO(data))
    else:
        raise ValueError(f"Unsupported vocabulary list file type: {file_name}")

    if df.empty:
        return VocabularyList(name=list_name, words=set(), translations={})

    cols = list(df.columns)
    word_col = _resolve_column(cols, ["word", "english", "vocabulary"])
    translation_col = _resolve_column(cols, ["chinese", "translation", "zh"])

    if word_col is None:
        word_col = cols[0]

    words: set[str] = set()
    translations: dict[str, str] = {}

    for _, row in df.iterrows():
        raw_word = row.get(word_col)
        if pd.isna(raw_word):
            continue
        word = normalize_word(str(raw_word))
        if not word:
            continue
        words.add(word)

        if translation_col is not None:
            raw_zh = row.get(translation_col)
            if raw_zh is not None and not pd.isna(raw_zh):
                zh = str(raw_zh).strip()
                if zh:
                    translations[word] = zh

    return VocabularyList(name=list_name, words=words, translations=translations)


def analyze_vocabulary(counter: Counter, vocab_lists: list[VocabularyList]) -> dict[str, pd.DataFrame]:
    all_vocab_words = set().union(*(v.words for v in vocab_lists)) if vocab_lists else set()

    output: dict[str, pd.DataFrame] = {}

    word_to_lists: dict[str, list[str]] = defaultdict(list)
    translation_index: dict[str, str] = {}

    for vocab in vocab_lists:
        for word in vocab.words:
            word_to_lists[word].append(vocab.name)
        translation_index.update(vocab.translations)

    for vocab in vocab_lists:
        rows = []
        for word in sorted(vocab.words):
            count = counter.get(word, 0)
            if count > 0:
                rows.append(
                    {
                        "word": word,
                        "count": count,
                        "chinese": translation_index.get(word, ""),
                        "lists": ", ".join(sorted(word_to_lists[word])),
                    }
                )
        output[vocab.name] = pd.DataFrame(rows).sort_values(
            by=["count", "word"], ascending=[False, True]
        ) if rows else pd.DataFrame(columns=["word", "count", "chinese", "lists"])

    out_of_range_rows = []
    for word, count in counter.items():
        if word not in all_vocab_words:
            out_of_range_rows.append(
                {
                    "word": word,
                    "count": count,
                    "chinese": "",
                    "lists": "out_of_range",
                }
            )

    output["out_of_range"] = pd.DataFrame(out_of_range_rows).sort_values(
        by=["count", "word"], ascending=[False, True]
    ) if out_of_range_rows else pd.DataFrame(columns=["word", "count", "chinese", "lists"])

    return output
