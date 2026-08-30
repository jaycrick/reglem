"""Build an anchored regex alternation matching a set of lemmas.

The pattern shape is `^(alt1|alt2|...)([terminator-chars]|$)`: anchored to
the start of the field/line, so a lemma that's a prefix of another word
(`ὁ` vs `ὁδός`) doesn't false-match, and terminated by an explicit character
class or end-of-string rather than a lookahead assertion.

That terminator design isn't cosmetic: this is meant to also work as an Anki
`re:` search, and Anki's `re:` matching uses the Rust `regex` crate (see
https://docs.rs/regex, referenced from docs.ankiweb.net/searching.html),
which does NOT support lookaround. A pattern like `^word(?=[ ,])` is valid
Python/PCRE but invalid there -- the terminator has to be an ordinary
alternation group instead.

One anchored alternation over all lemmas, rather than one OR'd term per
lemma, keeps the pattern shorter and the match a single regex pass instead
of N.
"""

from __future__ import annotations

import re

from reglem.errors import EmptyLemmaSetError
from reglem.languages import get_language
from reglem.normalize import prepare_lemmas
from reglem.options import SearchOptions
from reglem.variants import VariantTable, expand_variants


def _expand(text: str, table: VariantTable | None) -> str:
    """Escape `text` literally, or with per-character variants from `table`."""
    if table is None:
        return re.escape(text)
    return expand_variants(text, table)


def build_pattern(lemmas: list[str], options: SearchOptions | None = None) -> str:
    """Build a bare (unquoted, un-field-prefixed) regex pattern matching `lemmas`.

    Raises `EmptyLemmaSetError` if `lemmas` is empty or normalizes down to
    nothing (e.g. all blank strings).
    """
    options = options or SearchOptions()
    alternatives = prepare_lemmas(lemmas, strip_trailing_digits=options.strip_trailing_digits)
    if not alternatives:
        raise EmptyLemmaSetError

    table: VariantTable | None = None
    if options.with_macrons:
        language = get_language(options.language)
        table = language.variant_tables.get("macrons")

    alternation = "|".join(_expand(alt, table) for alt in alternatives)
    terminator_class = re.escape(options.terminators)
    pattern = f"^({alternation})([{terminator_class}]|$)"

    re.compile(pattern)  # self-check: fail here, not at the point of use
    return pattern
