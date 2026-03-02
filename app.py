from __future__ import annotations

import streamlit as st

from wordie.exporting import annotate_pdf_bytes, export_excel_bytes
from wordie.processing import analyze_vocabulary, extract_words_from_pdf_bytes, parse_vocabulary_file
from wordie.translation import Translator

st.set_page_config(page_title="Wordie Vocabulary Analyzer", layout="wide")
st.title("📘 Wordie Vocabulary Analyzer")
st.write(
    "Upload one PDF and multiple vocabulary lists. Then generate Excel reports and an annotated PDF with Chinese translations."
)

pdf_file = st.file_uploader("Upload English PDF", type=["pdf"])
vocab_files = st.file_uploader(
    "Upload vocabulary lists (.txt/.csv/.xlsx)",
    type=["txt", "csv", "xlsx", "xls"],
    accept_multiple_files=True,
)
auto_translate = st.checkbox("Auto-translate missing Chinese meanings", value=False)

if pdf_file and vocab_files:
    pdf_bytes = pdf_file.read()

    with st.spinner("Extracting words from PDF..."):
        counter, _ = extract_words_from_pdf_bytes(pdf_bytes)

    vocab_lists = []
    for vf in vocab_files:
        vf.seek(0)
        vocab_lists.append(parse_vocabulary_file(vf.name, vf))

    results = analyze_vocabulary(counter, vocab_lists)

    all_known_translations: dict[str, str] = {}
    for vocab in vocab_lists:
        all_known_translations.update(vocab.translations)

    if auto_translate:
        translator = Translator()
        with st.spinner("Translating words to Chinese..."):
            for key, df in results.items():
                words = df["word"].tolist() if not df.empty else []
                all_known_translations = translator.fill_translations(words, all_known_translations)
                if not df.empty:
                    results[key]["chinese"] = [all_known_translations.get(w, "") for w in words]

    st.subheader("Vocabulary analysis preview")
    tabs = st.tabs(list(results.keys()))
    for idx, (sheet_name, df) in enumerate(results.items()):
        with tabs[idx]:
            st.write(f"Rows: {len(df)}")
            st.dataframe(df, use_container_width=True)

    excel_bytes = export_excel_bytes(results)
    st.download_button(
        label="Download Excel report",
        data=excel_bytes,
        file_name="wordie_vocabulary_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("Annotated PDF")
    options = [v.name for v in vocab_lists]
    selected_list_names = st.multiselect(
        "Select one or multiple vocabulary lists to annotate in PDF",
        options=options,
        default=options[:1],
    )

    if selected_list_names:
        selected_words: set[str] = set()
        for vocab in vocab_lists:
            if vocab.name in selected_list_names:
                selected_words |= vocab.words

        if st.button("Generate annotated PDF"):
            with st.spinner("Annotating PDF..."):
                annotated_bytes = annotate_pdf_bytes(pdf_bytes, sorted(selected_words), all_known_translations)
            st.download_button(
                label="Download annotated PDF",
                data=annotated_bytes,
                file_name="wordie_annotated.pdf",
                mime="application/pdf",
            )
else:
    st.info("Please upload one PDF file and at least one vocabulary list file.")
