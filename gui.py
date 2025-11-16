from backend import Translations, Forms, Phrases, Entry, Dictionary, Manager, pattern_to_str

import sys
import pickle
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QToolBar, QTabWidget, QMessageBox, QLabel, QMenu,
    QTableWidget, QTableWidgetItem, QDialog,
    QDialogButtonBox, QFormLayout, QLineEdit, QTextEdit,
    QHeaderView, QAbstractItemView, QFileDialog, QInputDialog, QTabBar
)
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtCore import Qt


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
    """Dialog for displaying detailed entry information."""

    def __init__(self, entry: Entry, parent=None):
        """
        Initialize the entry details dialog.

        Args:
            entry: Dictionary entry to display.
            parent: Parent widget.
        """

        super().__init__(parent)
        self.setWindowTitle(f'Entry "{entry.lemma}"')
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Form for displaying entry data
        form_layout = QFormLayout()

        layout.addLayout(form_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


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
        n_entries = self.dct.counters['lemmas']
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

        n_entries = self.dct.counters['lemmas']
        n_translations = self.dct.counters['translations']
        n_forms = self.dct.counters['forms']

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
            if self.manager.opened_dct:
                # Temporarily disconnect signal to avoid calling switch_dct during restoration
                self.tab_widget.currentChanged.disconnect()

                for dct_info in self.manager.opened_dct:
                    dct = dct_info['dct']
                    self.create_new_tab(dct.name, dct, set_active=False)

                # Restore active tab
                if self.manager.current_dct is not None:
                    self.tab_widget.setCurrentIndex(self.manager.current_dct)

                # Reconnect signal
                self.tab_widget.currentChanged.connect(self.on_tab_changed)
        except:  # TODO: specify error types
            pass

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
        dictionary = dct if dct is not None else self.manager.dct

        # Create new workspace
        workspace = WorkspaceWidget(dictionary)

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
