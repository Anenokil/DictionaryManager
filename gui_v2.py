from typing import Generator, Collection
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QToolBar, QTabWidget, QLabel, QMenu,
    QTableWidget, QTableWidgetItem, QDialog,
    QDialogButtonBox, QMessageBox, QFormLayout,
    QHeaderView, QAbstractItemView, QFileDialog,
    QInputDialog, QTabBar, QPushButton, QCheckBox,
)
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtCore import Qt

from backend import (
    Translations, Variants, Forms, GramForm, Phrases,
    Entry, Dictionary, Manager, gram_form_to_str,
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


class EntryDetailsDialog(QDialog):
    """Dialog for displaying entry information."""

    def __init__(self, dct: Dictionary, entry: Entry, parent: QWidget | None = None):
        super().__init__(parent)

        self.dct = dct
        self.entry = entry

        self._create_widgets()
        self._configure_window()

    def _configure_window(self):
        self.setWindowTitle(f'Entry "{lemma_to_str(self.entry.variants)}"')
        self.setModal(True)
        self.resize(500, 500)

    def _create_widgets(self):
        self.main_layout = QVBoxLayout(self)

        self._create_fields()
        self._create_buttons()

    def _create_fields(self):
        # Form for displaying entry data
        self.form_layout = QFormLayout(labelAlignment=Qt.AlignRight | Qt.AlignVCenter)
        self.main_layout.addLayout(self.form_layout)

        # Lemma variants table
        lemma_variants_label = QLabel('Lemma\nvariants:', alignment=Qt.AlignRight)
        self.lemma_variants_table = self.create_single_column_table(self.entry.variants)
        self.form_layout.addRow(lemma_variants_label, self.lemma_variants_table)

        # Translations table
        translations_label = QLabel('Translations:')
        self.translations_table = self.create_single_column_table(self.entry.tr)
        self.form_layout.addRow(translations_label, self.translations_table)

        # Forms table
        forms_label = QLabel('Forms:')
        self.forms_table = self.create_two_column_table(
            list(forms_to_pairs(self.entry.forms)),
            gram_forms=list(self.entry.forms.keys()),
            is_1_col_active=False,
        )
        self.form_layout.addRow(forms_label, self.forms_table)

        # Phrases table
        phrases_label = QLabel('Phrases:')
        self.phrases_table = self.create_two_column_table(
            list(phrases_to_pairs(self.entry.phrases))
        )
        self.form_layout.addRow(phrases_label, self.phrases_table)

        # Notes table
        notes_label = QLabel('Notes:')
        self.notes_table = self.create_single_column_table(self.entry.notes)
        self.form_layout.addRow(notes_label, self.notes_table)

        # Tags table
        tags_label = QLabel('Tags:')
        self.tags_table = self.create_single_column_table(self.entry.tags, is_active=False)
        self.form_layout.addRow(tags_label, self.tags_table)

        # Fav checkbox
        fav_label = QLabel('Favorite:')
        self.fav_checkbox = QCheckBox()
        self.fav_checkbox.setChecked(self.entry.is_fav)
        self.form_layout.addRow(fav_label, self.fav_checkbox)

    def _create_buttons(self):
        # Dialog buttons
        buttons = QDialogButtonBox()

        self.save_button = QPushButton('Save')
        self.close_button = QPushButton('Close')

        buttons.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(self.close_button, QDialogButtonBox.RejectRole)

        self.save_button.clicked.connect(self.save_and_close)
        self.close_button.clicked.connect(self.reject)

        self.main_layout.addWidget(buttons)

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

    def save_and_close(self):
        pass


class DctWorkspaceWidget(QWidget):
    """
    Widget representing a dictionary workspace in a tab.

    Displays dictionary entries in a table format. Provides selection
    functionality and status bar with dictionary statistics.
    """

    def __init__(self, dct: Dictionary):
        """
        Initialize the workspace widget.

        Args:
            dct: Dictionary instance to display.
        """

        super().__init__()

        # Dictionary instance for this tab
        self.dct = dct

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
        dialog = EntryDetailsDialog(self.dct, entry, self)
        dialog.exec()
        edited_entry = dialog.entry

        self.fill_table_row(index.row(), edited_entry)

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

        # Create Settings button
        self.settings_action = QAction('Settings', self)
        self.settings_action.triggered.connect(self.show_settings_menu)
        self.toolbar.addAction(self.settings_action)

        self._create_dictionaries_menu()

        # Create Dictionaries button with manual menu handling
        self.dictionaries_action = QAction('Dictionaries', self)
        self.dictionaries_action.triggered.connect(self.show_dictionaries_menu)
        self.toolbar.addAction(self.dictionaries_action)

    def _create_dictionaries_menu(self):
        # Create Dictionaries menu
        self.dictionaries_menu = QMenu(self)

        # Create button to open a dictionary
        self.open_action = QAction('Open', self)
        self.open_action.triggered.connect(self.open_dict)
        self.dictionaries_menu.addAction(self.open_action)

        # Create button to create new dictionary
        self.new_action = QAction('New', self)
        self.new_action.triggered.connect(self.new_dict)
        self.dictionaries_menu.addAction(self.new_action)

    def _create_tab_widget(self):
        # Create tab widget
        self.tab_widget = QTabWidget()
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

    def show_settings_menu(self):
        pass

    def show_dictionaries_menu(self):
        """Show the Dictionaries dropdown menu below the Dictionaries button."""

        # Get the widget for the Dictionaries button
        button_widget = self.toolbar.widgetForAction(self.dictionaries_action)
        if button_widget:
            # Calculate position for the menu - below the button
            pos = button_widget.mapToGlobal(button_widget.rect().bottomLeft())
            # Show the menu at this position
            self.dictionaries_menu.exec(pos)

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

    def create_new_tab(self, title: str, dct: Dictionary | None = None, set_active: bool = True):
        """
        Create a new tab with a dictionary workspace.

        Args:
            title: Tab title.
            dct: Dictionary to use. If None, uses the manager's current dictionary.
            set_active: Whether to set the new tab as active. Default True.
        """

        # Use provided dictionary or current one from manager
        if dct is None:
            dct = self.manager.active.dct

        # Create new workspace
        workspace = DctWorkspaceWidget(dct)

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
                    self.create_new_tab(dct.name, dct, set_active=False)

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
