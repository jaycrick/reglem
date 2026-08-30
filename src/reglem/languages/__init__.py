"""Registry of known languages.

A plain dict, not a plugin system -- with one language, entry-point discovery
would be pure ceremony. Revisit once a second language actually shows up.
"""

from __future__ import annotations

from reglem.errors import UnknownLanguageError
from reglem.languages._base import Language
from reglem.languages.greek import GREEK

_REGISTRY: dict[str, Language] = {GREEK.name: GREEK}


def get_language(name: str) -> Language:
    """Look up a `Language` by name, raising `UnknownLanguageError` if unknown."""
    try:
        return _REGISTRY[name]
    except KeyError:
        raise UnknownLanguageError(name, available_languages()) from None


def available_languages() -> tuple[str, ...]:
    """Return the names of every registered language, sorted."""
    return tuple(sorted(_REGISTRY))


__all__ = ["Language", "available_languages", "get_language"]
