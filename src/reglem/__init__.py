"""reglem: build anchored regex alternations over word lemmas.

Turns a list of lemmas into one anchored regex alternation
(`^(lemma1|lemma2|...)([terminators]|$)`), with optional per-language
spelling-variant expansion (currently: Greek macron/long-vowel forms), and an
Anki `field:re:...` search-string wrapper. See `docs/greek.md` and the
README for the motivating detail.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from reglem.anki import build_anki_search
from reglem.build import build_pattern
from reglem.errors import EmptyLemmaSetError, ReglemError, UnknownLanguageError
from reglem.languages import available_languages, get_language
from reglem.normalize import normalize_lemma, prepare_lemmas
from reglem.options import SearchOptions

try:
    __version__ = version("reglem")
except PackageNotFoundError:  # pragma: no cover -- only hit for an uninstalled checkout
    __version__ = "0.0.0+unknown"

__all__ = [
    "EmptyLemmaSetError",
    "ReglemError",
    "SearchOptions",
    "UnknownLanguageError",
    "__version__",
    "available_languages",
    "build_anki_search",
    "build_pattern",
    "get_language",
    "normalize_lemma",
    "prepare_lemmas",
]
