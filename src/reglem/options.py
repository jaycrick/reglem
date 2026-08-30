"""Options controlling how a lemma pattern is built."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from reglem.errors import UnknownLanguageError
from reglem.languages import available_languages, get_language

DEFAULT_TERMINATORS = " ,.\xa0"
"""Space, comma, full stop, non-breaking space (U+00A0).

The non-breaking space matters for Anki fields specifically: it shows up in
field HTML (e.g. entity-derived) but is invisible in the Anki editor, so
omitting it here would cause silent, hard-to-diagnose match misses. It's
harmless to keep as a default for other targets too.
"""

DEFAULT_FIELD = "Greek"


class SearchOptions(BaseModel):
    """Immutable, validated configuration for `build_pattern` / `build_anki_search`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    language: str = "greek"
    with_macrons: bool = False
    strip_trailing_digits: bool = False
    terminators: str = DEFAULT_TERMINATORS
    field: str = DEFAULT_FIELD

    @field_validator("language")
    @classmethod
    def _known_language(cls, value: str) -> str:
        # pydantic only auto-wraps ValueError/TypeError/AssertionError raised
        # from a validator into its own ValidationError, so translate here
        # rather than let UnknownLanguageError escape raw.
        try:
            get_language(value)
        except UnknownLanguageError as exc:
            raise ValueError(str(exc)) from exc
        return value

    @field_validator("terminators")
    @classmethod
    def _terminators_not_empty(cls, value: str) -> str:
        if not value:
            msg = "terminators must not be empty"
            raise ValueError(msg)
        return value

    @field_validator("field")
    @classmethod
    def _field_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "field must not be blank"
            raise ValueError(msg)
        if "\n" in value or "\r" in value:
            msg = "field must not contain a newline"
            raise ValueError(msg)
        return value

    @property
    def known_languages(self) -> tuple[str, ...]:
        """Convenience passthrough for callers building error/help text."""
        return available_languages()
