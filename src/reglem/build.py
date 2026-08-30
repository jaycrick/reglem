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

A language may also declare, per lemma, terminator characters that must be
*excluded* for that lemma specifically (`Language.excluded_terminators` --
see `languages/greek.py`'s `ARTICLE_FORMS` for why). When no lemma triggers
an exclusion, the whole set shares one terminator group exactly as above.
When one does, the alternatives are split into groups by their effective
terminator set and each group gets its own trailing group instead:
`^((?:lemma-a|lemma-b)(?:[terminators]|$)|(?:lemma-c)(?:[fewer-terminators]|$))`.
A branch whose lemma matches but whose terminator doesn't still falls
through to try the next branch, under ordinary leftmost-first alternation
(true for both Python's `re` and the Rust `regex` crate) -- so this still
needs no lookaround, same as the single-group form.
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


def _terminator_group(terminators: str) -> str:
    """Regex fragment matching one allowed terminator, or end-of-string.

    `terminators` may be empty (every character excluded for this lemma) --
    `[]` is not a valid regex character class, so that case falls back to
    requiring end-of-string outright.
    """
    if not terminators:
        return "$"
    return f"[{re.escape(terminators)}]|$"


def build_pattern(lemmas: list[str], options: SearchOptions | None = None) -> str:
    """Build a bare (unquoted, un-field-prefixed) regex pattern matching `lemmas`.

    Raises `EmptyLemmaSetError` if `lemmas` is empty or normalizes down to
    nothing (e.g. all blank strings).
    """
    options = options or SearchOptions()
    alternatives = prepare_lemmas(lemmas, strip_trailing_digits=options.strip_trailing_digits)
    if not alternatives:
        raise EmptyLemmaSetError

    language = get_language(options.language)  # already validated by SearchOptions
    table: VariantTable | None = None
    if options.with_macrons:
        table = language.variant_tables.get("macrons")
    excluded_terminators = language.excluded_terminators

    # Group alternatives by their effective (post-exclusion) terminator
    # string, preserving prepare_lemmas' longest-first order within a group.
    groups: dict[str, list[str]] = {}
    for alt in alternatives:
        excluded = excluded_terminators.get(alt, "")
        effective = "".join(char for char in options.terminators if char not in excluded)
        groups.setdefault(effective, []).append(alt)

    if len(groups) == 1:
        (effective,) = groups
        alternation = "|".join(_expand(alt, table) for alt in alternatives)
        pattern = f"^({alternation})({_terminator_group(effective)})"
    else:
        # Unrestricted group (if any) first, then the rest sorted for a
        # deterministic, reviewable pattern.
        ordered = sorted(groups, key=lambda t: (t != options.terminators, t))
        branches = [
            f"(?:{'|'.join(_expand(alt, table) for alt in groups[effective])})"
            f"(?:{_terminator_group(effective)})"
            for effective in ordered
        ]
        pattern = f"^({'|'.join(branches)})"

    re.compile(pattern)  # self-check: fail here, not at the point of use
    return pattern
