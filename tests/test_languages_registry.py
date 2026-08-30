from __future__ import annotations

import pytest

from reglem.errors import UnknownLanguageError
from reglem.languages import available_languages, get_language


def test_available_languages_includes_greek() -> None:
    assert "greek" in available_languages()


def test_get_language_returns_greek() -> None:
    language = get_language("greek")
    assert language.name == "greek"
    assert "macrons" in language.variant_tables


def test_get_language_unknown_raises_with_known_list() -> None:
    with pytest.raises(UnknownLanguageError) as exc_info:
        get_language("klingon")
    assert "greek" in str(exc_info.value)
