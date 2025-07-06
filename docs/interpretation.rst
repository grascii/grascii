
Interpretation
##############

Introduction
************

Grascii is ambiguous, and one of its most prominent types of ambiguity is a
consequence of multi-character strokes, or strokes that are represented by more
than one character.

Consider the Grascii string ``NTN``. It may represent:

- ``NT-N``: The ``NT`` under blend followed by an ``N``
- ``N-TN``: ``N`` followed by the ``TN`` over blend
- ``N-T-N``: ``N`` followed by ``T`` followed by ``N`` with sharp joinings

Each of the above is a possible interpretation of ``NTN``, or a breakdown of the
string into strokes, annotations, and other symbols.

It can be seen that ambiguity arises from:

1. Multi-character strokes that consist of characters that are single-character
   strokes. i.e. ``NT`` consists of ``N`` and ``T``.
2. Multi-character strokes whose last character is also a first character for
   other multi-character strokes. i.e. ``NT`` ends with ``T`` and ``TN`` starts
   with ``T``.

Given all of these possibilities, how should ``NTN`` be interpreted?

.. _canonical-interpretation:

The Canonical Interpretation
****************************

The canonical interpretation is based on Gregg principles, the nature of the
Grascii language, and a little bit of pragmatism. It aims to be the least
surprising interpretation of a Grascii string. That said, understanding the
rules in the following section is by no means a prerequisite for using Grascii.
Rather, they are targeted toward advanced Grascii users and developers.

Rules
=====

The following rules govern the breakdown of a Grascii string into its
canonical interpretation:

1. Prioritize multi-character strokes over single-character strokes.

   **Example**: ``DF`` is the ``DF`` blend, not ``D-F``.

   **Why**: Gregg created blends to be used.

   .. important::

      If the candidate multi-character stroke sequence is followed by an invalid
      annotation for that multi-character stroke, it must be treated as
      single-character strokes.

      For instance, ``SS,`` would be ``S-S,`` because the ``,`` annotation can
      only apply to ``S`` and not ``SS``.

2. Prioritize ``SH`` over multi-character strokes that end in ``S`` such as
   ``SS``/``XS``.

   **Example**: ``SSH`` is ``S-SH``.

   **Why**: Prioritizing the other strokes could lead to a dangling ``H`` which
   is not a valid single-character stroke.

3. Prioritize ``TH`` over multi-character strokes that end in ``T`` such as
   ``JNT``/``PNT``/``NT``/``MT``/``DT``.

   **Example**: ``DTH`` is ``D-TH``.

   **Why**: Prioritizing the other strokes could lead to a dangling ``H``
   which is not a valid single-character stroke.

4. Prioritize ``TN``/``DN``/``TM``/``DM`` over ``NT``/``ND``/``MT``/``MD``.

   **Example**: ``NTN`` is ``N-TN``, not ``NT-N``.

   **Why**: Gregg Shorthand Preanniversary Manual (1916), Seventh Lesson,
   General Exercise, Note (b):

     Where it is possble to use either *ten*, *den*, or *ent*, *end*, the *ten*,
     *den* blend is given the preference.

5. If no priorities from rules 2-4 apply, prioritize multi-character
   strokes that appear earlier in the string over multi-character strokes that
   appear later.

   **Example**: ``NDV`` is ``ND-V``, not ``N-DV``.

   **Why**: Assembling multi-character strokes from left-to-right is most
   natural to readers and writers.
