from typing import Generator, Collection, Callable, Any
from copy import deepcopy
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QScrollArea, QFrame, QWidget,
    QStackedWidget, QTabWidget, QTabBar, QToolBar, QMenu,
    QTableWidget, QTableWidgetItem, QTreeWidget,
    QTreeWidgetItem, QDialog, QInputDialog, QFileDialog,
    QDialogButtonBox, QPushButton, QGroupBox, QMessageBox, QComboBox,
    QCheckBox, QLineEdit, QTextEdit, QPlainTextEdit, QLabel,
    QLayout, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGridLayout, QHeaderView, QAbstractItemView, QSizePolicy,
    QStyle, QStyledItemDelegate,
)
from PySide6.QtGui import (
    QAction, QCloseEvent, QIcon, QPixmap, QColor, QBrush,
    QShortcut, QKeySequence, QValidator,
)
from PySide6.QtCore import Qt, QSize, QTimer, Signal, QPoint

from backend import (
    Translations, Variants, Forms, GramForm, Phrases, Notes,
    Tags, Entry, Dictionary, DctBundle, Manager, gram_form_to_str,
    TrainingFormat, TrainingOrder, EntrySelection, FormSelection,
    Replacer,
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


def notes_to_str(notes: Notes) -> str:
    return ', '.join(notes)


def tags_to_str(tags: Tags) -> str:
    tags = sorted(tags, key=lambda s: (s.lower(), s))
    return ', '.join(tags)


def accuracy_to_str(entry: Entry) -> str:
    if entry.total_att == 0:
        return '-'
    return '{:.0%}'.format(entry.accuracy)


def select_dct_file_to_load(parent: QWidget) -> tuple[str, bool]:
    file_filter = '(*.json)'
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        caption='Open Dictionary File',
        filter=file_filter,
    )
    return file_path, bool(file_path)


def select_dct_file_to_save(parent: QWidget, dct_name: str, ext: str = 'json') -> tuple[str, bool]:
    file_filter = f'(*.{ext})'
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        caption='Open Dictionary File',
        dir=f'{dct_name}.{ext}',
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
    button.setStyleSheet('''
        QPushButton {
            border: none;
            border-radius: 4px;
            background-color: transparent;
        }
        QPushButton:hover {
            background-color: rgba(127, 127, 127, 0.12);
        }
        QPushButton:pressed {
            background-color: rgba(127, 127, 127, 0.20);
        }
        QPushButton:checked {
            background-color: rgba(210, 225, 255, 0.70);
        }
        QPushButton:checked:hover {
            background-color: rgba(190, 210, 255, 0.90);
        }
        QPushButton:checked:pressed {
            background-color: rgba(255, 225, 210, 0.70);
        }
    ''')
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


def n_selected_msg(n: int, singular: str, plural: str | None = None) -> str:
    if n == 1:
        return f'1 {singular} selected'

    if plural is None:
        plural = f'{singular}s'
    return f'{n} {plural} selected'


def show_context_menu(
        widget: QWidget,
        pos: QPoint,
        actions_config: list[
            None | tuple[
                Callable[[], str] | str,
                Callable[[], Any] | None,
                Callable[[], bool] | bool
            ]
        ],
):
    """
    Configure and show a context menu.

    Args:
        widget: Widget to attach the context menu to.
        pos: Position at which to show the menu.
        actions_config: List describing menu items. Each element can be:
                        - None — inserts a separator.
                        - (text, callback, is_active) — creates a menu action, where:
                          - text: string or zero-argument function that returns the
                                  action text (useful for dynamic labels).
                          - callback: zero-argument function called when the action is
                                      triggered, or None for a non-clickable label.
                          - is_active: bool or zero-argument function returning whether
                                       the action is currently clickable.
    """

    menu = QMenu(widget)
    action_callbacks = {}

    for entry in actions_config:
        # Separator
        if entry is None:
            menu.addSeparator()
            continue

        text, callback, is_active = entry
        if isinstance(text, Callable):
            text = text()
        if isinstance(is_active, Callable):
            is_active = is_active()
        action = menu.addAction(text)

        if (callback is None) or (not is_active):
            action.setEnabled(False)
        else:
            action_callbacks[action] = callback

    chosen = menu.exec(pos)
    if chosen in action_callbacks:
        action_callbacks[chosen]()


