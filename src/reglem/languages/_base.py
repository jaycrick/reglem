"""The `Language` model shared by every language module and the registry.

Split out from `languages/__init__.py` to avoid a circular import: each
language module (e.g. `greek.py`) builds a `Language` instance at import
time, and the registry in `__init__.py` imports those modules -- so the
`Language` type itself can't live in `__init__.py` too.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

# Needed at runtime, not just for type-checking: pydantic resolves the
# `dict[str, VariantTable]` annotation below when building the model, which
# requires `VariantTable` to actually be in this module's namespace.
from reglem.variants import VariantTable  # noqa: TC001


class Language(BaseModel):
    """A named set of per-character spelling-variant tables for one language."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    variant_tables: dict[str, VariantTable]
