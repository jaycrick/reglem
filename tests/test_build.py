from __future__ import annotations

import re

import pytest

from reglem.build import build_pattern
from reglem.errors import EmptyLemmaSetError
from reglem.options import SearchOptions

LEMMAS = ["ὁ", "καί", "δέω2", "νῦν δή", "ἀγαθός"]


@pytest.fixture
def pattern() -> re.Pattern[str]:
    raw = build_pattern(LEMMAS, SearchOptions(strip_trailing_digits=True))
    return re.compile(raw)


def test_pattern_is_anchored_and_has_no_lookaround(pattern: re.Pattern[str]) -> None:
    assert pattern.pattern.startswith("^(")
    assert "(?=" not in pattern.pattern
    assert "(?!" not in pattern.pattern


@pytest.mark.parametrize(
    ("field_text", "expected"),
    [
        ("ὁ, ἡ, τό  the", True),
        ("ὁ", True),
        ("ὁδός, -οῦ  road", False),  # prefix must not leak past the terminator
        ("καί and, also", True),
        ("νῦν δή just now", True),  # multi-word lemma
        ("δέω to bind", True),  # δέω2 -> δέω after trailing-digit strip
        ("  ὁ leading space", False),  # anchored to start
        ("ἀγαθός good", True),
        ("Ξενοφῶν Xenophon", False),
        ("ὁ\xa0the", True),  # non-breaking space terminator
        ("ἀγαθόν good (wrong ending)", False),
    ],
)
def test_match_behaviour(pattern: re.Pattern[str], field_text: str, expected: bool) -> None:
    assert bool(pattern.search(field_text)) == expected


def test_macrons_disabled_by_default() -> None:
    raw = build_pattern(LEMMAS)
    assert "(?:" not in raw
    pattern = re.compile(raw)
    assert pattern.search("ἀγαθός good")
    assert not pattern.search("ᾱ̓γαθός good")


def test_macrons_enabled_matches_marked_form() -> None:
    raw = build_pattern(LEMMAS, SearchOptions(with_macrons=True))
    pattern = re.compile(raw)
    assert pattern.search("ᾱ̓γαθός good")


def test_trailing_digit_kept_by_default() -> None:
    raw = build_pattern(["word2"])
    pattern = re.compile(raw)
    assert not pattern.search("word alone")
    assert pattern.search("word2 alone")


def test_homograph_digits_collapse_to_one_alternative_when_stripped() -> None:
    raw = build_pattern(["ὅς", "ὅς2"], SearchOptions(strip_trailing_digits=True))
    assert raw.count("ὅς") == 1


def test_empty_lemma_list_raises() -> None:
    with pytest.raises(EmptyLemmaSetError):
        build_pattern([])


def test_blank_lemmas_raise() -> None:
    with pytest.raises(EmptyLemmaSetError):
        build_pattern(["", "  "])


def test_custom_terminators() -> None:
    raw = build_pattern(["cat"], SearchOptions(terminators=";"))
    pattern = re.compile(raw)
    assert pattern.search("cat;dog")
    assert not pattern.search("cat,dog")
