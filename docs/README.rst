
Grascii
#######

About the Project
*****************

Grascii is a language used to represent Gregg Shorthand forms using the ASCII
character set (characters found on a standard keyboard). The Grascii Project,
also referred to as Grascii, encompasses the set of tools and resources
accompanying the language that facilitate the reading, writing, and study of
Gregg Shorthand at all levels.

Useful Links
************

- `Full Documentation (readthedocs) <https://grascii.readthedocs.io>`_
- `Additional Dictionaries <https://github.com/grascii/dictionaries>`_
- `grascii-gui (graphical interface for Grascii Search) <https://github.com/grascii/gui>`_

Made With
*********
- Python 3

Getting Started
***************

Prerequisites
=============

- Python 3.7+

Installation
============

Install the package::

  $ python -m pip install grascii[interactive]

Note: We recommend the interactive extra for the majority of users. You may
omit the interactive extra when using the package as a library to
reduce dependencies. Also see `grascii-gui <https://github.com/grascii/gui>`_
for a graphical interface for Grascii Search.


Verify the installation::

  $ grascii --help

If the command fails, your PATH may not contain the location of Python scripts.

You can also try::

  $ python -m grascii --help

Grascii Language
****************

The Grascii Language aims to be straightforward for those who are familiar with
Gregg Shorthand. That is, Grascii represents most strokes with the letters that
match their sounds. For example, the word ``Cross`` is written as ``KROS``.

For a more detailed overview of the language, see `language
<https://grascii.readthedocs.io/en/latest/language.html>`_.

Grascii Search
**************

Grascii Search is the headline tool of the Grascii Project. It provides many
useful options for searching Grascii Dictionaries (reverse Gregg Shorthand
dictionaries).

Motivation
==========

The existence of shorthand dictionaries have aided the conversion of longhand
to shorthand. However, the reverse has remained a challenge since the
inception of Gregg Shorthand. Grascii Search solves this problem by allowing
users to identify the longhand corresponding to a shorthand form by performing
a search based on its Grascii representation.

Basic Usage
===========

Ex.::

    $ grascii search -g AB
    AB About
    A|B Agreeable
    Results: 2

Uncertainty
===========

Occassionally, a stroke is mistaken for one of similar form. Thus, Grascii
Search provides levels of uncertainty.

Ex.::

    $ grascii search -g FND -u1
    FND Found
    FND Fund
    FTH Forth
    FTH Further
    SND Sound
    Results: 5

The ND stroke could also be an under TH or an MT/MD. The search accounts for
these possibilities with Forth and Further. F is also close to S or V,
resulting in Sound.

Interactive Mode
================

For repeated usage, we recommend running Grascii Search in interactive mode.
For more complex queries, interactive mode removes the need of using escape
sequences on the command line.

::

    $ grascii search -i

Note: Requires the interactive extra

More Options
============

For more options, see `search <https://grascii.readthedocs.io/en/latest/gsearch.html>`_.

Grascii Dictionary
******************

Grascii comes with a dictionary based on the 1916 Gregg Shorthand Dictionary.

More dictionaries for other versions of Gregg and dictionaries including
phrases are available for installation at the `Grascii Dictionaries repository
<https://github.com/grascii/dictionaries>`_.

You can also write, build, and install your own custom dictionaries.

For more information, see `dictionary <https://grascii.readthedocs.io/en/latest/dictionary.html>`_.

Grascii Dephrase (Experimental)
*******************************

Grascii includes an experimental phrase parsing module.

It attempts to give the phrase for the most common phrase constructions in
Gregg Shorthand and provide suggestions for never before seen phrases::

    $ python -m grascii.dephrase AVNBA
    I HAVE NOT BEEN ABLE

Documentation
*************

Documentation is available on `Read the Docs <https://grascii.readthedocs.io>`_.

Contributing
************

Contributions of any kind are welcome and appreciated. You can contribute by:

- Reporting bugs or unexpected behavior
- Fixing bugs and solving issues
- Helping implement new features
- Editing documentation for correctness, completeness, and clarity
- Sharing thoughts and suggestions to improve the Grascii Language

Dictionary
==========

If you find an error in any of the dictionaries, please open an issue or pull
request at the `dictionaries repository <https://github.com/grascii/dictionaries>`_.

Contributions to the dictionaries repository are also welcome to correct errors
and create more dictionaries.

License
*******

This project is under the `MIT License <https://github.com/grascii/grascii/blob/master/LICENSE>`_.
