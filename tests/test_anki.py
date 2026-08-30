from __future__ import annotations

import re

import pytest

from reglem.anki import build_anki_search
from reglem.errors import EmptyLemmaSetError
from reglem.options import SearchOptions

LEMMAS = ["ὁ", "καί", "νῦν δή", "ἀγαθός"]


@pytest.fixture
def query() -> str:
    return build_anki_search(LEMMAS, SearchOptions(field="Greek"))


@pytest.fixture
def pattern(query: str) -> re.Pattern[str]:
    inner = query[1:-1]  # drop surrounding quotes
    assert inner.startswith("Greek:re:")
    raw = inner[len("Greek:re:") :]
    return re.compile(raw)


def test_query_has_no_lookahead(query: str) -> None:
    assert "(?=" not in query
    assert "(?!" not in query


def test_query_is_quoted_and_anchored(query: str) -> None:
    assert query.startswith('"Greek:re:^(')
    assert query.endswith('"')


def test_match_behaviour(pattern: re.Pattern[str]) -> None:
    assert pattern.search("ὁ, ἡ, τό  the")
    assert not pattern.search("ὁδός, -οῦ  road")
    assert pattern.search("νῦν δή just now")


def test_custom_field() -> None:
    query = build_anki_search(["cat"], SearchOptions(field="Front"))
    assert query.startswith('"Front:re:')


def test_field_with_quote_is_escaped() -> None:
    query = build_anki_search(["cat"], SearchOptions(field='we"ird'))
    assert 'we\\"ird' in query


def test_empty_lemma_list_raises() -> None:
    with pytest.raises(EmptyLemmaSetError):
        build_anki_search([])


def test_default_options_used_when_none_given() -> None:
    query = build_anki_search(["cat"])
    assert query.startswith('"Greek:re:')
