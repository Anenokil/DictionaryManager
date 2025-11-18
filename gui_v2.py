from typing import Generator, Collection
import sys
import pickle
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QToolBar, QTabWidget, QLabel, QMenu,
    QTableWidget, QTableWidgetItem, QDialog,
    QDialogButtonBox, QFormLayout, QLineEdit,
    QHeaderView, QAbstractItemView, QFileDialog,
    QInputDialog, QTabBar, QPushButton, QCheckBox,
)
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtCore import Qt

from backend import Translations, Forms, Phrases, Entry, Dictionary, Manager, pattern_to_str


def forms_to_pairs(forms: Forms) -> Generator[tuple[str, str], None, None]:
    for pattern, form in forms.items():
        yield pattern_to_str(pattern), form


def phrases_to_pairs(phrases: Phrases) -> Generator[tuple[str, str], None, None]:
    for phrase, translations in phrases.items():
        for tr in translations:
            yield phrase, tr


def translations_to_str(tr: Translations) -> str:
    return ', '.join(tr)


def forms_to_str(forms: Forms) -> str:
    return '\n'.join(f'[{pattern_to_str(pattern)}] {form}'
                     for pattern, form in forms.items())


def phrases_to_str(phrases: Phrases) -> str:
    add_quotes = lambda lst: (f'"{s}"' for s in lst)
    return '\n'.join(f'"{phrase}": ' + ', '.join(add_quotes(phrase_tr))
                     for phrase, phrase_tr in phrases.items())