def setup_table_context_menu(
        table: QTableWidget,
        actions_config: list[
            None | tuple[
                Callable[[], str] | str,
                Callable[[], Any] | None,
                Callable[[], bool] | bool
            ]
        ],
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
        show_context_menu(table, table.viewport().mapToGlobal(pos), actions_config)

    table.customContextMenuRequested.connect(show_menu)


def set_widget_shortcut(key_sequence: str, widget: QWidget, action: Callable):
    shortcut = QShortcut(QKeySequence(key_sequence), widget)
    shortcut.setContext(Qt.WidgetShortcut)
    shortcut.activated.connect(action)


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
            dct_bundle: DctBundle,
            initial: tuple[str, bool] | None = None,
            parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.replacer = dct_bundle.replacer
        if initial is None:
            title = 'New tag'
            tag = ''
            is_default = False
            self.other_tags = set(dct_bundle.dct.tags)
        else:
            title = 'Edit tag'
            tag, is_default = initial
            self.other_tags = set(dct_bundle.dct.tags).difference({tag})

        self.setWindowTitle(title)

        self._line_edit = QLineEdit(tag)
        self._is_default = QCheckBox('Automatically apply this tag to new entries')
        self._is_default.setChecked(is_default)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        label1 = QLabel('Tag:', alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.label_error = QLabel('', alignment=Qt.AlignHCenter)

        self.layout = QGridLayout(self)
        self.layout.addWidget(label1, 0, 0)
        self.layout.addWidget(self._line_edit, 0, 1)
        self.layout.addWidget(self._is_default, 1, 0, 1, 2, alignment=Qt.AlignBottom)
        self.layout.addWidget(buttons, 2, 0, 1, 2)

    def _validate(self) -> tuple[bool, str]:
        tag, _ = self.get_text()
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
        return self.replacer.replace(self._line_edit.text()), self._is_default.isChecked()

    @staticmethod
    def get_input(
            dct_bundle: DctBundle,
            current: tuple[str, bool] | None = None,
            parent: QWidget | None = None,
    ) -> tuple[str, bool, bool]:
        dialog = InputTagDialog(dct_bundle, current, parent)
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


class TristateCheckBox(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTristate(True)
        self._user_changed = False

    def nextCheckState(self):
        if not self._user_changed:
            if self.checkState() == Qt.PartiallyChecked:
                self.setCheckState(Qt.Unchecked)
            self._user_changed = True
            self.setTristate(False)
        super().nextCheckState()


class CheckableList(QScrollArea):
    def __init__(
            self,
            items: dict[str, Qt.CheckState],
            on_change: Callable[[], None] | None = None,
            is_tristate: bool = False,
    ):
        super().__init__()

        self._on_change = on_change

        CheckboxClass = TristateCheckBox if is_tristate else QCheckBox

        self.container = QWidget()
        layout = QVBoxLayout(self.container)
        layout.setAlignment(Qt.AlignTop)

        self.checkboxes: dict[str, CheckboxClass] = {}

        for text, state in items.items():
            checkbox = CheckboxClass(text)
            checkbox.setCheckState(state)
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

    def get_states(self) -> dict[str, Qt.CheckState]:
        return {text: cb.checkState() for text, cb in self.checkboxes.items()}

    def _update_max_height(self):
        content_height = self.container.sizeHint().height()
        frame = self.frameWidth() * 2
        full_height = content_height + frame
        self.setMaximumHeight(max(full_height, self.minimumHeight()))
        if self._on_change is not None:
            self._on_change()


class EditableTagList(QTableWidget):
    def __init__(self, replacer: Replacer, items: dict[str, bool], parent=None):
        super().__init__(0, 2, parent)

        self.replacer = replacer
        self.init_tags = set(items)

        self.setHorizontalHeaderLabels(['Tag', 'Default'])
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.setSelectionMode(QTableWidget.ExtendedSelection)
        self.setSelectionBehavior(QTableWidget.SelectRows)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.itemChanged.connect(self.on_item_changed)
        self.model().rowsRemoved.connect(self.on_rows_removed)

        for tag, is_default in items.items():
            self.add_tag(tag, is_default)

        setup_table_context_menu(self, [
            (lambda: n_selected_msg(self.n_selected_tags(), 'tag'), None, False),
            None,
            ('Delete', self.delete_tags, True),
        ])

    def n_selected_tags(self) -> int:
        return len(self.selectedIndexes()) // self.columnCount()

    def add_tag(self, tag: str, is_default: bool = False, is_new: bool = False):
        row = self.rowCount()
        self.insertRow(row)

        tag_item = QTableWidgetItem(tag)
        tag_item.setData(Qt.UserRole, None if is_new else tag)  # Store initial value
        tag_item.setFlags(tag_item.flags() | Qt.ItemIsEditable)
        self.setItem(row, 0, tag_item)

        checkbox = QCheckBox()
        checkbox.setChecked(is_default)

        checkbox_container = QWidget()
        checkbox_container.checkbox = checkbox
        layout = QHBoxLayout(checkbox_container)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setCellWidget(row, 1, checkbox_container)

        checkbox_item = QTableWidgetItem()
        checkbox_item.setData(Qt.UserRole, None if is_new else is_default)
        self.setItem(row, 1, checkbox_item)

        if is_new:
            # Set focus on the new cell
            self.setCurrentCell(row, 0)
            self.editItem(self.item(row, 0))

    def delete_tags(self):
        selected_rows = {item.row() for item in self.selectedIndexes()}
        for row in selected_rows:
            self.removeRow(row)

    def validate_and_update(self) -> bool:
        all_ok = True
        tags = get_column_data(self, 0)

        for row in range(self.rowCount()):
            item = self.item(row, 0)
            tag = self.replacer.replace(item.text())

            # Validate
            if tag == '':
                error_msg = 'Tag name must not be empty'
                ok = False
            elif tags.count(tag) > 1:
                error_msg = f'Tag "{tag}" is a duplicate'
                ok = False
            else:
                error_msg = ''
                ok = True

            all_ok &= ok

            # Update UI
            if ok:
                item.setBackground(QBrush())
                item.setToolTip('')
            else:
                item.setBackground(QBrush(QColor('#ffcccc')))
                item.setToolTip(error_msg)

        return all_ok

    def on_item_changed(self):
        self.validate_and_update()

    def on_rows_removed(self, parent, first: int, last: int):
        self.validate_and_update()

    def get_changes(self) -> tuple[dict[str, bool], dict[str, str], dict[str, bool], set[str]]:
        new_tags = {}
        renamed_tags = {}
        checked_tags = {}
        deleted_tags = self.init_tags.copy()

        for row in range(self.rowCount()):
            tag_item = self.item(row, 0)
            checked_item = self.item(row, 1)

            old_tag = tag_item.data(Qt.UserRole)
            new_tag = self.replacer.replace(tag_item.text())
            was_checked = checked_item.data(Qt.UserRole)
            is_checked = self.cellWidget(row, 1).checkbox.isChecked()

            if old_tag is None:
                new_tags[new_tag] = is_checked
            else:
                deleted_tags.remove(old_tag)
                if new_tag != old_tag:
                    renamed_tags[old_tag] = new_tag
                if is_checked != was_checked:
                    checked_tags[new_tag] = is_checked

        return new_tags, renamed_tags, checked_tags, deleted_tags


class TaggingDialog(QDialog):
    def __init__(
            self,
            dct_bundle: DctBundle,
            specs: dict[str, Qt.CheckState],
            title: str,
    ):
        super().__init__()

        self.dct_bundle = dct_bundle
        self.dct = dct_bundle.dct

        self.setWindowTitle(title)

        self.tags_list = CheckableList(
            {
                tag: specs[tag]
                for tag in sorted(self.dct.tags, key=lambda s: (s.lower(), s))
            },
            is_tristate=True,
        )
        self.tags_list.setWidgetResizable(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        add_tag_button = create_img_button('resources/qt/images/add.png')
        add_tag_button.clicked.connect(self.add_tag)
        buttons.addButton(add_tag_button, QDialogButtonBox.ActionRole)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tags_list)
        layout.addWidget(buttons)

    def add_tag(self):
        new_tag, is_default, ok = InputTagDialog.get_input(self.dct_bundle, parent=self)
        if ok and new_tag:
            self.dct.add_tag(new_tag, is_default)
            self.tags_list.add_item(new_tag, True)

    def get_values(self) -> dict[str, Qt.CheckState]:
        return self.tags_list.get_states()

    @staticmethod
    def get_settings(
            dct_bundle: DctBundle,
            specs: dict[str, Qt.CheckState],
            title: str,
    ) -> tuple[dict[str, Qt.CheckState] | None, bool]:
        dialog = TaggingDialog(dct_bundle, specs, title)
        ok = dialog.exec() == QDialog.Accepted
        values = dialog.get_values() if ok else None
        return values, ok


class ManageTagsDialog(QDialog):
    def __init__(self, dct_bundle: DctBundle):
        super().__init__()

        self.dct = dct_bundle.dct

        self.setWindowTitle('Tags')

        self.tags_list = EditableTagList(dct_bundle.replacer, {
            tag: self.dct.is_default_tag(tag)
            for tag in sorted(self.dct.tags, key=lambda s: (s.lower(), s))
        })
        self.tags_list.setItemDelegate(ColoredCellDelegate(self.tags_list))

        buttons = QDialogButtonBox()

        add_tag_button = create_img_button('resources/qt/images/add.png')
        add_tag_button.clicked.connect(self.add_tag)
        buttons.addButton(add_tag_button, QDialogButtonBox.ActionRole)

        self.close_button = QPushButton('Discard')
        buttons.rejected.connect(self.reject)
        buttons.addButton(self.close_button, QDialogButtonBox.RejectRole)

        self.save_button = QPushButton('Save')
        buttons.accepted.connect(self.save_and_close)
        buttons.addButton(self.save_button, QDialogButtonBox.AcceptRole)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tags_list)
        layout.addWidget(buttons)

    def add_tag(self):
        self.tags_list.add_tag('', False, is_new=True)

    def save_and_close(self):
        ok = self.tags_list.validate_and_update()
        if not ok:
            QMessageBox.critical(
                self,
                'Error',
                'Cannot apply your changes while there are invalid values (highlighted in red).'
            )
            return

        new_tags, renamed_tags, checked_tags, deleted_tags = self.tags_list.get_changes()

        for tag in deleted_tags:
            self.dct.delete_tag(tag)
        self.dct.rename_tags(renamed_tags)
        for tag, is_default in checked_tags.items():
            if is_default:
                self.dct.mark_tag_as_default(tag)
            else:
                self.dct.unmark_tag_as_default(tag)
        for tag, is_default in new_tags.items():
            self.dct.add_tag(tag, is_default)

        self.accept()


class GramFeaturesTree(QTreeWidget):
    def __init__(
            self,
            replacer: Replacer,
            features: dict[str, list[str]],
            parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.replacer = replacer
        self.init_categories = set(features.keys())
        self.init_values = {ctg: set(values) for ctg, values in features.items()}

        self.setHeaderHidden(True)
        self.setEditTriggers(QTreeWidget.DoubleClicked | QTreeWidget.EditKeyPressed)
        self.setSelectionMode(QTreeWidget.SingleSelection)

        self.itemChanged.connect(self.on_item_changed)
        self.model().rowsRemoved.connect(self.on_rows_removed)
        self.model().rowsInserted.connect(self.on_rows_inserted)

        for category, values in features.items():
            self.add_category(category, values)

        self.expandAll()

    def add_category(self, name: str = '', values: list[str] | None = None):
        item = QTreeWidgetItem([name])
        item.setData(0, Qt.UserRole, name or None)  # Store initial value
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.addTopLevelItem(item)
        for value in values or []:
            self.add_value(item, value)

    def add_value(self, category_item: QTreeWidgetItem, value: str = ''):
        child = QTreeWidgetItem([value])
        child.setData(0, Qt.UserRole, value or None)  # Store initial value
        child.setFlags(child.flags() | Qt.ItemIsEditable)
        category_item.addChild(child)

    def is_category(self, item: QTreeWidgetItem) -> bool:
        return item.parent() is None

    def delete_item(self, item: QTreeWidgetItem):
        if self.is_category(item):
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)
        else:
            item.parent().removeChild(item)

    def validate_and_update(self) -> bool:
        def update_ui(item: QTreeWidgetItem, is_ok: bool):
            if is_ok:
                item.setBackground(0, QBrush())
                item.setToolTip(0, '')
            else:
                item.setBackground(0, QBrush(QColor('#ffcccc')))
                item.setToolTip(0, error_msg)

        all_ok = True

        categories = [
            self.replacer.replace(self.topLevelItem(i).text(0))
            for i in range(self.topLevelItemCount())
        ]
        for i in range(self.topLevelItemCount()):
            category_item = self.topLevelItem(i)
            category = self.replacer.replace(category_item.text(0))

            # Validate category name
            if category == '':
                error_msg = 'Category name must not be empty'
                ok = False
            elif categories.count(category) > 1:
                error_msg = f'Category "{category}" is a duplicate'
                ok = False
            else:
                error_msg = ''
                ok = True

            all_ok &= ok
            update_ui(category_item, ok)

            values = [
                self.replacer.replace(category_item.child(j).text(0))
                for j in range(category_item.childCount())
            ]
            for j in range(category_item.childCount()):
                value_item = category_item.child(j)
                value = self.replacer.replace(value_item.text(0))

                # Validate category value
                if value == '':
                    error_msg = 'Category value must not be empty'
                    ok = False
                elif values.count(value) > 1:
                    error_msg = f'Category value "{value}" is a duplicate'
                    ok = False
                else:
                    error_msg = ''
                    ok = True

                all_ok &= ok
                update_ui(value_item, ok)

        return all_ok

    def on_item_changed(self):
        self.validate_and_update()

    def on_rows_inserted(self, parent, first: int, last: int):
        self.validate_and_update()

        index = self.model().index(first, 0, parent)
        item = self.itemFromIndex(index)
        self.setCurrentItem(item)
        self.editItem(item, 0)

    def on_rows_removed(self, parent, first: int, last: int):
        self.validate_and_update()

    def get_changes(self) -> tuple[
        list[str],
        list[tuple[str, str]],
        dict[str, str],
        dict[tuple[str, str], str],
        set[str],
        dict[str, set[str]],
    ]:
        new_ctgs = []
        new_values = []
        renamed_ctgs = {}
        renamed_values = {}
        deleted_ctgs = self.init_categories.copy()
        deleted_values = deepcopy(self.init_values)

        for i in range(self.topLevelItemCount()):
            category_item = self.topLevelItem(i)
            category = self.replacer.replace(category_item.text(0))
            if not category:
                continue
            category_init = category_item.data(0, Qt.UserRole)

            if category_init is None:
                new_ctgs.append(category)
            else:
                deleted_ctgs.remove(category_init)
                if category != category_init:
                    renamed_ctgs[category_init] = category

            for j in range(category_item.childCount()):
                value_item = category_item.child(j)
                value = self.replacer.replace(value_item.text(0))
                if not value:
                    continue
                value_init = value_item.data(0, Qt.UserRole)

                if value_init is None:
                    new_values.append((category, value))
                else:
                    deleted_values[category_init].remove(value_init)
                    if value != value_init:
                        renamed_values[(category, value_init)] = value

        for category_init in deleted_ctgs:
            del deleted_values[category_init]

        return new_ctgs, new_values, renamed_ctgs, renamed_values, deleted_ctgs, deleted_values


def setup_tree_context_menu(tree: GramFeaturesTree):
    tree.setContextMenuPolicy(Qt.CustomContextMenu)

    def show_menu(pos):
        item = tree.itemAt(pos)
        if item is None:
            return

        tree.setCurrentItem(item)

        menu = QMenu(tree)
        if tree.is_category(item):
            action_text = f'Delete category "{item.text(0)}" and its values'
        else:
            action_text = f'Delete value "{item.text(0)}"'
        delete_action = menu.addAction(action_text)

        chosen = menu.exec(tree.viewport().mapToGlobal(pos))
        if chosen == delete_action:
            tree.delete_item(item)

    tree.customContextMenuRequested.connect(show_menu)


class ManageGramFeaturesDialog(QDialog):
    def __init__(self, dct_bundle: DctBundle, parent: QWidget | None = None):
        super().__init__(parent)

        self.dct = dct_bundle.dct

        self.setWindowTitle('Grammatical Features')

        self.tree = GramFeaturesTree(dct_bundle.replacer, self.dct.features)
        self.tree.currentItemChanged.connect(self._update_add_value_button)
        self.tree.setItemDelegate(ColoredCellDelegate(self.tree))
        setup_tree_context_menu(self.tree)

        buttons = QDialogButtonBox()

        self.add_category_button = create_img_button('resources/qt/images/add_category.png')
        self.add_category_button.setToolTip('Add category')
        self.add_category_button.clicked.connect(self._on_add_category)
        buttons.addButton(self.add_category_button, QDialogButtonBox.ActionRole)

        self.add_value_button = create_img_button('resources/qt/images/add_value.png')
        self.add_value_button.setToolTip('Add value')
        self.add_value_button.setEnabled(self.tree.topLevelItemCount() != 0)
        self.add_value_button.clicked.connect(self._on_add_value)
        buttons.addButton(self.add_value_button, QDialogButtonBox.ActionRole)

        self.close_button = QPushButton('Discard')
        buttons.rejected.connect(self.reject)
        buttons.addButton(self.close_button, QDialogButtonBox.RejectRole)

        self.save_button = QPushButton('Save')
        buttons.accepted.connect(self.save_and_close)
        buttons.addButton(self.save_button, QDialogButtonBox.AcceptRole)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.addWidget(buttons)

    def _on_add_category(self):
        self.tree.add_category()

    def _on_add_value(self):
        current = self.tree.currentItem()
        if current is None:
            return
        category_item = current if self.tree.is_category(current) else current.parent()
        self.tree.add_value(category_item)
        category_item.setExpanded(True)

    def _update_add_value_button(self, current: QTreeWidgetItem | None, _previous=None):
        self.add_value_button.setEnabled(current is not None)

    def save_and_close(self):
        ok = self.tree.validate_and_update()
        if not ok:
            QMessageBox.critical(
                self,
                'Error',
                'Cannot apply your changes while there are invalid values (highlighted in red).'
            )
            return

        new_ctgs, new_vals, renamed_ctgs, renamed_vals, del_ctgs, del_vals = self.tree.get_changes()

        for ctg in del_ctgs:
            self.dct.delete_ctg(ctg)
        for ctg, vals in del_vals.items():
            for val in vals:
                self.dct.delete_ctg_value(ctg, val)
        self.dct.rename_ctgs(renamed_ctgs)
        self.dct.rename_ctg_values(renamed_vals)
        for ctg in new_ctgs:
            self.dct.add_ctg(ctg, [])
        for ctg, val in new_vals:
            self.dct.add_ctg_value(ctg, val)

        self.accept()


class ReplacementModifierValidator(QValidator):
    def __init__(self, options: list[str], parent: QWidget | None = None):
        super().__init__(parent)

        self.options = options

    def validate(self, text: str, pos: int):
        if text in self.options:
            return QValidator.Acceptable, text, pos
        if text == '':
            return QValidator.Intermediate, text, pos
        return QValidator.Invalid, text, pos


class ReplacementCharValidator(QValidator):
    def __init__(self, options: list[str], parent: QWidget | None = None):
        super().__init__(parent)

        self.options = options

    def validate(self, text: str, pos: int):
        if text not in self.options:
            return QValidator.Acceptable, text, pos
        if text == '':
            return QValidator.Intermediate, text, pos
        return QValidator.Invalid, text, pos


class ManageEscapeSequencesDialog(QDialog):
    def __init__(self, replacer: Replacer, parent: QWidget | None = None):
        super().__init__(parent)

        self.setWindowTitle('Escape Sequences')

        self.replacer = replacer
        self.combo_options = sorted(replacer.modifiers)
        self.rows: list[tuple[QComboBox, QLineEdit, QLineEdit, QWidget]] = []

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.rows_layout = QVBoxLayout(self.container)
        self.rows_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.container)

        for (modifier_char, input_char), output_char in replacer.replacements.items():
            is_deletable = modifier_char != input_char
            self.add_row(modifier_char, input_char, output_char, is_deletable)

        self.add_button = create_img_button('resources/qt/images/add.png')
        self.discard_button = QPushButton('Discard')
        self.save_button = QPushButton('Save')

        self.add_button.clicked.connect(
            lambda: self.add_row(sorted(replacer.modifiers)[0], '', '', True)
        )
        self.discard_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.save_and_close)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.discard_button)
        buttons_layout.addWidget(self.save_button)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(buttons_layout)

    def validate_and_update(self) -> bool:
        def update_ui(item: QComboBox | QLineEdit, error_msg: str, ok: bool):
            if ok:
                item.setStyleSheet('')
                item.setToolTip('')
            else:
                item.setStyleSheet('background-color: #ffcccc;')
                item.setToolTip(error_msg)

        input_pairs = [
            (combo.currentText(), line_edit1.text())
            for combo, line_edit1, _, _ in self.rows
        ]

        all_ok = True

        for combo, line_edit1, line_edit2, _ in self.rows:
            modifier = combo.currentText()
            input_char = line_edit1.text()
            output_char = line_edit2.text()

            if modifier not in self.combo_options:
                modifier_error_msg = 'Invalid modifier'
                modifier_ok = False
            else:
                modifier_error_msg = ''
                modifier_ok = True

            if input_char == '':
                input_error_msg = 'Input char must not be empty'
                input_ok = False
            else:
                input_error_msg = ''
                input_ok = True

            if output_char == '':
                output_error_msg = 'Output char must not be empty'
                output_ok = False
            else:
                output_error_msg = ''
                output_ok = True

            if input_pairs.count((modifier, input_char)) > 1:
                if modifier_ok and input_ok:
                    modifier_error_msg = input_error_msg = f'Sequence "{modifier}{input_char}" is a duplicate'
                    modifier_ok = input_ok = False

            update_ui(combo, modifier_error_msg, modifier_ok)
            update_ui(line_edit1, input_error_msg, input_ok)
            update_ui(line_edit2, output_error_msg, output_ok)

            all_ok &= modifier_ok & input_ok & output_ok

        return all_ok

    def on_item_changed(self):
        self.validate_and_update()

    def add_row(self, char_mod: str, char_in: str, char_out: str, is_editable: bool):
        row_container = QWidget()
        row_layout = QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)

        combo = QComboBox()
        combo.setEditable(True)
        combo.setEnabled(is_editable)
        combo.addItems(self.combo_options)
        combo.setCurrentText(char_mod)
        combo.lineEdit().setMaxLength(1)
        combo.lineEdit().setValidator(ReplacementModifierValidator(self.combo_options, combo))
        combo.setMaximumWidth(50)
        combo.editTextChanged.connect(self.on_item_changed)

        line_edit1 = QLineEdit(char_in)
        line_edit1.setEnabled(is_editable)
        line_edit1.setMaxLength(1)
        line_edit1.setValidator(ReplacementCharValidator(self.combo_options, combo))
        line_edit1.setMaximumWidth(30)
        line_edit1.textChanged.connect(self.on_item_changed)

        arrow_label = QLabel()
        arrow_label.setPixmap(QPixmap('resources/qt/images/arrow.png'))

        line_edit2 = QLineEdit(char_out)
        line_edit2.setEnabled(is_editable)
        line_edit2.setMaxLength(1)
        line_edit2.setValidator(ReplacementCharValidator(self.combo_options, combo))
        line_edit2.setMaximumWidth(30)
        line_edit2.textChanged.connect(self.on_item_changed)

        row_layout.addWidget(combo)
        row_layout.addWidget(line_edit1)
        row_layout.addWidget(arrow_label)
        row_layout.addWidget(line_edit2)

        row_data = (combo, line_edit1, line_edit2, row_container)

        if is_editable:
            delete_button = create_img_button('resources/qt/images/close.png')
            delete_button.clicked.connect(lambda: self.delete_sequence(row_data))
            row_layout.addWidget(delete_button)

        row_layout.addStretch()

        self.rows_layout.addWidget(row_container)
        self.rows.append(row_data)

        self.validate_and_update()

    def delete_row(self, row_data: tuple[QComboBox, QLineEdit, QLineEdit, QWidget]):
        self.rows.remove(row_data)
        row_container = row_data[3]
        self.rows_layout.removeWidget(row_container)
        row_container.deleteLater()

        self.validate_and_update()

    def delete_sequence(self, row_data: tuple[QComboBox, QLineEdit, QLineEdit, QWidget]):
        modifier = row_data[0].currentText()
        self.delete_row(row_data)

        same_modifier = [
            row for row in self.rows
            if row[0].currentText() == modifier
        ]
        if len(same_modifier) == 1:
            self.delete_row(same_modifier[0])

    def save_and_close(self):
        ok = self.validate_and_update()
        if not ok:
            QMessageBox.critical(
                self,
                'Error',
                'Cannot apply your changes while there are invalid values (highlighted in red).'
            )
            return

        sequences = [
            (combo.currentText(), line_edit1.text(), line_edit2.text())
            for combo, line_edit1, line_edit2, _ in self.rows
        ]
        sequences = [(m, i, o) for m, i, o in sequences if m != i]
        self.replacer.set_replacements(sequences)

        self.accept()


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

    _role_gram_form = Qt.UserRole
    _role_valid = Qt.UserRole + 1

    def __init__(
            self,
            dct_bundle: DctBundle,
            entry: Entry | None = None,
            parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.dct_bundle = dct_bundle
        self.dct = dct_bundle.dct
        self.replacer = dct_bundle.replacer
        self.entry = entry
        self.is_new = entry is None
        self.exit_code = None
        self._ignore_item_changed = False

        self._create_widgets()
        self._set_shortcuts()
        self._configure_window()

        if self.is_new:
            self.validate_and_update_table(self.lemma_variants_table)
            self.validate_and_update_table(self.translations_table)

    def _configure_window(self):
        title = 'New entry' if self.is_new else f'Entry "{lemma_to_str(self.entry.variants)}"'
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 500)

    def _create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self._create_fields()
        self._create_buttons()

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
        fav_label = QLabel('Starred:')

        # Create tables
        self.lemma_variants_table = self.create_single_column_table(
            [''] if self.is_new else [self.replacer.escape(s) for s in self.entry.variants]
        )
        self.translations_table = self.create_single_column_table(
            [''] if self.is_new else [self.replacer.escape(s) for s in self.entry.tr]
        )
        self.forms_table = self.create_two_column_table(
            [] if self.is_new else [
                (gf, self.replacer.escape(wf))
                for gf, wf in forms_to_pairs(self.entry.forms)
            ],
            gram_forms=[] if self.is_new else list(self.entry.forms.keys()),
            is_1_col_active=False,
        )
        self.phrases_table = self.create_two_column_table(
            [] if self.is_new else [
                (self.replacer.escape(ph), self.replacer.escape(pt))
                for ph, pt in phrases_to_pairs(self.entry.phrases)
            ]
        )
        self.notes_table = self.create_single_column_table(
            [] if self.is_new else [self.replacer.escape(s) for s in self.entry.notes]
        )

        self.tables = [
            self.lemma_variants_table,
            self.translations_table,
            self.forms_table,
            self.phrases_table,
            self.notes_table,
        ]

        link_exclusive_selection(self.tables)

        def delete_msg(table: QTableWidget, singular: str) -> str:
            n = len({i.row() for i in table.selectedIndexes()})
            if n == 1:
                return f'Delete 1 {singular}'
            return f'Delete {n} {singular}s'

        setup_table_context_menu(self.lemma_variants_table, [(
            lambda: delete_msg(self.lemma_variants_table, 'variant'),
            self.delete_lemma_variants,
            lambda: len(self.lemma_variants_table.selectedIndexes()) < self.lemma_variants_table.rowCount(),
        )])
        setup_table_context_menu(self.translations_table, [(
            lambda: delete_msg(self.translations_table, 'translation'),
            self.delete_translations,
            lambda: len(self.translations_table.selectedIndexes()) < self.translations_table.rowCount(),
        )])
        setup_table_context_menu(self.forms_table, [
            (lambda: delete_msg(self.forms_table, 'form'), self.delete_forms, True),
        ])
        setup_table_context_menu(self.phrases_table, [
            (lambda: delete_msg(self.phrases_table, 'phrase'), self.delete_phrases, True),
        ])
        setup_table_context_menu(self.notes_table, [
            (lambda: delete_msg(self.notes_table, 'note'), self.delete_notes, True),
        ])

        # Create other widgets
        self.tags_list = CheckableList(
            {
                tag: Qt.Checked if (not self.is_new) and (tag in self.entry.tags) else Qt.Unchecked
                for tag in sorted(self.dct.tags, key=lambda s: (s.lower(), s))
            },
            on_change=self.main_layout.activate,
        )
        self.tags_list.setWidgetResizable(True)
        self.tags_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tags_list.setMinimumHeight(50)
        self.tags_list.setMinimumWidth(120)

        self.fav_checkbox = QCheckBox()
        self.fav_checkbox.setChecked(not self.is_new and self.entry.is_fav)

        # Create image buttons
        self.add_lemma_variant_button = create_img_button('resources/qt/images/add.png')
        self.add_translation_button = create_img_button('resources/qt/images/add.png')
        self.add_form_button = create_img_button('resources/qt/images/add.png')
        self.add_phrase_button = create_img_button('resources/qt/images/add.png')
        self.add_note_button = create_img_button('resources/qt/images/add.png')
        self.add_tag_button = create_img_button('resources/qt/images/add.png')

        # Signal handling
        self.forms_table.cellDoubleClicked.connect(self.on_gram_form_double_clicked)

        self.add_lemma_variant_button.clicked.connect(self.add_lemma_variant)
        self.add_translation_button.clicked.connect(self.add_translation)
        self.add_form_button.clicked.connect(self.add_form)
        self.add_phrase_button.clicked.connect(self.add_phrase)
        self.add_note_button.clicked.connect(self.add_note)
        self.add_tag_button.clicked.connect(self.add_tag)

        # Validation for tables
        def connect_table_handlers(table: QTableWidget):
            table.itemChanged.connect(self.on_item_changed)
            table.model().rowsRemoved.connect(
                lambda *args: self.on_rows_removed(table, *args)
            )

        connect_table_handlers(self.lemma_variants_table)
        connect_table_handlers(self.translations_table)
        connect_table_handlers(self.forms_table)
        connect_table_handlers(self.phrases_table)
        connect_table_handlers(self.notes_table)

        # Custom cell coloring delegate
        self.lemma_variants_table.setItemDelegate(ColoredCellDelegate(self.lemma_variants_table))
        self.translations_table.setItemDelegate(ColoredCellDelegate(self.translations_table))
        self.forms_table.setItemDelegate(ColoredCellDelegate(self.forms_table))
        self.phrases_table.setItemDelegate(ColoredCellDelegate(self.phrases_table))
        self.notes_table.setItemDelegate(ColoredCellDelegate(self.notes_table))

        # Place widgets in the layout
        def create_field_container(table, button) -> QWidget:
            field_container = QWidget()
            field_layout = QHBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSizeConstraint(QLayout.SetMaximumSize)
            field_layout.addWidget(table)
            field_layout.addWidget(button)
            return field_container

        lemma_field_container = create_field_container(
            self.lemma_variants_table, self.add_lemma_variant_button,
        )
        translations_field_container = create_field_container(
            self.translations_table, self.add_translation_button,
        )
        forms_field_container = create_field_container(self.forms_table, self.add_form_button)
        phrases_field_container = create_field_container(self.phrases_table, self.add_phrase_button)
        notes_field_container = create_field_container(self.notes_table, self.add_note_button)
        tags_field_container = create_field_container(self.tags_list, self.add_tag_button)

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
        self.close_button = QPushButton('Discard')
        self.delete_button = QPushButton('Delete')

        buttons.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(self.close_button, QDialogButtonBox.RejectRole)
        buttons.addButton(self.delete_button, QDialogButtonBox.DestructiveRole)

        self.save_button.clicked.connect(self.save_and_close)
        self.close_button.clicked.connect(self.reject)
        self.delete_button.clicked.connect(self.delete_entry)

        if self.is_new:
            self.delete_button.setEnabled(False)

        self.main_layout.addWidget(buttons)

    def _set_shortcuts(self):
        set_widget_shortcut('Ctrl+N', self.lemma_variants_table, self.add_lemma_variant)
        set_widget_shortcut('Ctrl+N', self.translations_table, self.add_translation)
        set_widget_shortcut('Ctrl+N', self.forms_table, self.add_form)
        set_widget_shortcut('Ctrl+N', self.phrases_table, self.add_phrase)
        set_widget_shortcut('Ctrl+N', self.notes_table, self.add_note)

        QShortcut(QKeySequence('Ctrl+S'), self, self.save_and_close)
        QShortcut(QKeySequence('Ctrl+Q'), self, self.reject)

    @staticmethod
    def create_single_column_table(content: Collection[str]) -> QTableWidget:
        """Create a single-column table with the given data."""

        table = QTableWidget()
        table.setColumnCount(1)
        table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        table.setSelectionMode(QTableWidget.ExtendedSelection)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        header = table.horizontalHeader()
        header.setVisible(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Populate data
        table.setRowCount(len(content))
        for row, item in enumerate(content):
            table_item = QTableWidgetItem(item)
            table.setItem(row, 0, table_item)

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
        table.setColumnCount(2)
        table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.ExtendedSelection)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        header = table.horizontalHeader()
        table.horizontalHeader().setVisible(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Populate data
        table.setRowCount(len(content))
        for row, (item1, item2) in enumerate(content):
            table_item1 = QTableWidgetItem(item1)
            if gram_forms is not None:
                data1 = gram_forms[row]
                table_item1.setData(EntryDetailsDialog._role_gram_form, data1)
            if is_1_col_active:
                table_item1.setFlags(table_item1.flags() | Qt.ItemIsEditable)
            else:
                table_item1.setFlags(table_item1.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 0, table_item1)

            table_item2 = QTableWidgetItem(item2)
            table_item2.setFlags(table_item2.flags() | Qt.ItemIsEditable)
            table.setItem(row, 1, table_item2)

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

    def add_row_to_two_column_table(
            self,
            table: QTableWidget,
            is_1_col_active: bool = True,
            data=None,
    ):
        n_rows = table.rowCount()
        table.setRowCount(n_rows + 1)

        table_item1 = QTableWidgetItem('')
        if data is not None:
            table_item1.setData(self._role_gram_form, data)
        if is_1_col_active:
            table_item1.setFlags(table_item1.flags() | Qt.ItemIsEditable)
        else:
            table_item1.setFlags(table_item1.flags() & ~Qt.ItemIsEditable)

        table_item2 = QTableWidgetItem('')

        self._ignore_item_changed = True
        table.setItem(n_rows, 0, table_item1)
        table.setItem(n_rows, 1, table_item2)
        self._ignore_item_changed = False

        # Set focus on the new cell
        focused_column = 0 if is_1_col_active else 1
        table.setCurrentCell(n_rows, focused_column)
        table.editItem(table.item(n_rows, focused_column))

        self.validate_and_update_table(table)

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
            gram_form = table.item(row, 0).data(EntryDetailsDialog._role_gram_form)
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
            self.forms_table.item(row, 0).data(self._role_gram_form)
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

    def validate_cell(self, item: QTableWidgetItem) -> tuple[bool, str]:
        match item.tableWidget():
            case self.lemma_variants_table:
                return self.validate_lemma_variant(item.text())
            case self.translations_table:
                return self.validate_translation(item.text())
            case self.forms_table:
                if item.column() == 0:
                    return True, ''
                gram_form = self.forms_table.item(
                    item.row(), item.column() - 1
                ).data(self._role_gram_form)
                return self.validate_word_form(gram_form, item.text())
            case self.phrases_table:
                if item.column() == 0:
                    return self.validate_phrase(item.text())
                phrase = self.phrases_table.item(item.row(), item.column() - 1).text()
                return self.validate_phrase_translation(phrase, item.text())
            case self.notes_table:
                return self.validate_note(item.text())
        return False, 'Unknown table'

    def validate_and_update_table(self, table: QTableWidget):
        # Validate all cells in the table
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                item = table.item(row, column)

                ok, error_msg = self.validate_cell(item)

                self._ignore_item_changed = True

                # Update UI
                if ok:
                    item.setBackground(QBrush())
                    item.setToolTip('')
                else:
                    item.setBackground(QBrush(QColor('#ffcccc')))
                    item.setToolTip(error_msg)

                # Set cell status
                item.setData(self._role_valid, error_msg)

                self._ignore_item_changed = False

    def on_item_changed(self, item: QTableWidgetItem):
        if self._ignore_item_changed:
            return
        table = item.tableWidget()
        self.validate_and_update_table(table)

    def on_rows_removed(self, table: QTableWidget, parent, first: int, last: int):
        self.validate_and_update_table(table)

    def on_gram_form_double_clicked(self, row: int, column: int):
        if column != 0:
            return

        item = self.forms_table.item(row, column)
        if item is None:
            return

        specs = {k: [''] + v for k, v in self.dct.features.items()}
        gram_form = item.data(self._role_gram_form)
        res, ok = OptionsDialog.get_settings(
            specs, gram_form, 'Grammatical form settings', validator=valid_gram_form
        )
        if not ok:
            return
        new_gram_form = tuple(res.values())

        self.forms_table.item(row, column).setData(self._role_gram_form, new_gram_form)
        self.forms_table.item(row, column).setText(gram_form_to_str(new_gram_form))

    def validate_all(self) -> tuple[bool, str]:
        if self.is_new:
            if self.lemma_variants_table.rowCount() == 0:
                return False, 'Entry must have at least one lemma variant'
            if self.translations_table.rowCount() == 0:
                return False, 'Entry must have at least one translation'
        for table in self.tables:
            for column in range(table.columnCount()):
                for row in range(table.rowCount()):
                    cell = table.item(row, column)
                    error_msg = cell.data(self._role_valid)
                    if error_msg:
                        return (
                            False,
                            'Cannot apply your changes while there are '
                            'invalid values (highlighted in red).'
                        )
        return True, ''

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
        new_tag, is_default, ok = InputTagDialog.get_input(self.dct_bundle, parent=self)
        if ok and new_tag:
            self.dct.add_tag(new_tag, is_default)
            self.tags_list.add_item(new_tag, True)

    @staticmethod
    def _delete_selected_table_rows(table: QTableWidget):
        rows_to_delete = {i.row() for i in table.selectedItems()}
        for row in sorted(rows_to_delete, reverse=True):
            table.removeRow(row)

    def delete_lemma_variants(self):
        table = self.lemma_variants_table
        self._delete_selected_table_rows(table)

    def delete_translations(self):
        table = self.translations_table
        self._delete_selected_table_rows(table)

    def delete_forms(self):
        self._delete_selected_table_rows(self.forms_table)

    def delete_phrases(self):
        self._delete_selected_table_rows(self.phrases_table)

    def delete_notes(self):
        self._delete_selected_table_rows(self.notes_table)

    def save_and_close(self):
        is_ok, error_msg = self.validate_all()
        if not is_ok:
            QMessageBox.critical(self, 'Error', error_msg)
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

        if self.is_new:
            self.entry = self.dct.add_entry(
                lemma_variants, translations, forms, phrases, notes, tags, is_fav,
            )
            self.is_new = False
            self.delete_button.setEnabled(True)
        else:
            self.dct.rewrite_entry(
                self.entry,
                lemma_variants, translations, forms, phrases, notes, tags, is_fav,
            )

        self.exit_code = 'save'
        self.accept()

    def delete_entry(self):
        if not self.is_new:
            self.dct.delete_entry(self.entry)

        self.exit_code = 'delete'
        self.accept()


class DctTabWidget(QTabWidget):
    def __init__(self, manager: Manager):
        super().__init__()

        self.manager = manager

        self.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self.show_tab_context_menu)

    def update_tab_title(self, index: int):
        dct = self.manager.opened_dct_bundles[index].dct
        if dct.is_modified:
            self.setTabText(index, f'{dct.name} *')
        else:
            self.setTabText(index, dct.name)

    def show_tab_context_menu(self, pos):
        index = self.tabBar().tabAt(pos)
        if index == -1:
            return

        menu = QMenu(self)
        rename_action = menu.addAction('Rename...')
        menu.addSeparator()
        save_action = menu.addAction('Save')
        save_as_action = menu.addAction('Save As...')
        save_all_action = menu.addAction('Save All')
        menu.addSeparator()
        export_as_action = menu.addAction('Export As...')

        action = menu.exec(self.tabBar().mapToGlobal(pos))

        if action == rename_action:
            self.rename_dict(index)
        elif action == save_action:
            self.save_dict(index)
        elif action == save_as_action:
            self.save_dict_as(index)
        elif action == save_all_action:
            self.save_all_dicts()
        elif action == export_as_action:
            self.export_dict_as(index)

    def rename_dict(self, index):
        """
        Rename tab.

        Args:
            index: Index of the tab, or -1 if no tab is selected.
        """

        if index >= 0:
            current_name = self.manager.opened_dct_bundles[index].dct.name
            new_name, ok = QInputDialog.getText(
                self,
                'Rename Dictionary',
                'Enter new dictionary name:',
                text=current_name,
            )
            if ok and new_name:
                self.manager.rename_dct(index, new_name)
                self.update_tab_title(index)

    def save_dict(self, index: int):
        file_path = self.manager.opened_dct_bundles[index].filepath
        if file_path:
            self.manager.save_dct(index)
            self.update_tab_title(index)
        else:
            self.save_dict_as(index)

    def save_dict_as(self, index: int):
        dct_name = self.manager.opened_dct_bundles[index].dct.name
        file_path, ok = select_dct_file_to_save(self, dct_name)
        if not ok:
            return
        self.manager.save_dct(index, file_path)
        self.update_tab_title(index)

    def save_all_dicts(self):
        for index in range(len(self.manager.opened_dct_bundles)):
            self.save_dict(index)

    def export_dict_as(self, index: int):
        dct_name = self.manager.opened_dct_bundles[index].dct.name
        file_path, ok = select_dct_file_to_save(self, dct_name, ext='txt')
        if not ok:
            return
        self.manager.opened_dct_bundles[index].dct.to_txt(file_path)


