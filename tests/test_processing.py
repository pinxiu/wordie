from collections import Counter

from wordie.processing import VocabularyList, analyze_vocabulary, tokenize_text


def test_tokenize_text_basic():
    text = "Harry's wand is powerful. Harry, Hermione, Ron!"
    tokens = tokenize_text(text)
    assert "harry's" in tokens
    assert "hermione" in tokens
    assert "ron" in tokens


def test_analyze_vocabulary_matches_and_out_of_range():
    counter = Counter({"magic": 4, "wand": 3, "school": 2, "owl": 1})
    lists = [
        VocabularyList(name="elementary", words={"school", "owl"}, translations={}),
        VocabularyList(name="toefl", words={"magic", "arcane"}, translations={"magic": "魔法"}),
    ]

    result = analyze_vocabulary(counter, lists)

    assert set(result.keys()) == {"elementary", "toefl", "out_of_range"}
    assert set(result["toefl"]["word"].tolist()) == {"magic"}
    assert set(result["out_of_range"]["word"].tolist()) == {"wand"}
