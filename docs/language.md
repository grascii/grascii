
# Grascii Language

## What is Grascii?

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

For a summary of what the language does not currently support, see the list
below.

## Conversion Table

Shorthand Form | Grascii Representation(s) | Annotations
---------------|---------------------------|------------
|K
|G
|R
|L
|N
|M
|T
|D
|TH | )(,
|P
|B
|F
|V
|CH
|J
|S, Z | )(,
|X
|SH | ,
|'
|NG
|NK
|LD
|A | .,~\|
|E | .,~\|
|O | .,
|U | .,
|EU
|AU
|OE
|I | ~\|
|A&E
|A&'
|NT, ND
|MT, MD
|TN, DN
|TM, DM
|MN, MM
|DT, TD, DD
|DF, DV, TV
|SS
|XS
|JNT, JND, PNT, PND

## Annotations

Annotation | Acceptable Tokens | Description
-----------|-------------------|------------
.|A, E, O, U | Denotes the medium sound of the four standard vowel groups.
,|A, E, O, U | Denotes the long sound of the four standard vowel groups.
,|S, TH, SH | Denotes the more obscure sound of the proceeding consonant. Ex. _gas_ vs. _gaze_, _breath_ vs. _breathe_, _assure_ vs. _azure_.
\||A, E, I | Denotes that the preceeding circle vowel is looped.
~|A, E, I | Denotes that the preceeding circle vowel is reversed according to the reversing principle.
)|S, TH | When following an S, denotes a right S. When following an TH, denotes an under TH.
(|S, TH | When following an S, denotes a left S. When following an TH, denotes an over TH. 
\_|A, E, O, U, I, EU, AU, OE, A&E, A&' | Signifies a W sound to be applied before the preceeding vowel.

## Other Symbols

Symbol | Description
-------|------------
^|When placed between tokens, denotes that the two forms are disjoined. Whenplaced at the end of a from, denotes that the preceeding form lies above the line of writing.
-|When placed between grascii forms, denotes that the two characters should not be interpreted as a blended form. Ex. N-T prevents interpretation of NT.

## Examples
Shorthand Form | English | Grascii
---------------|---------|--------

## Unsupported Language Features

- Grascii does provide a way of distinguishing between smooth and sharp 
joinings. There is no plan to make it possible to make this distinction in 
the future.
- Intersection is currently not implemented. Proposed symbol to denote two
intersected characters: \\.
- RD is currently not implemented as it does not appear in Gregg 1916, 
although, it is a form in subsequent versions.
- There is no way of distinguishing the capitalization of a form.
- The under joining/short vowel sound is not included.