# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Core:
  `build_pattern` / `build_anki_search`,
  lemma normalization,
  per-language spelling-variant expansion,
  Greek macron table.
- Core:
  per-lemma terminator exceptions (`Language.excluded_terminators`),
  and a Greek exception denying space/NBSP right after any of the 19
  definite-article forms, so `ὁ` no longer false-matches entries like
  `ὁ σοφός, -ή, -όν` or `ἡ ἀρίστη`.
- `/` (slash) added to `DEFAULT_TERMINATORS`,
  so slash-separated citations (`ὁ/ἡ/τό`, `ἀγαθός/ή/όν`) still match.
- CLI:
  `reglem` console script
  (file / stdin / `-w` input, `--macrons`, `--raw`, `--list-languages`).
- Packaging:
  strict ruff + basedpyright,
  pytest with coverage gate,
  pre-commit,
  CI,
  PyPI Trusted Publishing workflow.

### Changed

- A Greek definite-article lemma (`ὁ`, `ἡ`, `τό`, and the rest of the
  paradigm) followed by a non-breaking space no longer matches —
  NBSP is now excluded the same as a plain space for these lemmas.
