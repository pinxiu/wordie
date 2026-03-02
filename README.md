# Wordie Vocabulary Analyzer

A local Streamlit app for analyzing difficult English vocabulary in a PDF book and mapping words to different vocabulary levels (elementary, middle school, high school, TOEFL/IELTS, etc.).

## Features

- Upload one English PDF book.
- Upload multiple vocabulary lists (`.txt`, `.csv`, `.xlsx`) with optional Chinese translations.
- Extract words from the full PDF and count word frequencies.
- Match book words against each vocabulary list.
- Generate an **out-of-range** list (words not covered by any uploaded list).
- Auto-translate missing Chinese translations (optional, requires internet).
- Export vocabulary results to Excel (`.xlsx`) with separate sheets.
- Generate an annotated PDF with highlights and translation notes for words from one or more selected vocabulary lists.

## Quick Start

1. Create a Python environment (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run app:

   ```bash
   streamlit run app.py
   ```

4. Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Vocabulary List File Format

Supported file types: `.txt`, `.csv`, `.xlsx`

- Required: one column/field containing English words.
- Optional: one column/field for Chinese translation.

Recommended column names:

- English word: `word`, `english`, `vocabulary`
- Chinese translation: `chinese`, `translation`, `zh`

For `.txt`:

- One word per line, e.g. `abandon`
- Or include translation with separators: `abandon, 放弃` or `abandon\t放弃`

## Notes

- Annotated PDF highlights all matched occurrences and adds an annotation popup with `word: 中文`.
- For very large PDFs, annotation can take time.
- Auto translation depends on external service availability.
