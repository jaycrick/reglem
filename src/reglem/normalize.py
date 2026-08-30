"""Normalize raw lemma text before it goes into a pattern.

Two independent cleanups live here:

- Unicode NFC normalization, so visually-identical lemmas that happen to use
  different combining-mark orders or precomposed-vs-decomposed forms compare
  equal.
- Optional trailing-digit stripping, for word lists that disambiguate
  homographs with a suffix digit (e.g. ``lead2`` for the metal vs. ``lead``
  the verb). Off by default -- not every source uses this convention, and
  guessing wrong silently merges two different words.
"""

from __future__ import annotations

import re
import unicodedata

_TRAILING_DIGITS_RE = re.compile(r"\d+$")


def normalize_lemma(text: str, *, strip_trailing_digits: bool = False) -> str:
    """Return `text` NFC-normalized, optionally with trailing digits removed."""
    if strip_trailing_digits:
        text = _TRAILING_DIGITS_RE.sub("", text)
    return unicodedata.normalize("NFC", text)


def prepare_lemmas(
    lemmas: list[str],
    *,
    strip_trailing_digits: bool = False,
) -> list[str]:
    """Normalize, drop blanks, dedupe, and order a list of raw lemmas.

    Order is longest-first (ties broken alphabetically) rather than
    insertion order or plain sort: it's deterministic, and it guarantees a
    longer alternative is tried before a shorter one that happens to be its
    prefix, which matters under leftmost-first regex alternation (the
    engines targeted here, including the Rust `regex` crate Anki embeds,
    pick the first alternative that matches rather than the longest).
    """
    normalized = (
        normalize_lemma(lemma, strip_trailing_digits=strip_trailing_digits).strip()
        for lemma in lemmas
    )
    deduped = {lemma for lemma in normalized if lemma}
    return sorted(deduped, key=lambda lemma: (-len(lemma), lemma))
