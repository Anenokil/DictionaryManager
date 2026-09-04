from typing import Generator, Collection, Callable, Any
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QScrollArea,
    QTabWidget, QTabBar, QToolBar, QMenu, QTableWidget,
    QTableWidgetItem, QDialog, QInputDialog, QFileDialog,
    QDialogButtonBox, QPushButton, QMessageBox, QComboBox,
    QCheckBox, QLineEdit, QLabel, QLayout, QVBoxLayout,
    QHBoxLayout, QFormLayout, QGridLayout, QHeaderView,
    QAbstractItemView, QSizePolicy,
    QStyle, QStyledItemDelegate,
)
from PySide6.QtGui import (
    QAction, QCloseEvent, QIcon, QColor, QBrush,
    QShortcut, QKeySequence,
)
from PySide6.QtCore import Qt, QSize, QTimer

from backend import (
    Translations, Variants, Forms, GramForm, Phrases,
    Entry, Dictionary, DctBundle, Manager, gram_form_to_str,
)
from persistence import AppData


def forms_to_pairs(forms: Forms) -> Generator[tuple[str, str], None, None]:
    for gram_form, word_forms in forms.items():
        for word_form in word_forms:
            yield gram_form_to_str(gram_form), word_form


def phrases_to_pairs(phrases: Phrases) -> Generator[tuple[str, str], None, None]:
    for phrase, translations in phrases.items():
        for tr in translations:
            yield phrase, tr


def lemma_to_str(variants: Variants) -> str:
    return ', '.join(variants)


def translations_to_str(tr: Translations) -> str:
    return ', '.join(tr)


def forms_to_str(forms: Forms) -> str:
    return '\n'.join(
        f'[{gram_form_to_str(gram_form)}] {', '.join(word_forms)}'
        for gram_form, word_forms in forms.items()
    )


def phrases_to_str(phrases: Phrases) -> str:
    add_quotes = lambda lst: (f'"{s}"' for s in lst)
    return '\n'.join(
        f'"{phrase}": ' + ', '.join(add_quotes(phrase_tr))
        for phrase, phrase_tr in phrases.items()
    )


def select_dct_file_to_load(parent: QWidget) -> tuple[str, bool]:
    file_filter = '(*.json)'
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        caption='Open Dictionary File',
        filter=file_filter,
    )
    return file_path, bool(file_path)


def select_dct_file_to_save(parent: QWidget) -> tuple[str, bool]:
    file_filter = '(*.json)'
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        caption='Open Dictionary File',
        filter=file_filter,
    )
    return file_path, bool(file_path)


