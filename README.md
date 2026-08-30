# reglem

Turn list of word lemmas into one anchored regex alternation.
Optional per-language spelling variants (Greek macrons, for now).
Optional Anki `field:re:...` search-string wrapper.

Greek only today.
Language layer built so more languages drop in later without touching core.

## Why

Building `re:` search for Anki (or any regex-search tool) by hand from a word list is fiddly:
prefix leaks (`ox` matching `oxen`),
Rust `regex` crate has no lookahead so `(?=...)` breaks in Anki,
spelling variants (accents, long-vowel marks) multiply the work.
This package does that once, correctly, tested.

## Install

```bash
uv add reglem
# or
pip install reglem
```

## Quickstart — library

```python
from reglem import build_anki_search, build_pattern, SearchOptions

# bare regex
build_pattern(["cat", "dog"])
# '^(dog|cat)([ ,. ]|$)'

# Anki search string
build_anki_search(["ὁ", "καί", "ἀγαθός"], SearchOptions(field="Greek", with_macrons=True))
# '"Greek:re:^(...)([ ,. ]|$)"'
```

Paste that string into Anki's Browse search bar.
It matches notes whose field *starts* with one of the given lemmas,
followed by space, comma, period, or end of field.

## Quickstart — CLI

```bash
reglem lemmas.txt                     # Anki search string, one lemma per line in file
cat lemmas.txt | reglem -             # same, from stdin
reglem -w ὁ -w καί -w ἀγαθός --macrons
reglem lemmas.txt --raw               # bare regex, no Anki wrapper
reglem --list-languages
```

`lemmas.txt`: one lemma per line, blank lines and `#` comments skipped.

## Flags

| flag | default | does |
|---|---|---|
| `-w/--word LEMMA` | — | add one lemma; repeatable; overrides file/stdin |
| `-f/--field NAME` | `Greek` | Anki field name in output search string |
| `--macrons` | off | expand ambiguous-length vowels into macron alternatives |
| `--strip-trailing-digits` | off | strip trailing homograph digit (`lead2` → `lead`) before matching |
| `--terminators CHARS` | `" ,. "` (space, comma, period, NBSP) | chars allowed right after a matched lemma |
| `--raw` | off | print bare regex, skip the `"field:re:..."` wrapper |
| `--language NAME` | `greek` | which variant tables to use for `--macrons` |
| `--list-languages` | — | print known language names, exit |

## Why prefix-anchored, no lookahead

Anki's `re:` search uses the Rust `regex` crate (no lookaround support),
and field regexes are unanchored by default.
So a naive `word(?=[ ,])` breaks two ways:
it's invalid syntax in Anki,
and without `^` it'd match `word` inside `password` too.
reglem builds `^(alt1|alt2|...)([terminators]|$)` instead —
one alternation, explicit anchor, ordinary terminator class.

## Greek macrons

See `docs/greek.md` for the full story —
why unmarked Greek text is vowel-length-ambiguous,
and how the macron expansion table is built.

## Development

```bash
uv sync
uv run pytest              # coverage gate: 95%
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run pre-commit run --all-files
```

## Publish

Tag `vX.Y.Z`, push tag.
CI builds, checks with `twine`, publishes via PyPI Trusted Publishing (OIDC) —
no stored token.

## License

MIT.
