# Dictionary Manager

A dictionary manager for memorizing foreign words and expanding your vocabulary.

## Table of Contents

- [Installation](#installation)
- [Features](#features)
  - [Dictionaries](#dictionaries)
    - [Tags](#tags)
    - [Grammatical categories](#grammatical-categories)
    - [Escape sequences](#escape-sequences)
  - [Practice](#practice)

## Installation

**Requirements:**

- Python 3.10 or newer
- [Pipenv](https://pipenv.pypa.io/)

The following packages are installed automatically by Pipenv:

- PySide6
- Pillow
- platformdirs

**Steps:**

```bash
git clone git@github.com:Anenokil/DictionaryManager.git
cd DictionaryManager
pipenv install --categories "packages gui-v2"
pipenv shell
python gui_v2.py
```

## Features

Dictionary Manager is designed for maintaining bilingual dictionaries and learning foreign vocabulary.
It is not language-specific and works with any language pair.

You can keep several dictionaries at once: create your own, share them,
and import dictionaries made by others.

### Dictionaries

A dictionary is a collection of entries, each devoted to a single word.
To create an entry, you only need to provide the word and at least one translation.
Optionally, you can also add spelling variants, additional translations, word forms,
phrases and usage examples, notes, and an illustration.
Entries can be tagged, and favorites can be marked with a star.

#### Tags

Tags make searching easier and let you study specific groups of words.

#### Grammatical categories

Grammatical categories let you define word forms. For example, the category
"number" with the values "singular" and "plural" lets you record the forms
*apple* (singular) and *apples* (plural).

The set of categories is not fixed, so you can add your own,
which makes the program suitable for any language.

#### Escape sequences

Escape sequences let you type characters that are missing from your current
keyboard layout without switching layouts.

### Practice

Practice mode offers several types of exercises: words, word forms, phrases, and more.
In each of them, you type the correct answer.

The program tracks your practice statistics, so you can see your weak spots
and focus on them, for example by practicing the most difficult entries first.
