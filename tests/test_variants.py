from __future__ import annotations

import re

from reglem.variants import expand_variants


def test_expand_variants_no_table_matches_leaves_text_escaped() -> None:
    assert expand_variants("abc", {}) == re.escape("abc")


def test_expand_variants_matches_plain_and_variant() -> None:
    fragment = expand_variants("a", {"a": "A"})
    pattern = re.compile(fragment)
    assert pattern.fullmatch("a")
    assert pattern.fullmatch("A")
    assert not pattern.fullmatch("b")


def test_expand_variants_only_touches_mapped_chars() -> None:
    fragment = expand_variants("ab", {"a": "A"})
    pattern = re.compile(fragment)
    assert pattern.fullmatch("ab")
    assert pattern.fullmatch("Ab")
    assert not pattern.fullmatch("aB")


def test_expand_variants_no_lookaround() -> None:
    fragment = expand_variants("a", {"a": "A"})
    assert "(?=" not in fragment
    assert "(?!" not in fragment


def test_expand_variants_empty_string() -> None:
    assert expand_variants("", {"a": "A"}) == ""


def test_expand_variants_escapes_regex_metacharacters() -> None:
    fragment = expand_variants(".", {})
    assert fragment == re.escape(".")
    assert not re.compile(fragment).fullmatch("x")
