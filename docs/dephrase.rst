
Dephrase
########

Gregg Shorthand includes phrases in which a single shorthand form may represent
several words. Readers unfamiliar with a phrase or lacking context may struggle
to determine what words the form represents or not even realize that the form
is a phrase at all. Grascii provides two tools to tackle this problem:

1. **Search**: The Grascii dictionaries contain thousands of common and not so
   common phrases.
2. **Dephrase**: When search does not provide results, dephrase is ready to fill
   the gap. Dephrase matches a Grascii string against several Gregg shorthand
   phrase patterns in order to provide possible longhand translations of a
   shorthand form. It is capable of deciphering common and novel phrases.

.. note::

   The currently implemented phrase patterns and vocabulary are based on the
   Preanniversary edition of Gregg Shorthand, but many patterns may also apply
   to other editions.

Standard Dephrasing
===================

The standard dephrasing uses a predefined set of phrase vocabulary.

::

  $ grascii dephrase USHSE
  YOU SHALL SEE
  YOU SHIP SEE
  WISH [TO] SEE

The dephraser provides three possibilities with the first and the last seeming
most plausible.

The brackets around the "TO" in the last result indicate that the word "TO"
does not correspond to any strokes in the Grascii string "USHSE". Instead, it
is a word often omitted in phrases.

Aggressive Dephrasing
=====================

Sometimes the standard phrase vocabulary is inadequate. Aggressive dephrasing
integrates Grascii search to expand the possibilities.

Consider "GTH" which does not give any results with standard dephrasing:

::

  $ grascii dephrase GTH
  No results
  You may try again with --aggressive to consider more possibilities.

Now with aggressive mode:

::

  $ grascii dephrase GTH --aggressive
  (GO|GOOD|GRAND|A GALLON) [TO] (THE|THANK|THEIR|THERE|THING|THINK|A THOUSAND)
  (GO|GOOD|GRAND|A GALLON) [TO] THEY
  (GO|GOOD|GRAND|A GALLON) [TO] THANK
  (GO|GOOD|GRAND|A GALLON) (THE|THANK|THEIR|THERE|THING|THINK|A THOUSAND)
  (GO|GOOD|GRAND|A GALLON) THEY
  (GO|GOOD|GRAND|A GALLON) THANK

The words in parentheses delimited by pipes represent the results of Grascii
search. That is, "G" in "GTH" could represent "GO", "GOOD", "GRAND", or "A
GALLON". Similarly, "TH" has its own set of possibilities.

From these results, some of the most plausible phrases are "GO THANK", "GO
THERE", and "GOOD THING".

.. note::

   At this time, the dictionaries and parameters aggressive dephrase uses for
   searches are the defaults based on :doc:`configuration`.

Usage
=====

.. object:: grascii dephrase [-h] [-a] [--ignore-limit] phrase

.. option:: <phrase>

A Grascii phrase to decipher.

.. option:: -h, --help

Print a help message and exit.

.. option:: -a, --aggressive

Perform a more aggressive dephrasing using Grascii search.

.. option:: --ignore-limit

Ignore the 8-character phrase limit.

By default, if ``phrase`` is greater than 8 characters long, performing an
aggressive dephrasing is blocked because the number of possibilities can
explode exponentially as the phrase gets longer. Set this flag to bypass this
restriction.
