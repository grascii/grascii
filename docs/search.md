
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

## Implementation

The search procedure when given a Grascii query is as follows:

1. Convert the Grascii string to uppercase. Parse the Grascii string into
   tokens and sets of annotations on those tokens.

2. As the Grascii language is ambiguous, all possible parsings are
generated.

3. Choose an interpretation (parse).

For each interpretation a regular expression is constructed.

4. Each token is replaced with a string of regex alternatives among
its equivalent forms and similar forms based on the uncertainty level. To
learn how uncertainty is resolved, see similarity.md.

5. In standard mode, modifiers are preserved. Or all possible modifiers
for each token are built into the regex which may or may not occur.

6. A set of starting letters is tracked which are the first alphabetic
characters required to be accepted by any regex.

7. The dictionary files corresponding to these letters are opened and 
each line is searched with each regex.

8. Any lines that have a matching regex are returned.
