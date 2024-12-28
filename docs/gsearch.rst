
Search
######

The core feature of the Grascii suite is search.

Fundamentally, it allows one to enter a Grascii string as a query and
search the Grascii dictionary for potential translations.

Usage
*****

.. object:: grascii search [-h] (-g GRASCII | -e REGEXP | -r REVERSE | -i) [-u {0,1,2}] [-s {match,start,contain}] [-a {discard,retain,strict}] [-p {discard,retain,strict}] [-j {discard,retain,strict}] [-n {best,all}] [-f] [-d DICTIONARIES] [--no-sort]

.. option:: -h, --help

Print a help message and exit.

.. option:: -g <grascii>, --grascii <grascii>

Set a Grascii String to use as a query.

.. option:: -e <regexp>, --regexp <regexp>

Set a regular expression to use as a query.

.. option:: -r <word>, --reverse <word>

Search by word instead of Grascii.

.. option:: -i, --interactive

Run searches in interactive mode. This is the recommended mode for general
use, as :option:`--grascii` and :option:`--regexp` may require using shell escape sequences.

.. option:: -u {0, 1, 2}, --uncertainty {0, 1, 2}

Set the uncertainty level of a Grascii string. 2 represents the greatest
uncertainty. For a more in-depth explanation of uncertainty, see
:doc:`similarity`.

.. option:: -s {match, start, contain}, --search-mode {match, start, contain}

Set the type of search to perform.

``match``: Search for words that
closely match the input.

``start``; Search for words that start with the input.

``contain``; Search for words that contain the input.

.. option:: -a {discard, retain, strict}, --annotation-mode {discard, retain, strict}

Set how to handle Grascii annotations.

``discard``: Annotations are discarded. Search results may contain
annotations in any location.

``retain``: Annotations in the input must appear in search results. Other annotations may appear in the results.

``strict``: Annotations in the input must appear in search results. Other annotations may not appear in the results.

.. option:: -p {discard, retain, strict}, --aspirate-mode {discard, retain, strict}

Set how to handle Grascii aspirates.

``discard``: Aspirates are discarded. Search results may contain
aspirates in any location.

``retain``: Aspirates in the input must appear in search results. Other aspirates may appear in the results.

``strict``: Aspirates in the input must appear in search results. Other aspirates may not appear in the results.

.. option:: -j {discard, retain, strict}, --disjoiner-mode {discard, retain, strict}

Set how to handle Grascii disjoiners.

``discard``: Disjoiners are discarded. Search results may contain
disjoiners in any location.

``retain``: Disjoiners in the input must appear in search results. Other disjoiners may appear in the results.

``strict``: Disjoiners in the input must appear in search results. Other disjoiners may not appear in the results.

.. option:: -n {best, all}, --interpretation {best, all}

How to handle ambiguous Grascii strings.

``best``: Only search with the best interpretation.

``all``: Search with all interpretations.

.. option:: -f, --fix-first

Apply an uncertainty of 0 to the first stroke.

.. option:: -d <dictionary>, --dictionary <dictionary>

Specify which dictionary to search. This option may be used more than once to
search multiple dictionaries at the same time.

``<dictionary>`` is either a path to the output directory of a built
dictionary, or a colon followed by the name of an installed dictionary.
Ex: ``:preanniversary``.

.. option:: --no-sort

Do not sort the search results.

Suggestions
===========

* use interactive mode
* :option:`--regexp` is intended for advanced users and advanced searches. Regexes
  can be difficult to deal with manually, and most users should use
  :option:`--grascii` instead as it handles many of these complications. Using
  :option:`--regexp` is effectively equivalent to
  ``$ grep [regexp] dict/*``

Implementation
**************

The search procedure when given a Grascii query is as follows:

1. Convert the Grascii string to uppercase. Parse the Grascii string into
   tokens and sets of annotations on those tokens.
2. As the Grascii language is ambiguous, all possible parsings are
   generated.
3. Choose an interpretation (parse).
   For each interpretation a regular expression is constructed.
4. Each token is replaced with a string of regexp alternatives among
   its equivalent forms and similar forms based on the uncertainty level. To
   learn how uncertainty is resolved, see similarity.md.
5. In standard mode, modifiers are preserved. Or all possible modifiers
   for each token are built into the regexp which may or may not occur.
6. A set of starting letters is tracked which are the first alphabetic
   characters required to be accepted by any regexp.
7. The dictionary files corresponding to these letters are opened and
   each line is searched with each regexp.
8. Any lines that have a matching regexp are returned.
