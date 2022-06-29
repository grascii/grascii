
# Changelog

## 0.4.1 - 2022-06-29

### Added

- Some classes and functions that are considered to be part of the public API are importable from the top-level `grascii`.

### Fixed

- Included `TV` in `grammar.STROKES`.

## 0.4.0 - 2022-06-27

### Added

- New `parser` module abstracts away Grascii parsing details.
- `grammar.CONSONANTS` and `grammar.VOWELS` constants.
- Experimental `outline` module with `Outline` class to infer directions of shorthand strokes.
- `GrasciiValidator` class to quickly validate, but not interpret, Grascii strings.
- `dictionaries` submodule to include dictionary source files.
- Dictionary build `--words` option to specify words file for spell checking.
- Dictionary build `--verbose` option to increase build output.
- New `docs` extra to specify doc building requirements.

### Changed

- Switched from `lark-parser` to new `lark` package.
- Boundaries can be retained during Grascii Interpretation creation.
- `grascii.lark` is compatible with LALR.
- An apostrophe is accepted to represent "a" or "an".
- Multiple semantic `grascii.lark` grammar changes (see [@7ebfd07](https://github.com/grascii/grascii/commit/7ebfd078dc6414ec1d4856641595c9f5221f25f5)).
- Dictionary build `--parse` option is now much faster.
- `ReverseSearcher` provides a more useful sorting of results.
- Updated preanniversary dictionary to [r00004](https://github.com/grascii/dictionaries/tree/r00004).

### Removed

- The `types` module has been removed. `Interpretation` is now defined in `grascii.parser`.
- The `utils` module has been removed.
- Dictionary source files are no longer stored in `dsrc`.
- The dictionary build `--spell` option has been removed. (Succeeded by `--words`)

### Fixed

- Removed `Y` from `grammar.HARD_CHARACTERS` and `grammar.ALPHABET`.
- Included `DV` in `grammar.STROKES`.
- Grascii contain searches do not match translations.
- Grascii searches match -ing(s) at the end of words.
- Grascii searches match a disjoiner at the end of words.
- Grascii searches do not match double aspirates (except at the end of a word) or double disjoiners.
- Fixed crash on interrupt during interactive interpretation selection.

## 0.3.0 - 2021-12-14

### Added

- New interactive search mode setting to select the dictionaries to search.

### Changed

- The search `-d/--dictionary` option can be specified multiple times to search
  more than one dictionary at a time.
- The config file `[Search] Dictionary` option now accepts a list of
  dictionaries.

## 0.2.2 - 2021-07-08

### Added

- Added the `-n/--count` option to `dictionary build` to enable the validation
  of expected word counts.

### Changed

- Word count validation for dictionary builds is no longer performed by
  default, but enabled with the `--count` option--helpful for phrase
  dictionaries.
- When the dictionary builder cannot determine an appropriate output file for
  an entry, it now prints an error and continues instead of crashing the build
  process.

### Fixed

- In dictionary builds, the incorrect number of words warning now properly
  behaves like a warning. The entry with the warning is now included in the
  build instead of being skipped.

## 0.2.1 - 2021-07-02

### Added

- `grascii.grammar.ALPHABET`: The set of valid characters in the Grascii language.

### Changed

- Grascii Search produces a better error message when given an invalid Grascii
  string.
- Grascii Dephrase produces a better error message when there are no results.

## 0.2.0 - 2021-06-25

First Release

### Added

- Grascii Search with Grascii, Interactive, Reverse, and Regex modes
- Grascii Dictionary build and installation tools
- Grascii Configuration file and management
- Built-in pre-anniversary dictionary [Status: Review]
- Experimental Grascii Dephrase tool