class EntryDetailsDialog(QDialog):
    """Dialog for displaying entry information."""

    def __init__(self, entry: Entry, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Entry "{entry.lemma}"')
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Form for displaying entry data
        form_layout = QFormLayout(labelAlignment=Qt.AlignRight | Qt.AlignVCenter)

        # Add entry data fields
        self.lemma_edit = QLineEdit(entry.lemma)
        #self.lemma_edit.setReadOnly(True)
        form_layout.addRow('Lemma:', self.lemma_edit)

        # Translations table
        translations_label = QLabel('Translations:')
        self.translations_table = self.create_single_column_table(entry.tr)
        form_layout.addRow(translations_label, self.translations_table)

        # Forms table
        forms_label = QLabel('Forms:')
        self.forms_table = self.create_two_column_table(list(forms_to_pairs(entry.forms)), is_1_col_active=False)
        form_layout.addRow(forms_label, self.forms_table)

        # Phrases table
        phrases_label = QLabel('Phrases:')
        self.phrases_table = self.create_two_column_table(list(phrases_to_pairs(entry.phrases)))
        form_layout.addRow(phrases_label, self.phrases_table)

        # Notes table
        notes_label = QLabel('Notes:')
        self.notes_table = self.create_single_column_table(entry.notes)
        form_layout.addRow(notes_label, self.notes_table)

        # Groups table
        groups_label = QLabel('Groups:')
        self.groups_table = self.create_single_column_table(entry.groups, is_active=False)
        form_layout.addRow(groups_label, self.groups_table)

        # Fav checkbox
        fav_label = QLabel('Favorite:')
        self.fav_checkbox = QCheckBox()
        self.fav_checkbox.setChecked(entry.fav)
        form_layout.addRow(fav_label, self.fav_checkbox)

        layout.addLayout(form_layout)

        # Dialog buttons
        buttons = QDialogButtonBox()

        self.save_button = QPushButton('Save')
        self.close_button = QPushButton('Close')

        buttons.addButton(self.save_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(self.close_button, QDialogButtonBox.RejectRole)

        self.save_button.clicked.connect(self.save_and_close)
        self.close_button.clicked.connect(self.reject)

        layout.addWidget(buttons)

    @staticmethod
    def create_single_column_table(content: Collection[str], is_active: bool = True) -> QTableWidget:
        """Create a single-column table with the given data."""

        table = QTableWidget()

        # Set up the table with one column
        table.setColumnCount(1)

        # Hide the horizontal header
        table.horizontalHeader().setVisible(False)

        # Enable editing if requested
        if is_active:
            table.setEditTriggers(QTableWidget.AllEditTriggers)
        else:
            table.setEditTriggers(QTableWidget.NoEditTriggers)

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
    def create_two_column_table(content: Collection[tuple[str, str]], is_1_col_active: bool = True) -> QTableWidget:
        """Create a two-column table with the given data."""

        table = QTableWidget()

        # Set up the table with two columns
        table.setColumnCount(2)

        # Hide the horizontal header
        table.horizontalHeader().setVisible(False)

        # Enable editing
        table.setEditTriggers(QTableWidget.AllEditTriggers)

        # Allow selecting individual cells or rows
        table.setSelectionBehavior(QTableWidget.SelectItems)
        table.setSelectionMode(QTableWidget.SingleSelection)

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

    def save_and_close(self):
        pass


class WorkspaceWidget(QWidget):
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

    def print_entries(self):
        """
        Populate the table with dictionary entries.

        Fills the table widget with all entries from the dictionary.
        """

        # Set row count
        n_entries = self.dct.count('lemmas')
        self.table_widget.setRowCount(n_entries)

        # Add entries to table
        for row, entry in enumerate(self.dct.get_entries()):
            # Column 0: Lemma
            lemma_item = QTableWidgetItem(entry.lemma)
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

    def on_item_double_clicked(self, index):
        """
        Handle double-click event on table item.

        Opens a details dialog for the entry in the clicked cell.

        Args:
            index: QModelIndex of the clicked cell.
        """

        # Get object from cell data
        item = self.table_widget.item(index.row(), index.column())
        if item:
            entry = item.data(Qt.UserRole)

            # Create and show details dialog
            dialog = EntryDetailsDialog(entry, self)
            dialog.exec()

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
        n_forms = self.dct.count('forms')

        status_text = f'{n_entries} E, {n_translations} T, {n_forms} F'
        tooltip_text = f'{n_entries} entries, {n_translations} translations, {n_forms} forms'

        if self.selected_rows:
            n_sel_entries = len(self.selected_rows)
            n_sel_translations, n_sel_forms = 0, 0
            for row in self.selected_rows:
                entry = self.table_widget.item(row, 0).data(Qt.UserRole)
                n_sel_translations += entry.count_t
                n_sel_forms += entry.count_f
            status_text = (
                f'Selected: {n_sel_entries} E, {n_sel_translations} T, '
                f'{n_sel_forms} F | {status_text}'
            )
            tooltip_text = (
                f'Selected: {n_sel_entries} entries, '
                f'{n_sel_translations} translations, {n_sel_forms} forms | '
                f'{tooltip_text}'
            )

        self.status_bar.setText(status_text)
        self.status_bar.setToolTip(tooltip_text)


class MainWindow(QMainWindow):
    """
    Main application window for Dictionary Manager.

    Manages multiple dictionary tabs, provides toolbar actions for opening
    and creating dictionaries, and handles application state persistence.
    """

    def __init__(self, savepath: str):
        """
        Initialize the main window.

        Args:
            savepath: Path to the file for saving/loading application state.
        """

        super().__init__()
        self.setWindowTitle('Dictionary Manager 2.0')
        self.setGeometry(100, 100, 800, 600)

        # Path for saving/loading application state
        self.savepath = savepath

        # Create dictionary manager instance
        self.manager = Manager()

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        layout.addWidget(self.toolbar)

        # Create Settings button
        self.settings_action = QAction('Settings', self)
        self.settings_action.triggered.connect(self.show_settings_menu)
        self.toolbar.addAction(self.settings_action)

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

        # Create Dictionaries button with manual menu handling
        self.dictionaries_action = QAction('Dictionaries', self)
        self.dictionaries_action.triggered.connect(self.show_dictionaries_menu)
        self.toolbar.addAction(self.dictionaries_action)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setVisible(False)  # Hide initially
        self.tab_widget.setMovable(True)
        layout.addWidget(self.tab_widget)

        # Enable double click for renaming tabs
        self.tab_widget.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.tab_widget.tabBar().setTabButton(0, QTabBar.LeftSide, None)
        self.tab_widget.tabBar().tabBarDoubleClicked.connect(self.rename_dict)

        # Connect signal for tab movement
        self.tab_widget.tabBar().tabMoved.connect(self.on_tab_moved)

        # Create placeholder for empty workspace
        self.placeholder = QLabel('No dictionary open')
        self.placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.placeholder)

        self.load_state()

    def show_dictionaries_menu(self):
        """Show the Dictionaries dropdown menu below the Dictionaries button."""

        # Get the widget for the Dictionaries button
        button_widget = self.toolbar.widgetForAction(self.dictionaries_action)
        if button_widget:
            # Calculate position for the menu - below the button
            pos = button_widget.mapToGlobal(button_widget.rect().bottomLeft())
            # Show the menu at this position
            self.dictionaries_menu.exec(pos)

    def on_tab_moved(self, to_index, from_index):
        """Handle tab movement and update manager."""

        self.manager.reorder(from_index, to_index)

    def save_state(self):
        """
        Save application state to file.

        Serializes the dictionary manager state (opened dictionaries and
        current selection) and saves it to the configured save path.
        """

        with open(self.savepath, 'wb') as f:
            savedata = self.manager.serialize()
            pickle.dump(savedata, f)

    def load_state(self):
        """
        Load application state from file and restore opened tabs.

        Deserializes the dictionary manager state and recreates all tabs
        that were open in the previous session. Restores the active tab
        selection.
        """

        try:
            with open(self.savepath, 'rb') as f:
                savedata = pickle.load(f)
            self.manager.deserialize(savedata)

            # Restore tabs for all opened dictionaries
            if self.manager.opened_dct_info:
                # Temporarily disconnect signal to avoid calling switch_dct during restoration
                self.tab_widget.currentChanged.disconnect()

                for dct_info in self.manager.opened_dct_info:
                    dct = dct_info['dct']
                    self.create_new_tab(dct.name, dct, set_active=False)

                # Restore active tab
                if self.manager.current_dct_id is not None:
                    self.tab_widget.setCurrentIndex(self.manager.current_dct_id)

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

        self.save_state()
        event.accept()

    def show_settings_menu(self):
        pass

    def open_dict(self):
        """
        Open a dictionary from file.

        Shows a file dialog to select a dictionary file, opens it in the
        manager, and creates a new tab for the opened dictionary.
        """

        file_filter = '(' + ' '.join(f'*{ext}' for ext in self.manager.allowed_file_ext) + ')'
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            caption='Open Dictionary File',
            filter=file_filter,
        )
        self.manager.open_dct(file_path)

        dict_name = self.manager.dct.name
        self.create_new_tab(dict_name)

    def new_dict(self):
        """
        Create a new empty dictionary.

        Creates a new dictionary with default name and opens it in a new tab.
        """

        new_dict_name = 'Unnamed'
        self.manager.create_dct(new_dict_name)
        self.create_new_tab(new_dict_name)

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
            dct = self.manager.dct

        # Create new workspace
        workspace = WorkspaceWidget(dct)

        # Add tab
        self.tab_widget.addTab(workspace, title)

        # Set new tab as active if requested
        if set_active:
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

        # Show tab widget if it was hidden
        if not self.tab_widget.isVisible():
            self.tab_widget.setVisible(True)
            self.placeholder.setVisible(False)

    def rename_dict(self, index):
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
                text=current_name
            )
            if ok and new_name:
                self.tab_widget.setTabText(index, new_name)
                self.manager.rename_dict(index, new_name)

    def on_tab_changed(self, index):
        """
        Handle tab switching event.

        Updates the manager's current dictionary to match the selected tab.

        Args:
            index: Index of the newly selected tab, or -1 if no tab is selected.
        """
        if index >= 0:
            self.manager.switch_dct(index)

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


if __name__ == '__main__':
    savepath = './dct_manager_savedata.pkl'  # TODO: replace with real path

    app = QApplication(sys.argv)
    window = MainWindow(savepath)
    window.show()
    sys.exit(app.exec())