def ask_yes_no(parent: QWidget, title: str, text: str) -> bool:
    reply = QMessageBox.question(
        parent, title, text,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    return reply == QMessageBox.Yes


def get_column_data(table: QTableWidget, column: int) -> list[str]:
    data = [
        table.item(row, column).text()
        for row in range(table.rowCount())
    ]
    return data


def create_img_button(
        img_path: str,
        icon_size: tuple[int, int] = (24, 24),
        button_size: tuple[int, int] = (28, 28),
) -> QPushButton:
    button = QPushButton()
    button.setIcon(QIcon(img_path))
    button.setIconSize(QSize(*icon_size))
    button.setFixedSize(*button_size)
    button.setFlat(True)
    return button


def make_table_growable_up_to_content(
        table: QTableWidget,
        on_change: Callable[[], None] | None = None,
):
    """
    The table grows only up to the height at which all rows are
    visible (no internal scrollbar). Beyond that, any extra space
    from resizing the window goes to other expanding widgets.
    """

    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_max_height():
        row_heights = sum(table.rowHeight(row) for row in range(table.rowCount()))
        header = table.horizontalHeader()
        header_height = header.height() if header.isVisible() else 0
        frame = table.frameWidth() * 2
        full_content_height = row_heights + header_height + frame
        full_content_height = max(full_content_height, table.minimumHeight())
        table.setMaximumHeight(full_content_height)
        if on_change is not None:
            on_change()

    def schedule_update():
        # Deferred: if a row is inserted and then populated with items
        # right after (insertRow + setItem), rowsInserted fires before
        # the items are set. Deferring to the next event loop iteration
        # ensures rowHeight() reflects the final content.
        QTimer.singleShot(0, update_max_height)

    update_max_height()
    table.model().rowsInserted.connect(lambda *_: schedule_update())
    table.model().rowsRemoved.connect(lambda *_: schedule_update())


def link_exclusive_selection(tables: list[QTableWidget]):
    """
    Selecting cells in one of the given tables clears the selection
    in all the other tables in the group.
    """

    is_updating = [False]

    def make_handler(current_table: QTableWidget):
        def on_selection_changed():
            if is_updating[0]:
                return
            is_updating[0] = True
            for table in tables:
                if table is not current_table:
                    table.clearSelection()
            is_updating[0] = False
        return on_selection_changed

    for table in tables:
        table.itemSelectionChanged.connect(make_handler(table))


def valid_gram_form(gram_form: dict[str, str]) -> tuple[bool, str]:
    if all(val == '' for val in gram_form.values()):
        return False, 'Grammatical form must not be empty'
    return True, ''


def setup_table_context_menu(
        table: QTableWidget,
        actions_config: list[None | tuple[str | Callable[[], str],
                                          Callable[[int, int], Any] | None]],
):
    """
    Configure a context menu for the given table.

    Args:
        table: Table widget to attach the context menu to.
        actions_config: List describing menu items. Each element can be:
                        - None - inserts a separator.
                        - (text, callback) - creates a menu action, where:
                          text: static string or a zero-argument callable that returns
                                the action text (useful for dynamic labels).
                          callback: function(row, column) called when the action is
                                    triggered, or None for a non-clickable label.
    """

    table.setContextMenuPolicy(Qt.CustomContextMenu)

    def show_menu(pos):
        item = table.itemAt(pos)
        if item is None:
            return
        row, column = item.row(), item.column()

        menu = QMenu(table)
        action_callbacks = {}

        for entry in actions_config:
            # Separator
            if entry is None:
                menu.addSeparator()
                continue

            text, callback = entry
            if isinstance(text, Callable):
                text = text()
            action = menu.addAction(text)

            if callback is None:
                action.setEnabled(False)
            else:
                action_callbacks[action] = callback

        chosen = menu.exec(table.viewport().mapToGlobal(pos))
        if chosen in action_callbacks:
            action_callbacks[chosen](row, column)

    table.customContextMenuRequested.connect(show_menu)


class ColoredCellDelegate(QStyledItemDelegate):
    """
    Custom item background stays visible even when the cell is selected.
    """

    OVERLAY_ALPHA = 160  # 0-255

    def paint(self, painter, option, index):
        background = index.data(Qt.BackgroundRole)

        if background is None:
            super().paint(painter, option, index)
            return

        color = QColor(background.color())
        is_selected = bool(option.state & QStyle.State_Selected)

        if is_selected:
            super().paint(painter, option, index)
            color.setAlpha(self.OVERLAY_ALPHA)
            painter.fillRect(option.rect, color)
        else:
            painter.fillRect(option.rect, color)
            super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            QTimer.singleShot(0, editor.selectAll)
        return editor


class InputTagDialog(QDialog):
    def __init__(
            self,
            dct: Dictionary,
            initial: tuple[str, bool] | None = None,
            parent: QWidget | None = None,
    ):
        super().__init__(parent)

        if initial is None:
            title = 'New tag'
            tag = ''
            is_default = False
            self.other_tags = set(dct.tags)
        else:
            title = 'Edit tag'
            tag, is_default = initial
            self.other_tags = set(dct.tags).difference({tag})

        self.setWindowTitle(title)

        self._line_edit = QLineEdit(tag)
        self._is_default = QCheckBox()
        self._is_default.setChecked(is_default)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        label1 = QLabel('Tag:', alignment=Qt.AlignRight | Qt.AlignVCenter)
        label2 = QLabel(
            'Automatically apply\n'
            'this tag to new entries:',
            alignment=Qt.AlignRight | Qt.AlignVCenter,
        )
        self.label_error = QLabel('', alignment=Qt.AlignHCenter)

        self.layout = QGridLayout(self)
        self.layout.addWidget(label1, 0, 0)
        self.layout.addWidget(self._line_edit, 0, 1)
        self.layout.addWidget(label2, 1, 0)
        self.layout.addWidget(self._is_default, 1, 1, alignment=Qt.AlignBottom)
        self.layout.addWidget(buttons, 2, 0, 1, 2)

    def _validate(self) -> tuple[bool, str]:
        tag = self._line_edit.text()
        if tag == '':
            return False, 'Tag must not be empty'
        if tag in self.other_tags:
            return False, 'Tag already exists'
        return True, ''

    def accept(self):
        is_ok, error_msg = self._validate()

        if is_ok:
            super().accept()
        else:
            self.label_error.setText(f'Invalid value: {error_msg}')
            self.label_error.setStyleSheet('color: #d32f2f;')
            self.layout.addWidget(self.label_error, 3, 0, 1, 2)

    def get_text(self) -> tuple[str, bool]:
        return self._line_edit.text(), self._is_default.isChecked()

    @staticmethod
    def get_input(
            dct: Dictionary,
            current: tuple[str, bool] | None = None,
            parent: QWidget | None = None,
    ) -> tuple[str, bool, bool]:
        dialog = InputTagDialog(dct, current, parent)
        ok = dialog.exec() == QDialog.Accepted
        tag, is_default = dialog.get_text() if ok else ('', False)
        return tag, is_default, ok


class OptionsDialog(QDialog):
    def __init__(
            self,
            specs: dict[str, list[str]],
            defaults: tuple[str, ...],
            title: str,
            validator: Callable[[dict[str, str]], tuple[bool, str]] | None = None,
    ):
        super().__init__()

        self.specs = specs
        self.validator = validator

        self.setWindowTitle(title)

        self.combo_boxes: dict[str, QComboBox] = {}

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        form_container = QWidget()
        form_layout = QFormLayout(form_container)

        for spec, default in zip(specs.items(), defaults):
            name, options = spec

            combo = QComboBox()
            for option in options:
                combo.addItem(option)

            # Set default option
            default_index = combo.findText(default)
            if default_index != -1:
                combo.setCurrentIndex(default_index)

            form_layout.addRow(QLabel(name), combo)
            self.combo_boxes[name] = combo

        scroll.setWidget(form_container)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.label_error = QLabel()

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(scroll)
        self.layout.addWidget(buttons)

    def _validate(self) -> tuple[bool, str]:
        if self.validator is None:
            return True, ''
        return self.validator(self.get_values())

    def accept(self):
        is_ok, error_msg = self._validate()

        if is_ok:
            super().accept()
        else:
            self.label_error.setText(f'Invalid value: {error_msg}')
            self.label_error.setStyleSheet('color: #d32f2f;')
            self.layout.addWidget(self.label_error)

    def get_values(self) -> dict[str, str]:
        return {
            name: combo.currentText()
            for name, combo in self.combo_boxes.items()
        }

    @staticmethod
    def get_settings(
            specs: dict[str, list[str]],
            defaults: tuple[str, ...],
            title: str,
            validator: Callable[[dict[str, str]], tuple[bool, str]] | None = None,
    ) -> tuple[dict[str, str] | None, bool]:
        dialog = OptionsDialog(specs, defaults, title, validator)
        ok = dialog.exec() == QDialog.Accepted
        values = dialog.get_values() if ok else None
        return values, ok


class CheckableList(QScrollArea):
    def __init__(
            self,
            items: list[str],
            checked_items: set[str],
            on_change: Callable[[], None] | None = None,
    ):
        super().__init__()

        self._on_change = on_change

        self.container = QWidget()
        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignTop)

        self.checkboxes: dict[str, QCheckBox] = {}

        for text in items:
            checkbox = QCheckBox(text)
            is_checked = text in checked_items
            checkbox.setChecked(is_checked)
            layout.addWidget(checkbox)
            self.checkboxes[text] = checkbox

        self.setWidget(self.container)

        self._update_max_height()

    def add_item(self, text: str, is_checked: bool = False):
        checkbox = QCheckBox(text)
        checkbox.setChecked(is_checked)
        self.container.layout().addWidget(checkbox)
        self.checkboxes[text] = checkbox
        QTimer.singleShot(0, self._update_max_height)

    def get_checked_items(self) -> list[str]:
        return [text for text, cb in self.checkboxes.items() if cb.isChecked()]

    def _update_max_height(self):
        content_height = self.container.sizeHint().height()
        frame = self.frameWidth() * 2
        full_height = content_height + frame
        self.setMaximumHeight(max(full_height, self.minimumHeight()))
        if self._on_change is not None:
            self._on_change()


