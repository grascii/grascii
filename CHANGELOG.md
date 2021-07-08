
# Changelog

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
