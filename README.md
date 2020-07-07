
# Grascii 

## About the Project

Grascii is comprised of a language designed to represent Gregg Shorthand
forms using the ASCII character set and of the tools revolving around
the language to facillitate the study of Gregg Shorthand.

## Made With
- Python 3

## Getting Started

### Prerequisites
- Grascii runs on Python 3. It has not been tested on Python 3.5 and below.
- Grascii depends on lark-parser

```
$ pip install lark-parser
```

### Installation

There are two ways to install Grascii.

#### Latest Release

Download the latest release from the releases page.
Releases come bundled with a built version of the Grascii Dictionary.
Simply run from the repository root:

```
$ unzip dict.zip
```

#### Clone the Repository

```
$ git clone ...
```

After cloning, the Grascii Dictionary must be built.

```
$ python grascii.py build -o dict/ ../dsrc/*.txt
```

## Grascii Language

Explanation and example.

## Purpose
When studying shorthand, a student may come across a form which is 
unfamiliar, new, or represents an unknown word. Traditionally, a student
could refer to the dictionary which maps English words to their 
corresponding shorthand forms. However, this technique can be tricky and
inefficient as the student must guess the word in English to
compare to the unknown form. This is likened to the process of using a
dictionary to determine the spelling of a word. This is where the main tool
comes in: Grascii Search.

## Grascii Search
The Grascii forms of all entries of the 1916 Gregg Shorthand Dictionary
have been collected. The Grascii Search Feature allows a user to query with
a Grascii string to search the Grascii dictionary for similar matches
which tell what corresponding English word goes with the form.

### Basic Usage

Ex.

    $ python grascii.py -g AB
    AB About
    Results: 1

### Uncertainty

It is acknowledged that when looking at a form, a stroke may be mistaken
for one of similar form whether by proportion error etc. Thus, Grascii
Search provides levels of uncertainty.

Ex.

    $ python grascii.py -g FND -u1

The ND stroke could also potentially be an under TH or an MT/MD. The search
accounts for these possibilities. F is also close to S or V.

### Interactive Mode

For practical usage, it is recommended to run Grascii Search in interactive
mode. For more complex queries, it removes the need of using escape 
sequences on the command line. It also is more efficient for doing 
multiple searches in succession.

```

$ python grascii.py -i
Enter Search: AB

Found 1 possible interpretation
Beginning search
AB About

Results: 1

...

```

### More Options

For more details on Grascii Search, see search.md.

## Grascii Dictionary

Grascii comes with a dictionary for the 1916 version of the Gregg
Shorthand Dictionary. 

There is also the ability to package other words and derivatives into
the dictionary used by Grascii Search.

For more information, see dictionary.md.

## Grascii Dephrase (Experimental)

Grascii includes an experimental phrase parsing feature which is still under
major development.

It is designed to give the phrase for the most common phrase constructions
in Gregg Shorthand as well as to provide suggestions for never before
seen phrases.

```
$ python grascii.py dephrase AVNBA
I HAVE NOT BEEN ABLE
```

For more information, see dephrase.md.

## Issues

The Grascii Dictionary has not been reviewed for accuracy. If you find any
incorrect entries, please let me know. 

If you discover any issues with the program or have any
suggestions, file an issue.

## Contributing

You are welcome to contribute and make pull requests.

It would be great to have others to add more words to the dictionary
as well as to make dictionaries for other versions of Gregg Shorthand.

If you would like to help, please read the dictionary conventions in
dictionary.md.

## License

## Contact

## Acknowledgements