class EqualGrowFormLayout(QGridLayout):
    """
    A 'label + field' layout where widgets in each row grow evenly,
    without empty gaps: as soon as a row's growable widget reaches
    its maximumHeight, the row's stretch is removed, and the freed-up
    space goes entirely to the remaining growing rows.
    """

    _GROWABLE_STRETCH = 1

    def __init__(self, label_alignment: Qt.AlignmentFlag):
        super().__init__()

        self._label_alignment = label_alignment
        self._row = 0

    def add_row(self, label_widget, field_widget, growable_widget=None):
        row = self._row

        self.addWidget(label_widget, row, 0, self._label_alignment)
        self.addWidget(field_widget, row, 1)

        widget_to_track = growable_widget or field_widget
        vertical_policy = widget_to_track.sizePolicy().verticalPolicy()
        is_expanding = vertical_policy in (QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        self.setRowStretch(row, self._GROWABLE_STRETCH if is_expanding else 0)
        self._row += 1


class EntryDetailsDialog(QDialog):
    """Dialog for displaying entry information."""

    def __init__(self, dct_bundle: DctBundle, entry: Entry, parent: QWidget | None = None):
        super().__init__(parent)

        self.dct = dct_bundle.dct
        self.replacer = dct_bundle.replacer
        self.entry = entry
        self.statuses = {}
        self.exit_code = None

        self._create_widgets()
        self._set_shortcuts()
        self._configure_window()

    def _configure_window(self):
        self.setWindowTitle(f'Entry "{lemma_to_str(self.entry.variants)}"')
        self.setModal(True)
        self.resize(500, 500)

    def _create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self._create_fields()
        self._create_buttons()

    @staticmethod
    def _create_field_container(table, button) -> QWidget:
        field_container = QWidget()
        field_layout = QHBoxLayout(field_container)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSizeConstraint(QLayout.SetMaximumSize)
        field_layout.addWidget(table)
        field_layout.addWidget(button)
        return field_container

    def _create_fields(self):
        # Layout for displaying entry data
        self.form_layout = EqualGrowFormLayout(label_alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.main_layout.addLayout(self.form_layout)

        # Create labels
        lemma_variants_label = QLabel('Lemma\nvariants:', alignment=Qt.AlignRight)
        translations_label = QLabel('Translations:')
        forms_label = QLabel('Forms:')
        phrases_label = QLabel('Phrases:')
        notes_label = QLabel('Notes:')
        tags_label = QLabel('Tags:')
        fav_label = QLabel('Favorite:')

        # Create tables
        self.lemma_variants_table = self.create_single_column_table(
            [self.replacer.escape(s) for s in self.entry.variants]
        )
        self.translations_table = self.create_single_column_table(
            [self.replacer.escape(s) for s in self.entry.tr]
        )
        self.forms_table = self.create_two_column_table(
            [(gf, self.replacer.escape(wf))
             for gf, wf in forms_to_pairs(self.entry.forms)],
            gram_forms=list(self.entry.forms.keys()),
            is_1_col_active=False,
        )
        self.phrases_table = self.create_two_column_table(
            [(self.replacer.escape(ph), self.replacer.escape(pt))
             for ph, pt in phrases_to_pairs(self.entry.phrases)]
        )
        self.notes_table = self.create_single_column_table(
            [self.replacer.escape(s) for s in self.entry.notes]
        )

        link_exclusive_selection([
            self.lemma_variants_table,
            self.translations_table,
            self.forms_table,
            self.phrases_table,
            self.notes_table,
        ])

        def delete_msg(table: QTableWidget, singular: str) -> str:
            n = len({i.row() for i in table.selectedIndexes()})
            if n == 1:
                return f'Delete 1 {singular}'
            return f'Delete {n} {singular}s'

        setup_table_context_menu(self.lemma_variants_table, [
            (lambda: delete_msg(self.lemma_variants_table, 'variant'), self.delete_lemma_variants),
        ])
        setup_table_context_menu(self.translations_table, [
            (lambda: delete_msg(self.translations_table, 'translation'), self.delete_translations),
        ])
        setup_table_context_menu(self.forms_table, [
            (lambda: delete_msg(self.forms_table, 'form'), self.delete_forms),
        ])
        setup_table_context_menu(self.phrases_table, [
            (lambda: delete_msg(self.phrases_table, 'phrase'), self.delete_phrases),
        ])
        setup_table_context_menu(self.notes_table, [
            (lambda: delete_msg(self.notes_table, 'note'), self.delete_notes),
        ])

        # Create other widgets
        self.tags_list = CheckableList(
            sorted(self.dct.tags), set(self.entry.tags),
            on_change=self.main_layout.activate,
        )
        self.tags_list.setWidgetResizable(True)
        self.tags_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tags_list.setMinimumHeight(50)
        self.tags_list.setMinimumWidth(120)

        self.fav_checkbox = QCheckBox()
        self.fav_checkbox.setChecked(self.entry.is_fav)

        # Create image buttons
        self.add_lemma_variant_button = create_img_button('resources/images/add.png')
        self.add_translation_button = create_img_button('resources/images/add.png')
        self.add_form_button = create_img_button('resources/images/add.png')
        self.add_phrase_button = create_img_button('resources/images/add.png')
        self.add_note_button = create_img_button('resources/images/add.png')
        self.add_tag_button = create_img_button('resources/images/add.png')

        # Signal handling
        self.forms_table.cellDoubleClicked.connect(self.on_gram_form_double_clicked)

        self.add_lemma_variant_button.clicked.connect(self.add_lemma_variant)
        self.add_translation_button.clicked.connect(self.add_translation)
        self.add_form_button.clicked.connect(self.add_form)
        self.add_phrase_button.clicked.connect(self.add_phrase)
        self.add_note_button.clicked.connect(self.add_note)
        self.add_tag_button.clicked.connect(self.add_tag)

        # Validation for tables
        self.lemma_variants_table.itemChanged.connect(self.on_item_changed)
        self.translations_table.itemChanged.connect(self.on_item_changed)
        self.forms_table.itemChanged.connect(self.on_item_changed)
        self.phrases_table.itemChanged.connect(self.on_item_changed)
        self.notes_table.itemChanged.connect(self.on_item_changed)

        # Custom cell coloring delegate
        self.lemma_variants_table.setItemDelegate(ColoredCellDelegate(self.lemma_variants_table))
        self.translations_table.setItemDelegate(ColoredCellDelegate(self.translations_table))
        self.forms_table.setItemDelegate(ColoredCellDelegate(self.forms_table))
        self.phrases_table.setItemDelegate(ColoredCellDelegate(self.phrases_table))
        self.notes_table.setItemDelegate(ColoredCellDelegate(self.notes_table))

        # Place widgets in the layout
        lemma_field_container = self._create_field_container(
            self.lemma_variants_table, self.add_lemma_variant_button,
        )
        translations_field_container = self._create_field_container(
            self.translations_table, self.add_translation_button,
        )
        forms_field_container = self._create_field_container(self.forms_table, self.add_form_button)
        phrases_field_container = self._create_field_container(
            self.phrases_table, self.add_phrase_button,
        )
        notes_field_container = self._create_field_container(self.notes_table, self.add_note_button)
        tags_field_container = self._create_field_container(self.tags_list, self.add_tag_button)

        self.form_layout.add_row(
            lemma_variants_label, lemma_field_container, self.lemma_variants_table
        )
        self.form_layout.add_row(
            translations_label, translations_field_container, self.translations_table
        )
        self.form_layout.add_row(forms_label, forms_field_container, self.forms_table)
        self.form_layout.add_row(phrases_label, phrases_field_container, self.phrases_table)
        self.form_layout.add_row(notes_label, notes_field_container, self.notes_table)
        self.form_layout.add_row(tags_label, tags_field_container, self.tags_list)
        self.form_layout.add_row(fav_label, self.fav_checkbox)

        # Configure table growth behavior
        make_table_growable_up_to_content(self.lemma_variants_table, self.main_layout.activate)
        make_table_growable_up_to_content(self.translations_table, self.main_layout.activate)
        make_table_growable_up_to_content(self.forms_table, self.main_layout.activate)
        make_table_growable_up_to_content(self.phrases_table, self.main_layout.activate)
        make_table_growable_up_to_content(self.notes_table, self.main_layout.activate)

    def _create_buttons(self):
        buttons = QDialogButtonBox()

        self.save_button = QPushButton('Save')
        self.close_button = QPushButton('Close')
        self.delete_button = QPushButton('Delete')

        buttons.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(self.close_button, QDialogButtonBox.RejectRole)
        buttons.addButton(self.delete_button, QDialogButtonBox.DestructiveRole)

        self.save_button.clicked.connect(self.save_and_close)
        self.close_button.clicked.connect(self.reject)
        self.delete_button.clicked.connect(self.delete_entry)

        self.main_layout.addWidget(buttons)

    def _set_shortcuts(self):
        add_lemma_variant_shortcut = QShortcut(QKeySequence('Ctrl+N'), self.lemma_variants_table)
        add_lemma_variant_shortcut.setContext(Qt.WidgetShortcut)
        add_lemma_variant_shortcut.activated.connect(self.add_lemma_variant)

        add_translation_shortcut = QShortcut(QKeySequence('Ctrl+N'), self.translations_table)
        add_translation_shortcut.setContext(Qt.WidgetShortcut)
        add_translation_shortcut.activated.connect(self.add_translation)

        add_form_shortcut = QShortcut(QKeySequence('Ctrl+N'), self.forms_table)
        add_form_shortcut.setContext(Qt.WidgetShortcut)
        add_form_shortcut.activated.connect(self.add_form)

        add_phrase_shortcut = QShortcut(QKeySequence('Ctrl+N'), self.phrases_table)
        add_phrase_shortcut.setContext(Qt.WidgetShortcut)
        add_phrase_shortcut.activated.connect(self.add_phrase)

        add_note_shortcut = QShortcut(QKeySequence('Ctrl+N'), self.notes_table)
        add_note_shortcut.setContext(Qt.WidgetShortcut)
        add_note_shortcut.activated.connect(self.add_note)

        save_shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        save_shortcut.activated.connect(self.save_and_close)

        close_shortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
        close_shortcut.activated.connect(self.reject)

    @staticmethod
    def create_single_column_table(
            content: Collection[str],
            is_active: bool = True,
    ) -> QTableWidget:
        """Create a single-column table with the given data."""

        table = QTableWidget()

        # Set up the table with one column
        table.setColumnCount(1)

        # Hide the horizontal header
        table.horizontalHeader().setVisible(False)

        # Enable editing if requested
        if is_active:
            table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        else:
            table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Allow selecting multiple rows
        table.setSelectionMode(QTableWidget.ExtendedSelection)

        # Set column resize mode
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Set row count and populate data
        table.setRowCount(len(content))
        for row, item in enumerate(content):
            table_item = QTableWidgetItem(item)
            table.setItem(row, 0, table_item)

        # Set reasonable size for the table
        table.setMinimumHeight(30)
        table.setMinimumWidth(100)

        return table

    @staticmethod
    def create_two_column_table(
            content: Collection[tuple[str, str]],
            gram_forms: Collection[GramForm] | None = None,
            is_1_col_active: bool = True,
    ) -> QTableWidget:
        """Create a two-column table with the given data."""

        table = QTableWidget()

        # Set up the table with two columns
        table.setColumnCount(2)

        # Hide the horizontal header
        table.horizontalHeader().setVisible(False)

        # Enable editing
        table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)

        # Allow selecting multiple rows
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.ExtendedSelection)

        # Enable smooth scrolling
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Set column resize modes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Set row count and populate data
        table.setRowCount(len(content))
        for row, (item1, item2) in enumerate(content):
            table_item1 = QTableWidgetItem(item1)
            if gram_forms is not None:
                data1 = gram_forms[row]
                table_item1.setData(Qt.UserRole, data1)
            if is_1_col_active:
                table_item1.setFlags(table_item1.flags() | Qt.ItemIsEditable)
            else:
                table_item1.setFlags(table_item1.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 0, table_item1)

            table_item2 = QTableWidgetItem(item2)
            table_item2.setFlags(table_item2.flags() | Qt.ItemIsEditable)
            table.setItem(row, 1, table_item2)

        # Set reasonable size for the table
        table.setMinimumHeight(30)
        table.setMinimumWidth(120)

        return table

    @staticmethod
    def add_row_to_single_column_table(table: QTableWidget):
        n_rows = table.rowCount()
        table.setRowCount(n_rows + 1)
        table.setItem(n_rows, 0, QTableWidgetItem(''))

        # Set focus on the new cell
        table.setCurrentCell(n_rows, 0)
        table.editItem(table.item(n_rows, 0))

    @staticmethod
    def add_row_to_two_column_table(table: QTableWidget, is_1_col_active: bool = True, data=None):
        n_rows = table.rowCount()
        table.setRowCount(n_rows + 1)

        table_item1 = QTableWidgetItem('')
        if data is not None:
            table_item1.setData(Qt.UserRole, data)
        if is_1_col_active:
            table_item1.setFlags(table_item1.flags() | Qt.ItemIsEditable)
        else:
            table_item1.setFlags(table_item1.flags() & ~Qt.ItemIsEditable)

        table_item2 = QTableWidgetItem('')

        table.setItem(n_rows, 0, table_item1)
        table.setItem(n_rows, 1, table_item2)

        # Set focus on the new cell
        focused_column = 0 if is_1_col_active else 1
        table.setCurrentCell(n_rows, focused_column)
        table.editItem(table.item(n_rows, focused_column))

    @staticmethod
    def get_phrases_data(table: QTableWidget) -> dict[str, list[str]]:
        data = {}
        for row in range(table.rowCount()):
            phrase = table.item(row, 0).text()
            translation = table.item(row, 1).text()
            data.setdefault(phrase, []).append(translation)
        return data

    @staticmethod
    def get_forms_data(table: QTableWidget) -> dict[GramForm, list[str]]:
        data = {}
        for row in range(table.rowCount()):
            gram_form = table.item(row, 0).data(Qt.UserRole)
            word_form = table.item(row, 1).text()
            data.setdefault(gram_form, []).append(word_form)
        return data

    def validate_lemma_variant(self, variant: str) -> tuple[bool, str]:
        if variant == '':
            return False, 'Lemma variant must not be empty'
        variants = get_column_data(self.lemma_variants_table, 0)
        if variants.count(variant) > 1:
            return False, f'Variant {variant} is a duplicate'
        return True, ''

    def validate_translation(self, translation: str) -> tuple[bool, str]:
        if translation == '':
            return False, 'Translation must not be empty'
        translations = get_column_data(self.translations_table, 0)
        if translations.count(translation) > 1:
            return False, f'Translation {translation} is a duplicate'
        return True, ''

    def validate_word_form(self, gram_form: GramForm, word_form: str) -> tuple[bool, str]:
        if word_form == '':
            return False, 'Word form must not be empty'
        gram_forms = [
            self.forms_table.item(row, 0).data(Qt.UserRole)
            for row in range(self.forms_table.rowCount())
        ]
        word_forms = get_column_data(self.forms_table, 1)
        adj_word_forms = [wf for gf, wf in zip(gram_forms, word_forms) if gf == gram_form]
        if adj_word_forms.count(word_form) > 1:
            return False, f'Word form {word_form} is a duplicate'
        return True, ''

    def validate_phrase(self, phrase: str) -> tuple[bool, str]:
        if phrase == '':
            return False, 'Phrase must not be empty'
        return True, ''

    def validate_phrase_translation(self, phrase: str, phrase_tr: str) -> tuple[bool, str]:
        if phrase_tr == '':
            return False, 'Phrase translation must not be empty'
        phrases = get_column_data(self.phrases_table, 0)
        phrase_trs = get_column_data(self.phrases_table, 1)
        adj_phrase_trs = [pt for ph, pt in zip(phrases, phrase_trs) if ph == phrase]
        if adj_phrase_trs.count(phrase_tr) > 1:
            return False, f'Phrase translation {phrase_tr} is a duplicate'
        return True, ''

    def validate_note(self, note: str) -> tuple[bool, str]:
        if note == '':
            return False, 'Note must not be empty'
        notes = get_column_data(self.notes_table, 0)
        if notes.count(note) > 1:
            return False, f'Note {note} is a duplicate'
        return True, ''

    def on_item_changed(self, item: QTableWidgetItem):
        # Validation
        match item.tableWidget():
            case self.lemma_variants_table:
                ok, error_msg = self.validate_lemma_variant(item.text())
            case self.translations_table:
                ok, error_msg = self.validate_translation(item.text())
            case self.forms_table:
                if item.column() != 1:
                    return
                gram_form = self.forms_table.item(item.row(), item.column() - 1).data(Qt.UserRole)
                ok, error_msg = self.validate_word_form(gram_form, item.text())
            case self.phrases_table:
                if item.column() == 0:
                    ok, error_msg = self.validate_phrase(item.text())
                else:
                    phrase = self.phrases_table.item(item.row(), item.column() - 1).text()
                    ok, error_msg = self.validate_phrase_translation(phrase, item.text())
            case self.notes_table:
                ok, error_msg = self.validate_note(item.text())

        # Update UI
        if ok:
            item.setBackground(QBrush())
            item.setToolTip('')
        else:
            item.setBackground(QBrush(QColor('#ffcccc')))
            item.setToolTip(error_msg)

        # Set cell status
        self.statuses[item.tableWidget(), item.row(), item.column()] = error_msg

    def on_gram_form_double_clicked(self, row: int, column: int):
        if column != 0:
            return

        item = self.forms_table.item(row, column)
        if item is None:
            return

        specs = {k: [''] + v for k, v in self.dct.features.items()}
        gram_form = item.data(Qt.UserRole)
        res, ok = OptionsDialog.get_settings(
            specs, gram_form, 'Grammatical form settings', validator=valid_gram_form
        )
        if not ok:
            return
        new_gram_form = tuple(res.values())

        self.forms_table.item(row, column).setData(Qt.UserRole, new_gram_form)
        self.forms_table.item(row, column).setText(gram_form_to_str(new_gram_form))

    def add_lemma_variant(self):
        self.add_row_to_single_column_table(self.lemma_variants_table)

    def add_translation(self):
        self.add_row_to_single_column_table(self.translations_table)

    def add_form(self):
        specs = {k: [''] + v for k, v in self.dct.features.items()}
        empty_gram_form = tuple('' for _ in range(len(self.dct.features)))

        res, ok = OptionsDialog.get_settings(
            specs, empty_gram_form, 'Set grammatical form', validator=valid_gram_form
        )
        if not ok:
            return
        new_gram_form = tuple(res.values())

        self.add_row_to_two_column_table(self.forms_table, False, new_gram_form)
        n_rows = self.forms_table.rowCount()
        self.forms_table.item(n_rows - 1, 0).setText(gram_form_to_str(new_gram_form))

    def add_phrase(self):
        self.add_row_to_two_column_table(self.phrases_table)

    def add_note(self):
        self.add_row_to_single_column_table(self.notes_table)

    def add_tag(self):
        new_tag, is_default, ok = InputTagDialog.get_input(self.dct, parent=self)
        if ok and new_tag:
            self.dct.add_tag(new_tag, is_default)
            self.tags_list.add_item(new_tag, True)

    @staticmethod
    def _delete_selected_table_rows(table: QTableWidget):
        rows_to_delete = {i.row() for i in table.selectedItems()}
        for row in sorted(rows_to_delete, reverse=True):
            table.removeRow(row)

    def delete_lemma_variants(self, _row, _column):
        table = self.lemma_variants_table
        if len(table.selectedIndexes()) >= table.rowCount():
            QMessageBox.critical(
                self,
                'Error',
                'Cannot delete all lemma variants.',
            )
            return
        self._delete_selected_table_rows(table)

    def delete_translations(self, _row, _column):
        table = self.translations_table
        if len(table.selectedIndexes()) >= table.rowCount():
            QMessageBox.critical(
                self,
                'Error',
                'Cannot delete all entry translations.',
            )
            return
        self._delete_selected_table_rows(table)

    def delete_forms(self, _row, _column):
        self._delete_selected_table_rows(self.forms_table)

    def delete_phrases(self, _row, _column):
        self._delete_selected_table_rows(self.phrases_table)

    def delete_notes(self, _row, _column):
        self._delete_selected_table_rows(self.notes_table)

    def save_and_close(self):
        is_ok = all(status == '' for status in self.statuses.values())
        if not is_ok:
            QMessageBox.critical(
                self,
                'Error',
                'Cannot apply your changes while there are invalid values (highlighted in red).',
            )
            return

        lemma_variants = [
            self.replacer.replace(s)
            for s in get_column_data(self.lemma_variants_table, 0)
        ]
        translations = [
            self.replacer.replace(s)
            for s in get_column_data(self.translations_table, 0)
        ]
        forms = {
            gf: [self.replacer.replace(wf) for wf in wfs]
            for gf, wfs in self.get_forms_data(self.forms_table).items()
        }
        phrases = {
            self.replacer.replace(ph): [self.replacer.replace(pt) for pt in pts]
            for ph, pts in self.get_phrases_data(self.phrases_table).items()
        }
        notes = [
            self.replacer.replace(s)
            for s in get_column_data(self.notes_table, 0)
        ]
        tags = self.tags_list.get_checked_items()
        is_fav = self.fav_checkbox.isChecked()

        self.entry = self.dct.rewrite_entry(
            self.entry,
            lemma_variants, translations, forms, phrases, notes, tags, is_fav,
        )

        self.exit_code = 'save'
        self.accept()

    def delete_entry(self):
        self.dct.delete_entry(self.entry)

        self.exit_code = 'delete'
        self.accept()


