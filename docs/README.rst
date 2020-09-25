
Grascii
#######

About the Project
*****************

Grascii is a language designed to represent Gregg Shorthand
forms using the ASCII character set. It also encompasses the set of tools
using the language to facillitate the study of Gregg Shorthand.

Made With
*********
- Python 3

Getting Started
***************

Prerequisites
=============

- Python 3.6+
- Lark

::

  $ pip install lark-parser --upgrade

Installation
============

To use Grascii pre-release, clone the repository.

::

  $ git clone https://github.com/chanicpanic/grascii

From the root of the repository, run::

  $ pip install -e .

Updating
========

From the root of the repository, run::

  $ git pull origin master

Grascii Language
****************

The Grascii Language is designed to be straightforward for those
who are familiar with Gregg Shorthand. That is, most strokes are
represented by the letters that match their sounds. For example,
the word ``Cross`` would be written as ``KROS``.

For a more detailed overview of the language, see :doc:`language`.

Purpose
*******

When studying shorthand, a student may come across a form which is 
unfamiliar, new, or represents an unknown word. Traditionally, a student
could refer to the dictionary which maps English words to their 
corresponding shorthand forms. However, this technique can be tricky and
inefficient as the student must guess the word in English to
compare to the unknown form. This is likened to the process of using a
dictionary to determine the spelling of a word. This is where the main tool
comes in: Grascii Search.

Grascii Search 
**************

The Grascii forms of all entries of the 1916 Gregg Shorthand Dictionary
have been collected. The Grascii Search Feature allows a user to query with
a Grascii string to search the Grascii dictionary for similar matches
which tell what corresponding English word goes with the form.

Basic Usage
===========

Ex.::

    $ grascii search -g AB
    AB About
    A|B Agreeable
    Results: 2

Uncertainty
===========

It is acknowledged that when looking at a form, a stroke may be mistaken
for one of similar form whether by proportion error etc. Thus, Grascii
Search provides levels of uncertainty.

Ex.::

    $ grascii search -g FND -u1
    FND Found
    FND Fund
    FTH Forth
    FTH Further
    SND Sound
    Results: 5

The ND stroke could also potentially be an under TH or an MT/MD. The search
accounts for these possibilities. F is also close to S or V.

Interactive Mode
================

For repeated usage, it is recommended to run Grascii Search in interactive
mode. For more complex queries, it removes the need of using escape 
sequences on the command line.

::

    $ grascii search -i

More Options
============

For more options, see :doc:`gsearch`.

Grascii Dictionary
******************

Grascii comes with a dictionary for the 1916 version of the Gregg
Shorthand Dictionary. 

There is also the ability to build and install your own custom 
dictionaries.

For more information, see :doc:`dictionary`.

Grascii Dephrase (Experimental)
*******************************

Grascii includes an experimental phrase parsing module.

It is designed to give the phrase for the most common phrase constructions
in Gregg Shorthand as well as to provide suggestions for never before
seen phrases.::

    $ python -m grascii.dephrase AVNBA
    I HAVE NOT BEEN ABLE
    
Documentation
*************

Documentation is available on `Read the Docs <https://grascii.readthedocs.io>`_.

Issues
******

The Grascii Dictionary is in the process of being reviewed for accuracy. 
If you find any incorrect entries, please let me know. 

If you discover any issues with the program or have any
suggestions, open an issue or pull request.

Contributing
************

You are welcome to contribute and make pull requests.

Dictionary
==========

It would be great to have help adding more words to the dictionary
and making dictionaries for other versions of Gregg Shorthand.

If you would like to help with this, please read the dictionary conventions in
:doc:`dictionary`.

License
*******

This project is under the MIT License.

Acknowledgements
****************

Many thanks to the developers of `Lark <https://github.com/lark-parser/lark>`_, `Questionary <https://github.com/tmbo/questionary>`_, and `appdirs <https://github.com/ActiveState/appdirs>`_.
