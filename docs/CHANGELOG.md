# Changelog

## Unreleased

## 0.6.1 - 2024-12-27

### Changed

- Updated similarity graph to include edges connecting circle diphthongs

## 0.6.0 - 2024-07-01

### Added

- Dictionary build `--no-output` option
- `DictionaryOutputOptions` class for `DictionaryBuilder.build`
- `BuildSummary` class for results of `DictionaryBuilder.build`
- Experimental pipelines for dictionary builds
- `ignore_case` option to `GrasciiValidator`
- `-q` and `--quiet` options for `grascii dictionary build`.

### Changed

- `Searcher.__init__` does not handle `DictionaryNotFound` exceptions
- `grascii search` prints an error if a dictionary cannot be found
- Many `DictionaryBuilder.__init__` options moved to `DictionaryBuilder.build`
  or were removed
- `DictionaryBuilder.build` takes `infiles` and `output` arguments and returns
  a `BuildSummary`
- Updated the `grascii_standard` metric to incorporate the position and length
  of the matched grascii
- Migrated to `platformdirs`: The location for the configuration file on MacOS
  changed from `~/Library/Preferences` to `~/Library/Application Support`
- Updated preanniversary dictionary to [2024.06.14](https://github.com/grascii/dictionaries/tree/2024.06.14).

### Removed

- `grascii.grammars.get_grammar`: Use
  `Lark.open_from_package("grascii.grammars", grammar_name)` instead.
- `BuildDirectory` configuration file option
- Dictionary build `--check-only` option: Use `--no-output` instead
- `grascii.dictionary.build.build` function: Use `DictionaryBuilder.build` instead

### Fixed

- Regex metacharacters in reverse search inputs are escaped

## 0.5.0 - 2022-08-12

### Added

- `SearchResult` class to group together relevant data from matches.
- `Searcher.sorted_search` to obtain a list of sorted `SearchResult`s.
- `grascii.dictionary.common` module to contain `DictionaryException`s and utility functions.
- `Dictionary` class to work with grascii dictionaries.
- `config.get_default_config` to get the text of the default configuration file.
- `-V` and `--version` command line options.
- `InvalidGrascii` exception which is produced by a parser.
- `--no-sort` option for `grascii search`.
- `grascii.parser.get_grascii_regex_str()` to get a string that can be compiled into
  a regular expression that recognizes grascii strings.

### Changed

- `Searcher.search` no longer sorts results.
- `grascii.dictionary.list`: `get_installed` and `get_built_ins` return a collection of
installed dictionary names (prefixed with `:`).
- `grascii.dictionary.install.install_dict` renamed to `install_dictionary` and accepts more options.
- `grascii.dictionary.uninstall.uninstall_dict` renamed to `uninstall_dictionary` and accepts more options.
- `DICTIONARY_PATH` renamed to `INSTALLATION_DIR`.
- Using builtin `sorted` function speeds up general grascii searches.
- `GrasciiParser.interpret` returns an iterator instead of a list.
- Updated preanniversary dictionary to [2022.07.26](https://github.com/grascii/dictionaries/tree/2022.07.26).

### Removed

- Dropped Python 3.6 support.
- `grascii.dictionary.get_dict_file`: Use `grascii.dictionary.Dictionary.open` instead.
- `GrasciiValidator.__init__` `use_cache` option

### Fixed

- Typing issues with searchers and metrics.
- Errors when passing a grascii string with boundaries or disjoiners to the aggressive dephraser.

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