class DctTabWidget(QTabWidget):
    def __init__(self, manager: Manager):
        super().__init__()

        self.manager = manager

        self.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self.show_tab_context_menu)

    def show_tab_context_menu(self, pos):
        index = self.tabBar().tabAt(pos)
        if index == -1:
            return

        menu = QMenu(self)
        save_action = menu.addAction('Save')
        save_as_action = menu.addAction('Save as...')

        action = menu.exec(self.tabBar().mapToGlobal(pos))

        if action == save_action:
            self.save_dict(index)
        elif action == save_as_action:
            self.save_dict_as(index)

    def save_dict(self, index: int):
        self.manager.save_dct(index)

    def save_dict_as(self, index: int):
        file_path, ok = select_dct_file_to_save(self)
        if not ok:
            return
        self.manager.save_dct(index, file_path)


class DctWorkspaceWidget(QWidget):
    """
    Widget representing a dictionary workspace in a tab.

    Displays dictionary entries in a table format. Provides selection
    functionality and status bar with dictionary statistics.
    """

    def __init__(self, dct_bundle: DctBundle):
        """
        Initialize the workspace widget.

        Args:
            dct: Dictionary instance to display.
        """

        super().__init__()

        # Dictionary instance for this tab
        self.dct_bundle = dct_bundle
        self.dct = dct_bundle.dct

        layout = QVBoxLayout(self)

        # Create table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(['Word', 'Translation', 'Forms', 'Phrases'])

        # Storage for selected table rows
        self.selected_rows = set()

        # Set minimum column widths
        self.table_widget.setColumnWidth(0, 150)
        self.table_widget.setColumnWidth(1, 200)
        self.table_widget.setColumnWidth(2, 200)
        self.table_widget.setColumnWidth(3, 200)

        # Configure row selection
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.ExtendedSelection)  # Multiple selection

        # Configure column resizing
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionsMovable(False)

        # Enable horizontal scrollbar
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Enable smooth scrolling (pixel-based scrolling, not item-based)
        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Disable table editing
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        # Connect double-click handler
        self.table_widget.doubleClicked.connect(self.on_item_double_clicked)
        # Connect selection handler
        self.table_widget.itemSelectionChanged.connect(self.on_selection_changed)

        layout.addWidget(self.table_widget)

        # Create status bar at the bottom
        self.status_bar = QLabel()
        self.status_bar.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.status_bar)

        # Fill the table
        self.print_entries()

        # Update status bar
        self.update_status_bar()

    def fill_table_row(self, row: int, entry: Entry):
        # Column 0: Lemma
        lemma_item = QTableWidgetItem(lemma_to_str(entry.variants))
        lemma_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 0, lemma_item)

        # Column 1: Translations
        translations_item = QTableWidgetItem(translations_to_str(entry.tr))
        translations_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 1, translations_item)

        # Column 2: Forms
        forms_item = QTableWidgetItem(forms_to_str(entry.forms))
        forms_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 2, forms_item)

        # Column 3: Phrases
        phrases_item = QTableWidgetItem(phrases_to_str(entry.phrases))
        phrases_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 3, phrases_item)

    def print_entries(self):
        """
        Populate the table with dictionary entries.

        Fills the table widget with all entries from the dictionary.
        """

        # Set row count
        n_entries = self.dct.count('lemmas')
        self.table_widget.setRowCount(n_entries)

        # Add entries to table
        for row, entry in enumerate(self.dct):
            self.fill_table_row(row, entry)

    def on_item_double_clicked(self, index):
        """
        Handle double-click event on table item.

        Opens a details dialog for the entry in the clicked cell.

        Args:
            index: QModelIndex of the clicked cell.
        """

        # Get object from cell data
        item = self.table_widget.item(index.row(), index.column())
        if item is None:
            return

        entry = item.data(Qt.UserRole)

        # Create and show details dialog
        dialog = EntryDetailsDialog(self.dct_bundle, entry, self)
        dialog.exec()
        if dialog.exit_code == 'save':
            edited_entry = dialog.entry
            self.fill_table_row(index.row(), edited_entry)
        elif dialog.exit_code == 'delete':
            self.table_widget.removeRow(item.row())

    def on_selection_changed(self):
        """
        Handle table selection change event.

        Updates the internal selection storage and refreshes the status bar
        to reflect the current selection.
        """

        # Update selected rows storage
        self.selected_rows = set(item.row() for item in self.table_widget.selectedItems())

        # Update status bar with selection info
        self.update_status_bar()

    def update_status_bar(self):
        """
        Update the status bar with dictionary statistics.

        Displays entry, translation, and form counts. If rows are selected,
        also shows selected item statistics. Updates both the status bar text
        and tooltip with full descriptions.
        """

        n_entries = self.dct.count('lemmas')
        n_translations = self.dct.count('translations')
        n_gram_forms = self.dct.count('gram_forms')
        n_word_forms = self.dct.count('word_forms')

        status_text = f'{n_entries} E, {n_translations} T, {n_gram_forms} GF, {n_word_forms} WF'
        tooltip_text = (
            f'{n_entries} entries, '
            f'{n_translations} translations, '
            f'{n_gram_forms} grammatical forms, '
            f'{n_word_forms} word forms'
        )

        if self.selected_rows:
            n_sel_entries = len(self.selected_rows)
            n_sel_translations, n_sel_gram_forms, n_sel_word_forms = 0, 0, 0
            for row in self.selected_rows:
                entry = self.table_widget.item(row, 0).data(Qt.UserRole)
                n_sel_translations += entry.n_translations
                n_sel_gram_forms += entry.n_gram_forms
                n_sel_word_forms += entry.n_word_forms
            status_text = (
                f'Selected: {n_sel_entries} E, {n_sel_translations} T, '
                f'{n_sel_gram_forms} GF, {n_sel_word_forms} WF | {status_text}'
            )
            tooltip_text += (
                f'\nSelected: '
                f'{n_sel_entries} entries, '
                f'{n_sel_translations} translations, '
                f'{n_sel_gram_forms} grammatical forms, '
                f'{n_sel_word_forms} word forms'
            )

        self.status_bar.setText(status_text)
        self.status_bar.setToolTip(tooltip_text)


