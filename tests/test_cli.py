from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pytest

from reglem.cli import main

if TYPE_CHECKING:
    from pathlib import Path


def test_words_flag(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-w", "cat", "-w", "dog"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.startswith('"Greek:re:^(')


def test_raw_flag(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-w", "cat", "--raw"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.startswith("^(cat)")


def test_reads_from_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    lemma_file = tmp_path / "lemmas.txt"
    lemma_file.write_text("cat\n# a comment\n\ndog\n", encoding="utf-8")
    exit_code = main([str(lemma_file)])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "cat" in out
    assert "dog" in out


def test_reads_from_stdin(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("cat\ndog\n"))
    exit_code = main(["-"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "cat" in out


def test_reads_from_stdin_when_no_path_given(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("cat\n"))
    exit_code = main([])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "cat" in out


def test_custom_field(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-w", "cat", "-f", "Front"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.startswith('"Front:re:')


def test_macrons_flag(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-w", "ἀγαθός", "--macrons", "--raw"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "(?:" in out


def test_strip_trailing_digits_flag(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-w", "word2", "--strip-trailing-digits", "--raw"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "word2" not in out
    assert "word" in out


def test_custom_terminators(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-w", "cat", "--terminators", ";", "--raw"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert ";" in out


def test_list_languages(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["--list-languages"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "greek" in out


def test_version() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0


def test_empty_input_is_an_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    exit_code = main(["-"])
    err = capsys.readouterr().err
    assert exit_code == 1
    assert "error:" in err


def test_bad_language_is_an_error(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-w", "cat", "--language", "klingon"])
    err = capsys.readouterr().err
    assert exit_code == 1
    assert "error:" in err


def test_missing_file_is_an_error(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["/no/such/file.txt"])
    err = capsys.readouterr().err
    assert exit_code == 1
    assert "error:" in err
