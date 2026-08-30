from __future__ import annotations

import pytest
from pydantic import ValidationError

from reglem.options import SearchOptions


def test_defaults() -> None:
    options = SearchOptions()
    assert options.language == "greek"
    assert options.with_macrons is False
    assert options.strip_trailing_digits is False
    assert options.field == "Greek"


def test_frozen() -> None:
    options = SearchOptions()
    with pytest.raises(ValidationError):
        options.field = "Other"  # type: ignore[misc]


def test_extra_forbidden() -> None:
    with pytest.raises(ValidationError):
        SearchOptions(bogus="x")  # type: ignore[call-arg]


def test_unknown_language_rejected() -> None:
    with pytest.raises(ValidationError):
        SearchOptions(language="klingon")


def test_blank_field_rejected() -> None:
    with pytest.raises(ValidationError):
        SearchOptions(field="   ")


def test_field_with_newline_rejected() -> None:
    with pytest.raises(ValidationError):
        SearchOptions(field="Greek\nInjected")


def test_empty_terminators_rejected() -> None:
    with pytest.raises(ValidationError):
        SearchOptions(terminators="")


def test_known_languages_property() -> None:
    assert "greek" in SearchOptions().known_languages
