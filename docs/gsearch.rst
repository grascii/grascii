
Search
######

The core feature of the Grascii suite is search.

Fundamentally, it allows one to enter a Grascii string as a query and
search the Grascii dictionary for potential translations.

Usage
*****

.. object:: grascii search [-h] (-g GRASCII | -e REGEXP | -r REVERSE | -i) [-u {0,1,2}] [-s {match,start,contain}] [-a {discard,retain,strict}] [-p {discard,retain,strict}] [-j {discard,retain,strict}] [-n {best,all}] [-f] [-d DICTIONARIES] [--show-dictionary] [--no-sort]

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

``best``: Only search using the :ref:`canonical interpretation <canonical-interpretation>`.

``all``: Search using all possible interpretations.

.. option:: -f, --fix-first

Apply an uncertainty of 0 to the first stroke.

.. option:: -d <dictionary>, --dictionary <dictionary>

Specify which dictionary to search. This option may be used more than once to
search multiple dictionaries at the same time.

``<dictionary>`` is either a path to the output directory of a built
dictionary, or a colon followed by the name of an installed dictionary.
Ex: ``:preanniversary``.

.. option:: --show-dictionary

Show the dictionary containing each search result.

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

Algorithm
*********

The Grascii search procedure is as follows:

1. Convert the Grascii string to uppercase.

2. Split the Grascii string into strokes, sets of annotations on those strokes,
   and other symbols. Each possible way of splitting the string is an
   interpretation.

3. For each selected interpretation, construct a regular expression (regexp):

   a. Replace each stroke with a string of regexp alternatives among
      its equivalent forms and similar forms based on the uncertainty level. To
      learn how uncertainty is resolved, see :doc:`similarity`.

   b. For each stroke, insert characters into the regexp to match possible
      annotations according to the annotation mode.

   c. Insert characters around/between strokes to match possible aspirates
      according to the aspirate mode.

   d. Insert characters between strokes to match possible disjoiners according
      to the disjoiner mode.

4. Determine the set of starting letters: the first alphabetic characters that
   may be matched by any constructed regexp.

5. Open the dictionary files corresponding to the starting letters and search
   each line with each regexp.

6. Return a result for every line that matches a regexp.