class MainWindow(QMainWindow):
    """
    Main application window for Dictionary Manager.

    Manages multiple dictionary tabs, provides toolbar actions for opening
    and creating dictionaries, and handles application state persistence.
    """

    def __init__(self, app_data: AppData):
        """
        Initialize the main window.

        Args:
            app_data: The main structure with app data.
        """

        super().__init__()

        self.app_data = app_data
        self.manager = app_data.manager

        self._configure_window()
        self._create_widgets()

        self.load_state()

    def _configure_window(self):
        self.setWindowTitle('Dictionary Manager 2.0')
        self.setGeometry(100, 100, 800, 600)

    def _create_widgets(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._create_toolbar()
        self._create_tab_widget()
        self._create_placeholder()

    def _create_toolbar(self):
        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.main_layout.addWidget(self.toolbar)

        self.file_action = QAction('File', self)
        self.file_action.triggered.connect(self.show_file_menu)
        self.toolbar.addAction(self.file_action)
        self._create_file_menu()

        self.settings_action = QAction('Settings', self)
        self.settings_action.triggered.connect(self.show_settings_menu)
        self.toolbar.addAction(self.settings_action)

    def _create_file_menu(self):
        # Create File menu
        self.file_menu = QMenu(self)

        # Create button to create new dictionary
        self.new_action = QAction('New', self)
        self.new_action.triggered.connect(self.new_dict)
        self.file_menu.addAction(self.new_action)

        # Create button to open a dictionary
        self.open_action = QAction('Open', self)
        self.open_action.triggered.connect(self.open_dict)
        self.file_menu.addAction(self.open_action)

    def _create_tab_widget(self):
        # Create tab widget
        self.tab_widget = DctTabWidget(self.manager)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setVisible(False)  # Hide initially
        self.tab_widget.setMovable(True)
        self.main_layout.addWidget(self.tab_widget)

        # Enable double click for renaming tabs
        self.tab_widget.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.tab_widget.tabBar().setTabButton(0, QTabBar.LeftSide, None)
        self.tab_widget.tabBar().tabBarDoubleClicked.connect(self.on_tab_renamed)

        # Connect signal for tab movement
        self.tab_widget.tabBar().tabMoved.connect(self.on_tab_moved)

    def _create_placeholder(self):
        # Create placeholder for empty workspace
        self.placeholder = QLabel('No dictionary open')
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.placeholder)

    def show_file_menu(self):
        """Show the File dropdown menu below the File button."""

        # Get the widget for the File button
        button_widget = self.toolbar.widgetForAction(self.file_action)
        if button_widget:
            # Calculate position for the menu - below the button
            pos = button_widget.mapToGlobal(button_widget.rect().bottomLeft())
            # Show the menu at this position
            self.file_menu.exec(pos)

    def show_settings_menu(self):
        pass

    def on_tab_changed(self, index):
        """
        Handle tab switching event.

        Updates the manager's current dictionary to match the selected tab.

        Args:
            index: Index of the newly selected tab, or -1 if no tab is selected.
        """

        if index >= 0:
            self.manager.switch_dct(index)

    def on_tab_moved(self, to_index, from_index):
        """Handle tab movement and update manager."""

        self.manager.move_dct(from_index, to_index)

    def on_tab_renamed(self, index):
        """
        Rename tab on double click.

        Args:
            index: Index of the tab, or -1 if no tab is selected.
        """

        if index >= 0:
            current_name = self.tab_widget.tabText(index)
            new_name, ok = QInputDialog.getText(
                self,
                'Rename Dictionary',
                'Enter new dictionary name:',
                text=current_name,
            )
            if ok and new_name:
                self.tab_widget.setTabText(index, new_name)
                self.manager.rename_dct(index, new_name)

    def create_new_tab(
            self,
            title: str,
            dct_bundle: DctBundle | None = None,
            set_active: bool = True,
    ):
        """
        Create a new tab with a dictionary workspace.

        Args:
            title: Tab title.
            dct_bundle: Dictionary to use. If None, uses the manager's current dictionary.
            set_active: Whether to set the new tab as active. Default True.
        """

        # Use provided dictionary or current one from manager
        if dct_bundle is None:
            dct_bundle = self.manager.active

        # Create new workspace
        workspace = DctWorkspaceWidget(dct_bundle)

        # Add tab
        self.tab_widget.addTab(workspace, title)

        # Set new tab as active if requested
        if set_active:
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

        # Show tab widget if it was hidden
        if not self.tab_widget.isVisible():
            self.tab_widget.setVisible(True)
            self.placeholder.setVisible(False)

    def close_tab(self, index):
        """
        Handle tab closing event.

        Closes the dictionary in the manager and removes the tab from the UI.
        Shows placeholder if no tabs remain.

        Args:
            index: Index of the tab to close.
        """

        self.manager.close_dct(index)
        self.tab_widget.removeTab(index)

        # Hide tab widget if no tabs are open
        if self.tab_widget.count() == 0:
            self.tab_widget.setVisible(False)
            self.placeholder.setVisible(True)

    def save_state(self):
        """
        Save application state to file.

        Serializes the dictionary manager state (opened dictionaries and
        current selection) and saves it to the configured save path.
        """

        self.app_data.save()

    def load_state(self):
        """
        Load application state from file and restore opened tabs.

        Deserializes the dictionary manager state and recreates all tabs
        that were open in the previous session. Restores the active tab
        selection.
        """

        try:
            # Restore tabs for all opened dictionaries
            if self.manager.opened_dct_bundles:
                # Temporarily disconnect signal to avoid calling switch_dct during restoration
                self.tab_widget.currentChanged.disconnect()

                for dct_bundle in self.manager.opened_dct_bundles:
                    dct = dct_bundle.dct
                    self.create_new_tab(dct.name, dct_bundle, set_active=False)

                # Restore active tab
                if self.manager.active_dct_id is not None:
                    self.tab_widget.setCurrentIndex(self.manager.active_dct_id)

                # Reconnect signal
                self.tab_widget.currentChanged.connect(self.on_tab_changed)
        except Exception as e:  # TODO: specify error types
            print(e)  # TODO: handling

    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event.

        Saves application state before closing the window.

        Args:
            event: Close event from Qt.
        """

        for index, dct_bundle in enumerate(self.manager.opened_dct_bundles):
            dct = dct_bundle.dct
            if dct.is_modified:
                to_save = ask_yes_no(self, 'Unsaved changes', f'Save dictionary {dct.name}?')
                if to_save:
                    file_path = dct_bundle.filepath
                    if not file_path:
                        file_path, ok = select_dct_file_to_save(self)
                        if not ok:
                            continue
                    self.manager.save_dct(index, file_path)
                elif dct_bundle.filepath is None:
                    self.close_tab(index)

        self.save_state()
        event.accept()

    def open_dict(self):
        """
        Open a dictionary from file.

        Shows a file dialog to select a dictionary file, opens it in the
        manager, and creates a new tab for the opened dictionary.
        """

        file_path, ok = select_dct_file_to_load(self)
        if not ok:
            return
        self.manager.open_dct(file_path, to_activate=True)

        dict_name = self.manager.active.dct.name
        self.create_new_tab(dict_name, set_active=True)

    def new_dict(self):
        """
        Create a new empty dictionary.

        Creates a new dictionary with default name and opens it in a new tab.
        """

        new_dict_name = 'Untitled'
        self.manager.create_dct(name=new_dict_name)
        self.create_new_tab(new_dict_name)


if __name__ == '__main__':
    savepath = './resources/app_data.json'  # TODO: replace with real path
    app_data = AppData(savepath, 'qt')
    app_data.load()

    app = QApplication(sys.argv)
    window = MainWindow(app_data)
    window.show()
    sys.exit(app.exec())
