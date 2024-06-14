
Language
########

What is Grascii?
****************

Grascii is a language designed to represent Gregg Shorthand forms using the
ASCII character set.

It is designed to be intuitive to those already familiar with the system.

Grascii is a context free grammar, and it's implementation can be viewed
in grascii.lark.

Grascii is moderately ambiguous. However, as the shorthand system is also
ambiguous, it is reasonable that Grascii inherits this attribute.

The current definition of Grascii is based on the Pre-anniversary (1916)
version of Gregg Shorthand.

It aims to describe the shorthand forms accurately and succinctly. It also
has many additional symbols enabling it to describe some of the lesser used
features of the system.

For language limitations, see `Unsupported Language Features`_.

+-----------------------------------+---------------------------+---------------+
| Shorthand Form                    | Grascii Representation(s) | Annotation(s) |
+===================================+===========================+===============+
| .. image:: images/strokes/k.png   |K                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/g.png   |G                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/r.png   |R                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/l.png   |L                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/n.png   |N                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/m.png   |M                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/t.png   |T                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/d.png   |D                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/th.png  |TH                         | ( ) ,         |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/p.png   |P                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/b.png   |B                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/f.png   |F                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/v.png   |V                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/ch.png  |CH                         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/j.png   |J                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/s.png   |S                          | ( ) ,         |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/x.png   |X                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/sh.png  |SH                         | ,             |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/h.png   |'                          |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/ng.png  |NG                         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/nk.png  |NK                         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/ld.png  |LD                         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/a.png   |A                          | ~ \| . ,      |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/e.png   |E                          | ~ \| . ,      |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/o.png   |O                          | ( . ,         |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/u.png   |U                          | ) . ,         |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/eu.png  |EU                         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/au.png  |AU                         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/oe.png  |OE                         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/i.png   |I                          | ~ \|          |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/ae.png  |A&E                        | ~ \|          |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/ah.png  |A&'                        | ~ \|          |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/nt.png  |NT, ND                     |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/mt.png  |MT, MD                     |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/tn.png  |TN, DN                     |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/tm.png  |TM, DM                     |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/mn.png  |MN, MM                     |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/td.png  |DT, TD, DD                 |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/df.png  |DF, DV, TV                 |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/jnt.png |JNT, JND, PNT, PND         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/ss.png  |SS                         |               |
+-----------------------------------+---------------------------+---------------+
| .. image:: images/strokes/xs.png  |XS                         |               |
+-----------------------------------+---------------------------+---------------+

Annotations
***********

+-------------+----------------------------+---------------------------------+
| Annotation  |  Acceptable Tokens         | Description                     |
+=============+============================+=================================+
|.            |A, E, O, U                  |Denotes the medium               |
|             |                            |sound of the four                |
|             |                            |standard vowel groups.           |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|,            |A, E, O, U                  |Denotes the long                 |
|             |                            |sound of the four                |
|             |                            |standard vowel groups.           |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|,            |S, Z, TH, SH                |Denotes the more                 |
|             |                            |obscure sound of the             |
|             |                            |preceeding consonant.            |
|             |                            |Ex. *gas* vs. *gaze*,            |
|             |                            |*breath* vs. *breathe*,          |
|             |                            |*assure* vs. *azure*.            |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|~            |A, E, I, A&', A&E           |Denotes that the                 |
|             |                            |preceeding circle                |
|             |                            |vowel is reversed.               |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|\|           |A, E, I, A&', A&E           |Denotes that the                 |
|             |                            |preceeding circle                |
|             |                            |vowel is looped.                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|)            |S, Z, TH                    |When following an S/Z,           |
|             |                            |denotes a right S/Z.             |
|             |                            |When following an TH,            |
|             |                            |denotes an under TH.             |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|(            |S, Z, TH                    |When following an S/Z,           |
|             |                            |denotes a left S/Z.              |
|             |                            |When following an TH,            |
|             |                            |denotes an over TH.              |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|(            |O                           |Denotes an O on its              |
|             |                            |side.                            |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|)            |U                           |Denotes an U on its              |
|             |                            |side.                            |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+
|_            |A, E, O, U, I, EU, OU, OE,  |Signifies a W sound to           |
|             |A&', A&E                    |be applied before the            |
|             |                            |preceeding vowel.                |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
|             |                            |                                 |
+-------------+----------------------------+---------------------------------+

Other Symbols
*************

+-------------+--------------------------------------------------------------+
| Symbol      |Description                                                   |
+=============+==============================================================+
|^            |When placed between tokens, denotes that the two forms are    |
|             |disjoined. When placed at the end of a form, denotes that     |
|             |the preceeding form lies above the line of writing.           |
|             |                                                              |
+-------------+--------------------------------------------------------------+
|\-           |When placed between grascii forms, denotes that the two       |
|             |characters should not be interpreted as a blended form.       |
|             |Ex. N-T prevents interpretation on NT.                        |
|             |                                                              |
+-------------+--------------------------------------------------------------+

Examples
********
+------------------------------------------------+-----------+---------------+
| Shorthand Form                                 | Grascii   | Longhand      |
+================================================+===========+===============+
| .. image:: images/examples/accumulate.png      | AKEUM^U   | Accumulate    |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/approximation.png   | APRXSH    | Approximation |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/boldness.png        | BOLDN     | Boldness      |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/defiant.png         | DFINT     | Defiant       |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/feather.png         | FETH)     | Feather       |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/grouch.png          | GRAUCH    | Grouch        |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/harmony.png         | 'A~MNE    | Harmony       |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/inkling.png         | ENKL'     | Inkling       |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/lifelong.png        | LAFLNG    | Lifelong      |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/prompt.png          | PRMT      | Prompt        |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/scientist.png       | SA&ENTES  | Scientist     |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/seared.png          | S(E,D     | Seared        |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/tangent.png         | TNJNT     | Tangent       |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/timidity.png        | TMEDTE    | Timidity      |
+------------------------------------------------+-----------+---------------+
| .. image:: images/examples/voyage.png          | VOEJ      | Voyage        |
+------------------------------------------------+-----------+---------------+

Unsupported Language Features
*****************************

- Grascii does not provide a way of distinguishing between smooth and sharp
  joinings. There is no plan to make it possible to make this distinction in
  the future.
- Intersection is currently not implemented. Proposed symbol to denote two
  intersected characters: \\.
- RD is currently not implemented as it does not appear in Gregg 1916,
  although, it is a form in subsequent versions.
- There is no way of distinguishing the capitalization of a form.
- The under joining/short vowel sound is not included.
