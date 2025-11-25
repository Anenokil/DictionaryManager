"""
Central place for semantic type aliases used across backend modules.

Author: Anenokil
"""

from typing import Any

# Typing aliases shared across backend package
Word = str
Translation = Word
Category = str  # For example, gender, number, tense
CtgValue = str  # For example, singular/plural, present/past/future
GramForm = tuple[CtgValue, ...]  # For example, present perfect & 3rd person
WordForm = Word  # For example, goes, went
Text = str
Phrase = Text
PhraseTr = Text
Note = Text
Group = str
Timestamp = tuple[int, int, int]
EntryID = int
DctName = str | None
SerializedData = dict[str, Any]  # Serialized entry/dictionary/manager
