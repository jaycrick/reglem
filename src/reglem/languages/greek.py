"""Greek variant tables: macron (long-vowel) alternatives for α, ι, υ.

Many Greek word lists (e.g. lemma dictionaries, vocabulary tools) mark accent
and breathing but never vowel *length* -- α, ι, and υ are ambiguous between
short and long in that spelling. Pedagogical texts, by contrast, often mark
long instances of these three vowels with a macron layered on top of
whatever accent/breathing the vowel already carries, e.g. a long alpha with
smooth breathing appears as ᾱ̓ rather than ἀ.

Unicode has a precomposed macron-vowel character (ᾱ ῑ ῡ) but NOT a
precomposed macron+breathing or macron+accent character -- those are the
macron-vowel codepoint followed by ordinary *combining* breathing/accent
marks (U+0313 smooth, U+0314 rough, U+0301 acute, U+0300 grave), breathing
before accent. Verified against Python's `unicodedata` (both directions):

    >>> import unicodedata
    >>> unicodedata.normalize("NFC", "ᾱ" + "̓" + "́") == "ᾱ" + "̓" + "́"
    True  # already canonical -- NFC does not reorder or recompose it further

Also verified: NFC always resolves the alpha/iota/upsilon + acute ambiguity
(there are two Unicode encodings of e.g. "alpha with acute", the polytonic
U+1F71 and the monotonic U+03AC "tonos" form) down to the single tonos
codepoint -- most Greek lemma sources use NFC text, so there's no
dual-encoding to account for on that side.

Circumflex forms (ᾶ, ἆ, ἇ, and the ι/υ equivalents) are deliberately absent
from MACRON_MAP: a circumflex accent can only fall on a long vowel, so a
circumflexed α/ι/υ is already unambiguously long and has no separate macron
form to search for.

Known simplification: this maps every occurrence of a bare/accented/breathed
α, ι, or υ, including ones that are actually the first or second vowel of a
diphthong (αι, αυ, ει, ευ, οι, ου, υι), where a macron would never actually
be written. This only makes a generated pattern larger (extra alternation
branches that can never match anything real), not incorrect -- reliably
detecting diphthongs is much more machinery than the false-positive cost
justifies here.

Separately, `ARTICLE_FORMS` lists the 19 forms of the Greek definite article.
A lemma pattern normally allows a plain space right after a matched lemma
(see `DEFAULT_TERMINATORS` in `options.py`), but the article is special: it
is never the last thing before running Greek text in a dictionary/word-list
entry the way an ordinary headword is. Instead it's cited on its own, joined
to its other forms by punctuation -- `ὁ, ἡ, τό` or `ὁ/ἡ/τό` -- while in
running text it is immediately followed by the word it modifies (`ὁ σοφός`,
`ἡ ἀρίστη`). Without an exception, an article lemma matches the start of
every one of those unrelated entries. So `GREEK.excluded_terminators` denies
a plain space, and a non-breaking space (U+00A0), right after any article
form -- comma, period, slash, and end-of-field are still allowed.

NBSP is excluded for the same reason it's a default terminator at all
(`options.py`'s `DEFAULT_TERMINATORS` docstring): it renders as an invisible
space in the Anki editor while still separating words in field HTML, so it
needs the same treatment as a literal space here.

Grave-accented forms (τὸν, τὴν, τοὺς, τὰς -- the article as it actually
appears in running text, where an acute shifts to a grave before another
word) are deliberately not in `ARTICLE_FORMS`: a lemma list cites the acute
citation form, not the running-text accentuation, so there is nothing to
exclude a terminator from for those spellings. Adding them would be a
one-line extension if a source ever needs it.
"""

from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING

from reglem.languages._base import Language

if TYPE_CHECKING:
    from reglem.variants import VariantTable

_SMOOTH = "̓"  # combining comma above (psili)
_ROUGH = "̔"  # combining reversed comma above (dasia)
_ACUTE = "́"  # combining acute accent (oxia)
_GRAVE = "̀"  # combining grave accent (varia)


def _macron_table(bare: str, macron_base: str, breathing_accent_block: str) -> dict[str, str]:
    """Build the 9-entry {surface_form: macron_form} table for one vowel.

    `breathing_accent_block` holds the eight precomposed Greek Extended
    characters for this vowel, in the fixed order: smooth, rough,
    smooth+grave, rough+grave, smooth+acute, rough+acute, grave, acute.
    """
    smooth, rough, smooth_grave, rough_grave, smooth_acute, rough_acute, grave, acute = (
        breathing_accent_block
    )
    return {
        bare: macron_base,
        acute: macron_base + _ACUTE,
        grave: macron_base + _GRAVE,
        smooth: macron_base + _SMOOTH,
        rough: macron_base + _ROUGH,
        smooth_acute: macron_base + _SMOOTH + _ACUTE,
        rough_acute: macron_base + _ROUGH + _ACUTE,
        smooth_grave: macron_base + _SMOOTH + _GRAVE,
        rough_grave: macron_base + _ROUGH + _GRAVE,
    }


# fmt: off
MACRON_MAP: VariantTable = {
    **_macron_table("α", "ᾱ", "ἀἁἂἃἄἅὰά"),
    **_macron_table("ι", "ῑ", "ἰἱἲἳἴἵὶί"),
    **_macron_table("υ", "ῡ", "ὐὑὒὓὔὕὺύ"),
}
# fmt: on

_EXPECTED_MACRON_MAP_SIZE = 27  # 9 each for α/ι/υ
assert len(MACRON_MAP) == _EXPECTED_MACRON_MAP_SIZE, (  # noqa: S101
    f"expected {_EXPECTED_MACRON_MAP_SIZE} entries, got {len(MACRON_MAP)}"
)

# fmt: off
ARTICLE_FORMS: tuple[str, ...] = tuple(
    unicodedata.normalize("NFC", form)
    for form in (
        "ὁ", "ἡ", "τό",
        "τοῦ", "τῆς", "τῷ", "τῇ", "τόν", "τήν",
        "τώ", "τοῖν",
        "οἱ", "αἱ", "τά", "τῶν", "τοῖς", "ταῖς", "τούς", "τάς",
    )
)
# fmt: on
"""The 19 forms of the Greek definite article (masc./fem./neut., all cases,
all numbers), NFC-normalized to match how `prepare_lemmas` compares lemmas.
See the module docstring for why these specifically need a terminator
exception.
"""

_EXPECTED_ARTICLE_FORM_COUNT = 19
assert len(ARTICLE_FORMS) == _EXPECTED_ARTICLE_FORM_COUNT, (  # noqa: S101
    f"expected {_EXPECTED_ARTICLE_FORM_COUNT} article forms, got {len(ARTICLE_FORMS)}"
)

_SPACE_TERMINATORS = " \xa0"  # plain space, non-breaking space

GREEK = Language(
    name="greek",
    variant_tables={"macrons": MACRON_MAP},
    excluded_terminators=dict.fromkeys(ARTICLE_FORMS, _SPACE_TERMINATORS),
)
