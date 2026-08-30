from __future__ import annotations

import re

from hypothesis import assume, given
from hypothesis import strategies as st

from reglem.build import build_pattern
from reglem.languages.greek import ARTICLE_FORMS
from reglem.options import SearchOptions

# Plain Greek letters plus a handful of the ambiguous-length accented/breathed
# forms macron expansion cares about -- enough to exercise both the plain and
# the `--macrons` code path without needing the full alphabet.
_GREEK_CHARS = "αβγδεζηθικλμνξοπρστυφχψωἀἁάἰἱίὐὑύ"


@given(
    lemma=st.text(alphabet=_GREEK_CHARS, min_size=1, max_size=8),
    with_macrons=st.booleans(),
)
def test_pattern_matches_its_own_lemma_at_field_start(
    lemma: str,
    with_macrons: bool,
) -> None:
    # ο/α/ἱ are all in _GREEK_CHARS, so Hypothesis can draw exactly "οἱ" or
    # "αἱ" -- both Greek article forms, which (by design, see
    # languages/greek.py) reject a plain-space terminator. That's covered
    # separately below; excluded here so this generic property holds.
    assume(lemma not in ARTICLE_FORMS)
    pattern = re.compile(build_pattern([lemma], SearchOptions(with_macrons=with_macrons)))
    assert pattern.search(lemma + " rest")


def test_article_lemma_rejects_space_but_accepts_comma() -> None:
    pattern = re.compile(build_pattern(["ὁ"]))
    assert not pattern.search("ὁ rest")
    assert pattern.search("ὁ, rest")


@given(lemma=st.text(alphabet=_GREEK_CHARS, min_size=1, max_size=8))
def test_pattern_rejects_lemma_prefixed_by_another_letter(lemma: str) -> None:
    pattern = re.compile(build_pattern([lemma]))
    assert not pattern.search("ξ" + lemma + " rest")
