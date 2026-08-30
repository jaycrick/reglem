"""Command-line entry point for reglem.

Usage
-----
    reglem lemmas.txt
    cat lemmas.txt | reglem -
    reglem -w lemma-one -w "lemma two" --macrons
    reglem lemmas.txt --raw --terminators ",;"
    reglem --list-languages
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reglem import __version__
from reglem.anki import build_anki_search
from reglem.build import build_pattern
from reglem.errors import ReglemError
from reglem.languages import available_languages
from reglem.options import DEFAULT_FIELD, DEFAULT_TERMINATORS, SearchOptions


def build_parser() -> argparse.ArgumentParser:
    """Build the `reglem` argument parser."""
    parser = argparse.ArgumentParser(
        prog="reglem",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="file of lemmas, one per line ('#' comments and blank lines skipped); "
        "'-' or omitted reads stdin",
    )
    parser.add_argument(
        "-w",
        "--word",
        action="append",
        dest="words",
        metavar="LEMMA",
        help="a lemma to include; repeatable. Overrides path/stdin when given.",
    )
    parser.add_argument(
        "-f",
        "--field",
        default=DEFAULT_FIELD,
        help=f"Anki field to match against (default: {DEFAULT_FIELD!r})",
    )
    parser.add_argument(
        "--language",
        default="greek",
        help="language whose spelling-variant tables to use (default: greek)",
    )
    parser.add_argument(
        "--macrons",
        action="store_true",
        help="expand ambiguous-length vowels into macron alternatives (language-dependent)",
    )
    parser.add_argument(
        "--strip-trailing-digits",
        action="store_true",
        help="strip a trailing homograph digit (e.g. 'lead2') from each lemma before matching",
    )
    parser.add_argument(
        "--terminators",
        default=DEFAULT_TERMINATORS,
        help=f"characters (besides end-of-field) that may follow a matched lemma "
        f"(default: {DEFAULT_TERMINATORS!r})",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="print the bare regex pattern instead of a quoted Anki search string",
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="print known language names and exit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"reglem {__version__}",
    )
    return parser


def _read_lemmas(path: str | None, words: list[str] | None) -> list[str]:
    """Resolve lemmas from `-w` words, a file path, or stdin, in that precedence order."""
    if words:
        return list(words)

    if path is None or path == "-":
        lines = sys.stdin.readlines()
    else:
        lines = Path(path).read_text(encoding="utf-8").splitlines()

    lemmas: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lemmas.append(line)
    return lemmas


def main(argv: list[str] | None = None) -> int:
    """Run the `reglem` CLI. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_languages:
        for name in available_languages():
            print(name)
        return 0

    try:
        lemmas = _read_lemmas(args.path, args.words)
        options = SearchOptions(
            language=args.language,
            with_macrons=args.macrons,
            strip_trailing_digits=args.strip_trailing_digits,
            terminators=args.terminators,
            field=args.field,
        )
        result = (
            build_pattern(lemmas, options) if args.raw else build_anki_search(lemmas, options)
        )
    except (ReglemError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
