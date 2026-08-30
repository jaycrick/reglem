"""Error types raised by reglem."""

from __future__ import annotations


class ReglemError(Exception):
    """Base class for every error reglem raises on purpose."""


class EmptyLemmaSetError(ReglemError):
    """Raised when a pattern is requested for zero lemmas."""

    def __init__(self) -> None:
        """Build the fixed error message for this error."""
        super().__init__("no lemmas given -- need at least one to build a pattern")


class UnknownLanguageError(ReglemError):
    """Raised when a language name isn't in the registry."""

    def __init__(self, name: str, known: tuple[str, ...]) -> None:
        """Build an error message naming the bad `name` and the `known` alternatives."""
        super().__init__(f"unknown language {name!r}; known languages: {', '.join(known)}")
