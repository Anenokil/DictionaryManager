"""
Public exports for backend.core package.

Author: Anenokil
"""

from .types import (
    Word, Translation, Category, CtgValue, GramForm, WordForm,
    Phrase, PhraseTr, Note, Group, Timestamp, EntryID, DctName,
    SerializedData,
)
from .errors import (
    DMError, BackendError, BackendCoreError,
    DeserializationError, MissingFieldsError,
    FieldTypeError, UnknownVersionError,
)
from .entry import Entry, Translations, Forms, Phrases, Notes, Groups
from .dictionary import Dictionary
from .trainer import (
    Trainer, TrainingMethod, TrainingOrder, EntrySelection,
    FormSelection, TrainingConfig,
)
from .utils import (
    remove_dup, gram_form_to_str, validate_required_fields,
    validate_field_type, validate_field_len,
)
