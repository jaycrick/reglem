from __future__ import annotations

from reglem.normalize import normalize_lemma, prepare_lemmas


def test_normalize_lemma_nfc() -> None:
    decomposed = "ε" + "́"  # epsilon + combining acute
    precomposed = "έ"
    assert normalize_lemma(decomposed) == normalize_lemma(precomposed)


def test_normalize_lemma_strips_trailing_digits_when_asked() -> None:
    assert normalize_lemma("word2", strip_trailing_digits=True) == "word"
    assert normalize_lemma("word2", strip_trailing_digits=False) == "word2"


def test_normalize_lemma_leaves_internal_digits() -> None:
    assert normalize_lemma("a2b", strip_trailing_digits=True) == "a2b"


def test_prepare_lemmas_dedupes_and_drops_blanks() -> None:
    result = prepare_lemmas(["a", "a", "", "  ", "b"])
    assert result in (["a", "b"], ["b", "a"])
    assert set(result) == {"a", "b"}


def test_prepare_lemmas_longest_first() -> None:
    result = prepare_lemmas(["a", "aa", "aaa"])
    assert result == ["aaa", "aa", "a"]


def test_prepare_lemmas_ties_broken_alphabetically() -> None:
    result = prepare_lemmas(["ba", "ab"])
    assert result == ["ab", "ba"]


def test_prepare_lemmas_folds_homographs_when_stripping() -> None:
    result = prepare_lemmas(["word2", "word"], strip_trailing_digits=True)
    assert result == ["word"]


def test_prepare_lemmas_empty_input() -> None:
    assert prepare_lemmas([]) == []


def test_prepare_lemmas_all_blank() -> None:
    assert prepare_lemmas(["", "  ", "\t"]) == []
