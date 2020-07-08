
# Grascii Search

The core feature of the Grascii suite is search.

Fundamentally, it allows one to enter a Grascii string as a query and 
search the Grascii dictionary for potential translations.

## Usage

`python grascii.py search [-h] (-g GRASCII | -r REGEX | -i) [-u {0,1,2}] [-v]`

`-h`, `--help`

Print a help message and exit.

`g`, `--grascii`

Set a Grascii String to use as a query.

`r`, `--regex`

Set a regular expression to use as a query.

`-i`, `--interactive`

Run searches in interactive mode. This is the recommended mode for general
use, as `--grascii` and `--regex` may require using shell escape sequences.

`-u`, `--uncertainty`

Set the uncertainty level of a Grascii string. 2 represents the greatest
uncertainty. For more information....

`-v`, `--verbose`

Enable verbose output.

### Suggestions

* use interactive mode
* `--regex` is intended for advanced users and advanced searches. Regexes 
can be difficult to deal with manually, and most users should use 
`--grascii` instead as it handles many of these complications. Using
`--regex` is effectively equivalent to
`$ grep [regex] dict/*`
