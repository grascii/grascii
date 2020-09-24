
Dictionary
##########

Grascii comes with the Grascii forms of all words in the 1916 Gregg 
Shorthand Dictionary.

These mappings of Grascii strings to their corresponding words are
contained in a series of text files in the ``dsrc`` directory.

These dictionary source files are compiled into the dictionary
format that Grascii Search expects using ``grascii dictionary build``.

Dictionary Source File Layout
*****************************

Basic Entry
===========

Each entry in a dictionary source file is contained on its own line in
the following scheme:

``[Grascii String] [Translation]``

There can be any amount of whitespace surrounding the ``Grascii String`` and 
its ``Translation``.

Both ``Grascii String`` and ``Translation`` are case-insensitive.

Blank Lines
===========

Blank Lines are ignored

Comments
========

Lines whose first non-whitespace character is a `#` are ignored.

::

  # This is a comment

Uncertainties
=============

An entry preceded by a `?` will produce a warning during the build phase.

::

  # I am not sure if that is an A or an E
  ? ken keen

Source File Conventions
***********************

While there is a reasonable amount of freedom in the dictionary source file
format, a number of conventions were followed in writing the source files
for the dictionary. It is recommended for new files to also follow these
conventions.

* Within source files, entries are placed alphabetically by translation.
* When adding entries from a Gregg Shorthand dictionary, a comment denotes
  the corresponding page and column number in the dictionary. Entries in
  different pages/columns are separated by a blank line.
* Comments should have `#` as the first character of the line, and there
  should be a single space following the `#` before the first word of the 
  comment.
* If applicable, `?` should be the first character of the line, and there
  should be a single space following the `?` before the Grascii string.
* There should be no excess whitespace before or after the Grascii string
  and its translation. There should be a single space between the Grascii
  string and its translation.
* Grascii Strings and translations are written in lower case. The case will
  be adjusted during a build.
* Entries taken from a dictionary are written in Grascii as presented. That
  is, annotations are not applied unless explicitly displayed. By extension,
  entries should be written in the simplest form possible. Use areannotations only if
  necessary to distinguish the word from another. This helps generalize the
  dictionary for better search results.
* The direction annotations on S and TH are only included if the 
  character is in the direction contrary to its standard joining based on the
  characters around it.
* Words which include two stokes next to each other that make up a blend, 
  but are not blended, are written with a barrier between them `-`.
  While these are stripped in the standard build mode, this information is
  useful for other build types that may be valuable in the future.
* When writing a stroke that has more than one sound, Use the version that
  matches the sound it makes in the word.

The Build Process
*****************

Input and Output
================

The ``build`` routine takes a set of dictionary source files and outputs a
set of text files in the format expected by Grascii Search.

It outputs files of the form: `A`, `B`, `C`, `D`, etc. where each file
contains entries whose first alphabetic character in its Grascii form
matches the name of the file in which it is contained.

This light indexing reduces the number of entries that Grascii Search must
check.

Output File Format
==================

Entries
-------

Each entry in an output file is contained on its own line in the following
scheme:

``[GRASCII STRING] [Translation]```

Where ``GRASCII STRING`` is in all uppercase and ``Translation``'s first letter
is uppercase, and the rest of the string is lowercase.

There is no whitespace preceding ``GRASCII STRING`` or following ``Translation``
. There is exactly one space between them.

Blank Lines
-----------

Output files contain no blank lines.

Building
********

Usage 
=====

.. describe:: grascii dictionary build [-h] [-o OUTPUT] [-c] [-p] [-s] infiles [infiles ...]

.. option:: <infiles>

  The dictionary source files to compile.

.. option:: -h, --help

  Print a help message and exit.

.. option:: -o, --output

  Set the directory in which compiled files will be output.

.. option:: -c, --clean

  Remove all files in the output directory before compiling.

.. option:: -p, --parse

  During the build, all Grascii Strings will be attempted to be parsed to
  verify that it is a valid Grascii string. If the parse fails, an error
  will be reported, and the corresponding entry will not be included in
  the output.

.. option:: -s, --spell

  During the build, all translations will be looked up in a dictionary to
  check the spelling/existence of the word. If the word is not found, a
  warning will be reported, but the corresponding entry will still be 
  included in the output.

.. option:: -k, --check-only

  Only check the input. No output is generated.
  

.. Talk about word list and dictionaries.

Warnings and Errors
===================

During a build, you may encounter warnings and errors.

Warnings indicate that something unusual has been found with an entry. 
Entries that receive a warning may warrant special attention/review.
However, these entries will still be included in the final output.

Errors indicate that there was a failure when processing an entry. Entries
that receive an error will not be included in the final output.

Possible Warnings
-----------------

Uncertainty
^^^^^^^^^^^

Reports that an entry beginning with `?` has been found.

Too many tokens
^^^^^^^^^^^^^^^

Reports that too many tokens have been found in a source entry. If there are
more than 2 words on a line, the first will be interpreted as a Grascii
string, and the second as its translation. The following words will be
discarded.

Spelling
^^^^^^^^

When the :option:`--spell` flag is set, denotes that an entry's translation
has not been found in a dictionary.

Possible Errors
---------------

Too few tokens
^^^^^^^^^^^^^^

Reports that there is only one word on a line. A translation may be 
missing.

Invalid Grascii
^^^^^^^^^^^^^^^

When the :option:`--parse` flag is set, denotes that the first word is not a valid
Grascii string.

Suggestions
-----------

Most of the time, it is acceptable to run the build without the :option:`--parse`
or :option:`--spell` flags for a quick build.

The overhead of :option:`--spell` is reasonable, but enabling :option:`--parse` will greatly
increase build times. However, it is recommended to run a build with these
options and resolving the issues before releasing the dictionary publicly.

Working with Custom Dictionaries
********************************

It is possible to write your own dictionaries to use with the Grascii 
tool suite.

1. Make a directory to store your dictionary source files.

::

  $ mkdir mysrc

2. Add source files to this directory that follow the dictionary source file 
   format.

3. Build your dictionary.

::

   $ grascii dictionary build mysrc/*.txt -o mydict

.. note::

  At this point, your dictionary is usable.

  ::
    
    $ grascii search --dictionary ./mydict/ -g AB

  If you would like to install the dictionary so you do not have to
  keep track of the path, continue with step 4.

4. Install the dictionary.

::

  $ grascii dictionary install --name custom ./mydict/
  

5. Verify the installation.

::

  $ grascii dictionary list
  Built-in Dictionaries:
  preanniversary

  Installed Dictionaries:
  custom

6. Enjoy.

::

  $ grascii search --dictionary :custom -g AB


Uninstalling
============

Simply run::

  $ grascii dictionary uninstall custom


