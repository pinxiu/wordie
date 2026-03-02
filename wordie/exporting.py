from __future__ import annotations

import io
from typing import Iterable

import pandas as pd


def export_excel_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31] if sheet_name else "Sheet1"
            df.to_excel(writer, sheet_name=safe_name, index=False)
    return output.getvalue()


def annotate_pdf_bytes(
    pdf_bytes: bytes,
    selected_words: Iterable[str],
    translations: dict[str, str],
) -> bytes:
    import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page in doc:
        for word in selected_words:
            rects = page.search_for(word, quads=False)
            for rect in rects:
                annot = page.add_highlight_annot(rect)
                zh = translations.get(word, "")
                annot.set_info(content=f"{word}: {zh}" if zh else word)
                annot.update()

    output = io.BytesIO()
    doc.save(output, garbage=4, deflate=True)
    doc.close()
    return output.getvalue()
