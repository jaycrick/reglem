from __future__ import annotations

import re
import unicodedata

import pytest

from reglem.languages.greek import GREEK, MACRON_MAP
from reglem.variants import expand_variants

# Independently constructed (not copy-pasted from greek.py) so a
# transcription error in the source table would still be caught here.
EXPECTED = {
    "α": {
        "α": "ᾱ",
        "ά": "ᾱ" + "́",
        "ὰ": "ᾱ" + "̀",
        "ἀ": "ᾱ" + "̓",
        "ἁ": "ᾱ" + "̔",
        "ἄ": "ᾱ" + "̓" + "́",
        "ἅ": "ᾱ" + "̔" + "́",
        "ἂ": "ᾱ" + "̓" + "̀",
        "ἃ": "ᾱ" + "̔" + "̀",
    },
    "ι": {
        "ι": "ῑ",
        "ί": "ῑ" + "́",
        "ὶ": "ῑ" + "̀",
        "ἰ": "ῑ" + "̓",
        "ἱ": "ῑ" + "̔",
        "ἴ": "ῑ" + "̓" + "́",
        "ἵ": "ῑ" + "̔" + "́",
        "ἲ": "ῑ" + "̓" + "̀",
        "ἳ": "ῑ" + "̔" + "̀",
    },
    "υ": {
        "υ": "ῡ",
        "ύ": "ῡ" + "́",
        "ὺ": "ῡ" + "̀",
        "ὐ": "ῡ" + "̓",
        "ὑ": "ῡ" + "̔",
        "ὔ": "ῡ" + "̓" + "́",
        "ὕ": "ῡ" + "̔" + "́",
        "ὒ": "ῡ" + "̓" + "̀",
        "ὓ": "ῡ" + "̔" + "̀",
    },
}

FLAT_EXPECTED = {k: v for cases in EXPECTED.values() for k, v in cases.items()}


def test_map_size() -> None:
    assert len(MACRON_MAP) == 27


@pytest.mark.parametrize("surface", sorted(FLAT_EXPECTED))
def test_macron_map_entries(surface: str) -> None:
    assert MACRON_MAP[surface] == FLAT_EXPECTED[surface]


def test_all_values_nfc_stable() -> None:
    for value in MACRON_MAP.values():
        assert unicodedata.normalize("NFC", value) == value


@pytest.mark.parametrize(
    "circumflex_form",
    ["ᾶ", "ἆ", "ἇ", "ῖ", "ἶ", "ἷ", "ῦ", "ὖ", "ὗ"],
)
def test_circumflex_forms_excluded(circumflex_form: str) -> None:
    # A circumflex already implies a long vowel, so it has no macron alternative.
    assert circumflex_form not in MACRON_MAP


def test_registered_as_greek_language() -> None:
    assert GREEK.name == "greek"
    # pydantic copies the dict into the model rather than keeping the same
    # object, so compare contents, not identity.
    assert GREEK.variant_tables["macrons"] == MACRON_MAP


def test_expand_variants_with_macron_map_matches_both_forms() -> None:
    fragment = expand_variants("ἀγαθός", MACRON_MAP)
    pattern = re.compile(fragment)
    assert pattern.fullmatch("ἀγαθός")  # unmarked
    assert pattern.fullmatch("ᾱ̓γαθός")  # first alpha marked long
    assert pattern.fullmatch("ἀγᾱθός")  # second alpha marked long
    assert pattern.fullmatch("ᾱ̓γᾱθός")  # both marked long
    assert not pattern.fullmatch("ἀγαθόν")  # different word entirely


def test_expand_variants_with_macron_map_leaves_non_target_chars_alone() -> None:
    # δέ contains no α/ι/υ, so nothing should be expanded.
    fragment = expand_variants("δέ", MACRON_MAP)
    assert fragment == re.escape("δέ")
