"""
Public exports for backend.core package.

Author: Anenokil
"""

from .types import (
    Word, Translation, Category, CtgValue, GramForm, WordForm,
    Phrase, PhraseTr, Note, Tag, Timestamp, DctName, SerializedData,
)
from .errors import (
    DMError, BackendError, DeserializationError, MissingFieldsError,
    FieldTypeError, UnknownVersionError, MigrationError,
)
from .entry import Entry, Variants, Translations, Forms, Phrases, Notes, Tags
from .dictionary import (
    Dictionary, InvalidTranslationError,
    InvalidGramFormError, InvalidWordFormError,
    InvalidPhraseError, InvalidPhraseTrError,
    InvalidNoteError, InvalidTagError,
    InvalidCategoryError, CategoryExistsError,
    InvalidCtgValueError, CtgValueExistsError,
    get_dct_id_from_dict, get_dct_name_from_dict,
)
from .trainer import (
    Trainer, TrainingFormat, TrainingOrder, EntrySelection,
    FormSelection, TrainingConfig,
)
from .utils import (
    remove_dup, gram_form_to_str, validate_required_fields,
    validate_field_type, validate_field_len, validation_and_migration,
    read_json, save_json,
)