class SearchBar(QFrame):
    def __init__(self, dct: Dictionary, parent: QWidget | None = None):
        super().__init__(parent)

        self.dct = dct

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText('Search')
        self.line_edit.setMaximumWidth(700)
        layout.addWidget(self.line_edit)

        self.close_btn = create_img_button('resources/qt/images/close.png', button_size=(24, 24))
        layout.addWidget(self.close_btn)

        self.match_case_btn = create_img_button('resources/qt/images/match_case.png')
        self.match_case_btn.setCheckable(True)
        layout.addWidget(self.match_case_btn)

        self.match_whole_word_btn = create_img_button('resources/qt/images/match_whole_word.png')
        self.match_whole_word_btn.setCheckable(True)
        layout.addWidget(self.match_whole_word_btn)

        self.settings_btn = create_img_button('resources/qt/images/settings.png')
        self.settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_btn)

        layout.addStretch()

        self.close_btn.clicked.connect(self.hide)
        self.setVisible(False)

    def open_settings(self):
        dialog = SearchSettingsDialog(self.dct, self)
        ok = dialog.exec() == QDialog.Accepted
        if ok:
            pass


class SearchSettingsDialog(QDialog):
    def __init__(
            self,
            dct: Dictionary,
            parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.dct = dct

        self.setWindowTitle('Search Settings')

        self._create_widgets()

    def _create_widgets(self):
        self.main_layout = QVBoxLayout(self)

        self._create_layout_settings()
        self._create_buttons()

    def _create_layout_settings(self):
        self.group_settings = QGroupBox(title='Search in:')
        self.layout_settings = QVBoxLayout(self.group_settings)

        self.combobox_starred = QComboBox()
        self.combobox_starred.addItems(
            ['All entries', 'Starred entries only', 'Unstarred entries only']
        )
        self.layout_settings.addWidget(self.combobox_starred)

        self._create_fields_settings_widgets()

        self.layout_settings.addWidget(QLabel('Target tags'))

        self.tags_list = CheckableList({tag: Qt.Unchecked for tag in self.dct.tags})
        self.layout_settings.addWidget(self.tags_list)

        self.main_layout.addWidget(self.group_settings)

    def _create_fields_settings_widgets(self):
        self.group_fields = QGroupBox(title='Target fields')
        self.layout_fields = QVBoxLayout(self.group_fields)

        self.checkbox_lemmas = QCheckBox('Lemmas')
        self.checkbox_translations = QCheckBox('Translations')
        self.checkbox_forms = QCheckBox('Forms')
        self.checkbox_phrases = QCheckBox('Phrases')
        self.checkbox_notes = QCheckBox('Notes')

        self.layout_fields.addWidget(self.checkbox_lemmas)
        self.layout_fields.addWidget(self.checkbox_translations)
        self.layout_fields.addWidget(self.checkbox_forms)
        self.layout_fields.addWidget(self.checkbox_phrases)
        self.layout_fields.addWidget(self.checkbox_notes)

        self.layout_settings.addWidget(self.group_fields)

    def _create_buttons(self):
        buttons = QDialogButtonBox()

        self.save_button = QPushButton('Save')
        self.close_button = QPushButton('Discard')

        buttons.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(self.close_button, QDialogButtonBox.RejectRole)

        self.save_button.clicked.connect(self.save_and_close)
        self.close_button.clicked.connect(self.reject)

        self.main_layout.addWidget(buttons)

    def save_and_close(self):
        pass  # TODO


class BrowsingPage(QWidget):
    on_practice_button_clicked = Signal()
    on_dct_edited = Signal()

    def __init__(self, dct_bundle: DctBundle, parent: QWidget | None = None):
        super().__init__(parent)

        self.dct_bundle = dct_bundle
        self.dct = dct_bundle.dct

        self._create_widgets()

        QShortcut(QKeySequence('Ctrl+F'), self, self.show_search_bar)
        QShortcut(QKeySequence('Esc'), self, self.hide_search_bar)

    def _create_widgets(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self._create_search_bar()
        self._create_entries_table()
        self._create_dct_buttons()
        self._create_status_bar()

    def _create_search_bar(self):
        self.search_bar = SearchBar(self.dct, self)
        self.main_layout.addWidget(self.search_bar, 0, 0, 1, 2)

    def _create_entries_table(self):
        # Create table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(11)
        self.table_widget.setHorizontalHeaderLabels([
            '', 'Word', 'Translation', 'Forms', 'Phrases', 'Notes', 'Tags',
            'Total attempts', 'Correct attempts', 'Win streak', 'Accuracy',
        ])
        self.main_layout.addWidget(self.table_widget, 1, 0, 1, 2)

        # Configure row selection
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.ExtendedSelection)  # Multiple selection

        # Configure column resizing
        header = self.table_widget.horizontalHeader()
        header.setMinimumSectionSize(20)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionsMovable(False)

        # Enable horizontal scrollbar
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Enable smooth scrolling (pixel-based scrolling, not item-based)
        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Disable table editing
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)

        # Connect signal handlers
        self.table_widget.doubleClicked.connect(self.on_item_double_clicked)
        self.table_widget.itemSelectionChanged.connect(self.on_selection_changed)

        # Setup context menu
        n_selected = lambda: n_selected_msg(len(self.get_selected_entries()), 'entry', 'entries')
        setup_table_context_menu(self.table_widget, [
            (n_selected, None, False),
            None,
            ('Manage Tags...', self.manage_entries_tags, True),
            ('Star', self.star_entries, True),
            ('Unstar', self.unstar_entries, True),
            ('Merge', self.merge_entries, lambda: len(self.get_selected_entries()) > 1),
            None,
            ('Delete', self.delete_entries, True),
        ])

        # Fill the table
        self.print_entries()

    def _create_dct_buttons(self):
        # Create button for adding new entry
        self.buttons_layout = QHBoxLayout()

        self.search_btn = create_img_button('resources/qt/images/search.png')
        self.add_entry_btn = create_img_button('resources/qt/images/add.png')
        self.manage_tags_btn = create_img_button('resources/qt/images/tag.png')
        self.manage_features_btn = create_img_button('resources/qt/images/features.png')
        self.manage_escape_sequences_btn = create_img_button('resources/qt/images/escape_seq.png')
        self.practice_btn = create_img_button('resources/qt/images/practice.png')

        self.search_btn.clicked.connect(self.toggle_search)
        self.add_entry_btn.clicked.connect(self.add_entry)
        self.manage_tags_btn.clicked.connect(self.manage_tags)
        self.manage_features_btn.clicked.connect(self.manage_features)
        self.manage_escape_sequences_btn.clicked.connect(self.manage_escape_sequences)
        self.practice_btn.clicked.connect(self.on_practice_button_clicked.emit)

        self.buttons_layout.addWidget(self.search_btn)
        self.buttons_layout.addWidget(self.add_entry_btn)
        self.buttons_layout.addWidget(self.manage_tags_btn)
        self.buttons_layout.addWidget(self.manage_features_btn)
        self.buttons_layout.addWidget(self.manage_escape_sequences_btn)
        self.buttons_layout.addWidget(self.practice_btn)

        self.main_layout.addLayout(self.buttons_layout, 2, 0)

    def _create_status_bar(self):
        self.status_bar = QLabel()
        self.status_bar.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.main_layout.addWidget(self.status_bar, 2, 1)

        self.update_status_bar()

    def show_search_bar(self):
        self.search_bar.setVisible(True)
        self.search_bar.line_edit.setFocus()
        self.search_bar.line_edit.selectAll()

    def hide_search_bar(self):
        self.search_bar.hide()

    def toggle_search(self):
        if self.search_bar.isVisible():
            self.hide_search_bar()
        else:
            self.show_search_bar()

    def fill_table_row(self, row: int, entry: Entry):
        # Column 0: Star
        star_item = QTableWidgetItem()
        if entry.is_fav:
            star_item.setIcon(QIcon('resources/qt/images/star.png'))
        star_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 0, star_item)

        # Column 1: Lemma
        lemma_item = QTableWidgetItem(lemma_to_str(entry.variants))
        lemma_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 1, lemma_item)

        # Column 2: Translations
        translations_item = QTableWidgetItem(translations_to_str(entry.tr))
        translations_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 2, translations_item)

        # Column 3: Forms
        forms_item = QTableWidgetItem(forms_to_str(entry.forms))
        forms_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 3, forms_item)

        # Column 4: Phrases
        phrases_item = QTableWidgetItem(phrases_to_str(entry.phrases))
        phrases_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 4, phrases_item)

        # Column 5: Notes
        notes_item = QTableWidgetItem(notes_to_str(entry.notes))
        notes_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 5, notes_item)

        # Column 6: Tags
        tags_item = QTableWidgetItem(tags_to_str(entry.tags))
        tags_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 6, tags_item)

        # Column 7: Total attempts
        total_att_item = QTableWidgetItem(str(entry.total_att))
        total_att_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 7, total_att_item)

        # Column 8: Correct attempts
        correct_att_item = QTableWidgetItem(str(entry.correct_att))
        correct_att_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 8, correct_att_item)

        # Column 9: Win streak
        win_streak_item = QTableWidgetItem(str(entry.win_streak))
        win_streak_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 9, win_streak_item)

        # Column 10: Accuracy
        accuracy_item = QTableWidgetItem(accuracy_to_str(entry))
        accuracy_item.setData(Qt.UserRole, entry)
        self.table_widget.setItem(row, 10, accuracy_item)

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

    def get_selected_entries(self) -> set[Entry]:
        return {item.data(Qt.UserRole) for item in self.table_widget.selectedIndexes()}

    def get_selected(self) -> set[tuple[int, Entry]]:
        return {
            (item.row(), item.data(Qt.UserRole))
            for item in self.table_widget.selectedIndexes()
        }

    def update_tab_title(self):
        self.on_dct_edited.emit()

    def add_entry(self):
        # Create and show details dialog
        dialog = EntryDetailsDialog(self.dct_bundle, None, self)
        dialog.exec()
        if dialog.exit_code == 'save':
            n_rows = self.table_widget.rowCount()
            new_entry = dialog.entry
            self.table_widget.setRowCount(n_rows + 1)
            self.fill_table_row(n_rows, new_entry)

        self.update_tab_title()

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

        self.update_tab_title()

    def manage_tags(self):
        dialog = ManageTagsDialog(self.dct_bundle)
        ok = dialog.exec() == QDialog.Accepted
        if ok:
            self.print_entries()

        self.update_tab_title()

    def manage_features(self):
        dialog = ManageGramFeaturesDialog(self.dct_bundle, self)
        ok = dialog.exec() == QDialog.Accepted
        if ok:
            self.print_entries()

        self.update_tab_title()

    def manage_escape_sequences(self):
        dialog = ManageEscapeSequencesDialog(self.dct_bundle.replacer, self)
        dialog.exec()

        self.update_tab_title()

    def on_selection_changed(self):
        """
        Handle table selection change event.

        Updates the internal selection storage and refreshes the status bar
        to reflect the current selection.
        """

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

        selected_rows = self.get_selected_entries()
        if selected_rows:
            n_sel_entries = len(selected_rows)
            n_sel_translations, n_sel_gram_forms, n_sel_word_forms = 0, 0, 0
            for entry in selected_rows:
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

    def manage_entries_tags(self):
        selected = self.get_selected()
        entries = {entry for row, entry in selected}

        specs = {}
        for tag in self.dct.tags:
            if all([tag in entry.tags for entry in entries]):
                specs[tag] = Qt.Checked
            elif all([tag not in entry.tags for entry in entries]):
                specs[tag] = Qt.Unchecked
            else:
                specs[tag] = Qt.PartiallyChecked
        res, ok = TaggingDialog.get_settings(self.dct_bundle, specs, 'Manage tags')
        if not ok:
            return

        for tag, state in res.items():
            if (tag not in specs) or (state != specs[tag]):
                if state == Qt.Checked:
                    self.dct.add_tag_to_entries(tag, entries)
                else:
                    self.dct.remove_tag_from_entries(tag, entries)

        for row, entry in selected:
            self.fill_table_row(row, entry)

        self.update_tab_title()

    def star_entries(self):
        selected = self.get_selected()
        entries = {entry for row, entry in selected}
        self.dct.add_to_fav(entries)
        for row, entry in selected:
            self.fill_table_row(row, entry)
        self.update_tab_title()

    def unstar_entries(self):
        selected = self.get_selected()
        entries = {entry for row, entry in selected}
        self.dct.remove_from_fav(entries)
        for row, entry in selected:
            self.fill_table_row(row, entry)
        self.update_tab_title()

    def merge_entries(self):
        selected = sorted(self.get_selected())
        if len(selected) <= 1:
            return

        target_row, target_entry = selected[0]
        other_rows, other_entries = zip(*selected[1:])

        for entry in other_entries:
            self.dct.merge_entries(target_entry, entry)

        for row in other_rows[::-1]:
            self.table_widget.removeRow(row)
        self.fill_table_row(target_row, target_entry)

        self.update_tab_title()

    def delete_entries(self):
        selected = sorted(self.get_selected(), reverse=True)
        for row, entry in selected:
            self.dct.delete_entry(entry)
            self.table_widget.removeRow(row)
        self.update_tab_title()


