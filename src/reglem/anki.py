"""Wrap a lemma pattern as a quoted Anki `field:re:...` search string.

Anki field regexes are unanchored by default (`front:re:[a-c]1` matches
anywhere in the field, not just at its start), which is why `build_pattern`
anchors with `^` explicitly rather than relying on Anki to do it.
"""

from __future__ import annotations

from reglem.build import build_pattern
from reglem.options import SearchOptions


def build_anki_search(lemmas: list[str], options: SearchOptions | None = None) -> str:
    """Build a quoted `"field:re:pattern"` Anki search matching any of `lemmas`.

    Raises `EmptyLemmaSetError` (from `build_pattern`) if `lemmas` is empty.
    """
    options = options or SearchOptions()
    pattern = build_pattern(lemmas, options)
    escaped_field = options.field.replace('"', '\\"')
    escaped_pattern = pattern.replace('"', '\\"')
    return f'"{escaped_field}:re:{escaped_pattern}"'
