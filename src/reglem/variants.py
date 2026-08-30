"""Expand a literal string into a regex fragment with per-character spelling variants.

A variant table maps one surface character to one alternative spelling of
that character (e.g. a plain vowel to its long-marked form). `expand_variants`
walks the input character by character, escaping every character literally
except the ones with a table entry, which become a non-capturing
`(?:plain|variant)` group.

This never emits lookaround (`(?=...)`, `(?!...)`), on purpose: some target
engines this feeds into -- notably the Rust `regex` crate Anki embeds -- don't
support it.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

VariantTable = Mapping[str, str]
"""Surface character -> alternative spelling of that character."""


def expand_variants(text: str, table: VariantTable) -> str:
    """Return a regex source fragment matching `text` or its per-character variants."""
    parts: list[str] = []
    for char in text:
        variant = table.get(char)
        if variant is None:
            parts.append(re.escape(char))
        else:
            parts.append(f"(?:{re.escape(char)}|{re.escape(variant)})")
    return "".join(parts)