class PracticeConfigPage(QWidget):
    on_practice_button_clicked = Signal()
    on_close_button_clicked = Signal()

    def __init__(self, dct: Dictionary, parent: QWidget | None = None):
        super().__init__(parent)

        self.dct = dct

        self._create_widgets()

    def _create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self._create_settings_widgets()
        self.main_layout.addStretch()
        self._create_buttons()

    def _create_settings_widgets(self):
        exercise_options = {
            'Words: to target language': TrainingFormat.TRANS_TO_WORD,
            'Words: to native language': TrainingFormat.WORD_TO_TRANS,
            'Phrases: to target language': TrainingFormat.TRANS_TO_PHRASE,
            'Phrases: to native language': TrainingFormat.PHRASE_TO_TRANS,
            'Der-Die-Das (German)': TrainingFormat.ARTICLES_GERMAN,
        }
        order_options = {
            'Random': TrainingOrder.RANDOM,
            'Difficult first': TrainingOrder.DIFFICULT_FIRST,
        }
        entries_options = {
            'All': EntrySelection.ALL,
            'Mostly starred': EntrySelection.MOSTLY_FAV,
            'Starred only': EntrySelection.FAV,
            'Unanswered only': EntrySelection.UNANSWERED,
            '10 random': EntrySelection.RANDOM_10,
            '10 random from starred': EntrySelection.RANDOM_10_FAV,
        }
        forms_options = {
            'Lemma only': FormSelection.LEMMAS,
            'One random form': FormSelection.RANDOM,
            'Inflected only': FormSelection.INFLECTED,
            'All': FormSelection.ALL,
        }

        label = QLabel('Configure practice')
        self.main_layout.addWidget(label, alignment=Qt.AlignHCenter)

        self.settings_layout = QGridLayout()

        self.label_exercise = QLabel('Exercise:', alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.settings_layout.addWidget(self.label_exercise, 0, 0)
        self.combo_exercise = QComboBox()
        self.combo_exercise.addItems(exercise_options)
        self.settings_layout.addWidget(self.combo_exercise, 0, 1)

        self.label_entries = QLabel('Entries:', alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.settings_layout.addWidget(self.label_entries, 1, 0)
        self.combo_entries = QComboBox()
        self.combo_entries.addItems(entries_options)
        self.settings_layout.addWidget(self.combo_entries, 1, 1)

        self.label_tags = QLabel('Required tags:', alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.settings_layout.addWidget(self.label_tags, 2, 0)
        self.list_tags = CheckableList({tag: Qt.Unchecked for tag in self.dct.tags})
        self.settings_layout.addWidget(self.list_tags, 2, 1)

        self.label_forms = QLabel('Word forms:', alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.settings_layout.addWidget(self.label_forms, 3, 0)
        self.combo_forms = QComboBox()
        self.combo_forms.addItems(forms_options)
        self.settings_layout.addWidget(self.combo_forms, 3, 1)

        self.label_order = QLabel('Order:', alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.settings_layout.addWidget(self.label_order, 4, 0)
        self.combo_order = QComboBox()
        self.combo_order.addItems(order_options)
        self.settings_layout.addWidget(self.combo_order, 4, 1)

        self.label_case = QLabel('Case sensitive:', alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.settings_layout.addWidget(self.label_case, 5, 0)
        self.checkbox_case = QCheckBox()
        self.settings_layout.addWidget(self.checkbox_case, 5, 1)

        self.main_layout.addLayout(self.settings_layout)

    def _create_buttons(self):
        self.buttons_layout = QHBoxLayout()

        self.practice_btn = create_img_button('resources/qt/images/practice.png')
        self.close_btn = create_img_button('resources/qt/images/exit.png')

        self.practice_btn.clicked.connect(self.on_practice_button_clicked.emit)
        self.close_btn.clicked.connect(self.on_close_button_clicked.emit)

        self.buttons_layout.addWidget(self.practice_btn)
        self.buttons_layout.addWidget(self.close_btn)

        self.main_layout.addLayout(self.buttons_layout)


class PracticePage(QWidget):
    on_close_button_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._create_widgets()

    def _create_widgets(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.task_edit = QPlainTextEdit()
        self.task_edit.setReadOnly(True)
        self.main_layout.addWidget(self.task_edit, 0, 0, 1, 4)

        self.user_input_edit = QLineEdit()
        self.user_input_edit.setPlaceholderText('Enter your answer here')
        self.main_layout.addWidget(self.user_input_edit, 1, 0)

        self.enter_btn = create_img_button('resources/qt/images/enter.png')
        self.hint_btn = create_img_button('resources/qt/images/hint.png')
        self.stop_btn = create_img_button('resources/qt/images/stop.png')

        self.enter_btn.clicked.connect(lambda: ...)  # TODO
        self.hint_btn.clicked.connect(lambda: ...)  # TODO
        self.stop_btn.clicked.connect(self.on_close_button_clicked.emit)

        self.main_layout.addWidget(self.enter_btn, 1, 1)
        self.main_layout.addWidget(self.hint_btn, 1, 2)
        self.main_layout.addWidget(self.stop_btn, 1, 3)


class PracticeResultsPage(QWidget):
    on_close_button_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._create_widgets()

    def _create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.results_edit = QTextEdit()
        self.results_edit.setReadOnly(True)
        self.main_layout.addWidget(self.results_edit)

        self.close_btn = create_img_button('resources/qt/images/exit.png')
        self.close_btn.clicked.connect(self.on_close_button_clicked.emit)
        self.main_layout.addWidget(self.close_btn, alignment=Qt.AlignRight)


class DctWorkspaceWidget(QWidget):
    """
    Widget representing a dictionary workspace in a tab.

    Displays dictionary entries in a table format. Provides selection
    functionality and status bar with dictionary statistics.
    """

    def __init__(self, tab_widget: DctTabWidget, dct_bundle: DctBundle):
        """
        Initialize the workspace widget.

        Args:
            dct: Dictionary instance to display.
        """

        super().__init__()

        self.dct_bundle = dct_bundle
        self.dct = dct_bundle.dct

        self.tab_widget = tab_widget

        self._create_widgets()

    def _create_widgets(self):
        self.pages = QStackedWidget()

        self.browsing_page = BrowsingPage(self.dct_bundle)
        self.browsing_page.on_practice_button_clicked.connect(self.open_practice_config_page)
        self.browsing_page.on_dct_edited.connect(self.update_tab_title)

        self.practice_config_page = PracticeConfigPage(self.dct)
        self.practice_config_page.on_practice_button_clicked.connect(self.open_practice_page)
        self.practice_config_page.on_close_button_clicked.connect(self.open_browsing_page)

        self.practice_page = PracticePage()
        self.practice_page.on_close_button_clicked.connect(self.open_practice_results_page)

        self.practice_results_page = PracticeResultsPage()
        self.practice_results_page.on_close_button_clicked.connect(self.open_browsing_page)

        self.pages.addWidget(self.browsing_page)
        self.pages.addWidget(self.practice_config_page)
        self.pages.addWidget(self.practice_page)
        self.pages.addWidget(self.practice_results_page)

        layout = QVBoxLayout(self)
        layout.addWidget(self.pages)

    def open_browsing_page(self):
        self.pages.setCurrentIndex(0)

    def open_practice_config_page(self):
        self.pages.setCurrentIndex(1)

    def open_practice_page(self):
        self.pages.setCurrentIndex(2)

    def open_practice_results_page(self):
        self.pages.setCurrentIndex(3)

    def update_tab_title(self):
        self.tab_widget.update_tab_title(self.tab_widget.indexOf(self))


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

        self.settings_action = QAction('Settings', self)
        self.settings_action.triggered.connect(self.show_settings_menu)
        self.toolbar.addAction(self.settings_action)

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

        button_widget = self.toolbar.widgetForAction(self.file_action)
        if button_widget:
            pos = button_widget.mapToGlobal(button_widget.rect().bottomLeft())
            show_context_menu(self, pos, [
                ('New', self.new_dict, True),
                ('Open', self.open_dict, True),
                None,
                ('Save', self.save_dict, lambda: self.tab_widget.count() != 0),
                ('Save As...', self.save_dict_as, lambda: self.tab_widget.count() != 0),
                ('Save All', self.save_all_dicts, lambda: self.tab_widget.count() != 0),
                None,
                ('Export As...', self.export_dict_as, lambda: self.tab_widget.count() != 0),
            ])

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

        self.tab_widget.rename_dict(index)

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
        workspace = DctWorkspaceWidget(self.tab_widget, dct_bundle)

        # Add tab
        self.tab_widget.addTab(workspace, title)

        # Set new tab as active if requested
        if set_active:
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

        # Show tab widget if it was hidden
        if not self.tab_widget.isVisible():
            self.tab_widget.setVisible(True)
            self.placeholder.setVisible(False)

    def _close_tab(self, index: int):
        self.manager.close_dct(index)
        self.tab_widget.removeTab(index)

        # Hide tab widget if no tabs are open
        if self.tab_widget.count() == 0:
            self.tab_widget.setVisible(False)
            self.placeholder.setVisible(True)

    def close_tab(self, index: int):
        """
        Handle tab closing event.

        Closes the dictionary in the manager and removes the tab from the UI.
        Shows placeholder if no tabs remain.

        Args:
            index: Index of the tab to close.
        """

        dct_bundle = self.manager.opened_dct_bundles[index]
        dct = dct_bundle.dct
        if dct.is_modified:
            to_save = ask_yes_no(self, 'Unsaved changes', f'Save dictionary {dct.name}?')
            if to_save:
                file_path = dct_bundle.filepath
                if file_path:
                    self.manager.save_dct(index, file_path)
                else:
                    file_path, ok = select_dct_file_to_save(self, dct.name)
                    if ok:
                        self.manager.save_dct(index, file_path)

        self._close_tab(index)

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
                        file_path, ok = select_dct_file_to_save(self, dct.name)
                        if not ok:
                            continue
                    self.manager.save_dct(index, file_path)
                elif dct_bundle.filepath is None:
                    self._close_tab(index)

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
        self.tab_widget.update_tab_title(self.tab_widget.count() - 1)

    def save_dict(self):
        dct_index = self.manager.active_dct_id
        self.tab_widget.save_dict(dct_index)

    def save_dict_as(self):
        dct_index = self.manager.active_dct_id
        self.tab_widget.save_dict_as(dct_index)

    def save_all_dicts(self):
        self.tab_widget.save_all_dicts()

    def export_dict_as(self):
        dct_index = self.manager.active_dct_id
        self.tab_widget.export_dict_as(dct_index)


if __name__ == '__main__':
    savepath = './resources/app_data.json'  # TODO: replace with real path
    app_data = AppData(savepath, 'qt')
    app_data.load()

    app = QApplication(sys.argv)
    window = MainWindow(app_data)
    window.show()
    sys.exit(app.exec())
