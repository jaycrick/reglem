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
- CLI:
  `reglem` console script
  (file / stdin / `-w` input, `--macrons`, `--raw`, `--list-languages`).
- Packaging:
  strict ruff + basedpyright,
  pytest with coverage gate,
  pre-commit,
  CI,
  PyPI Trusted Publishing workflow.
