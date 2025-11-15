from backend import Translations, Forms, Phrases, Entry, Dictionary, Manager, pattern_to_str

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QToolBar, QTabWidget, QMessageBox, QLabel, QMenu,
    QTableWidget, QTableWidgetItem, QDialog,
    QDialogButtonBox, QFormLayout, QLineEdit, QTextEdit,
    QHeaderView, QAbstractItemView, QFileDialog
)
from PySide6.QtGui import QAction
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
    """Dialog for displaying entry information."""

    def __init__(self, entry: Entry, parent=None):
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
    """Widget for tab workspace."""

    def __init__(self, dct: Dictionary):
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

        # Configure column resizing (columns are resizable)
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
        """Fill the table with entries."""

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
        # Get object from cell data
        item = self.table_widget.item(index.row(), index.column())
        if item:
            entry = item.data(Qt.UserRole)

            # Create and show details dialog
            dialog = EntryDetailsDialog(entry, self)
            dialog.exec()

    def on_selection_changed(self):
        # Update selected rows storage
        self.selected_rows = set(item.row() for item in self.table_widget.selectedItems())

        # Update status bar with selection info
        self.update_status_bar()

    def update_status_bar(self):
        """Update the status bar with dictionary information."""

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
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dictionary Manager 2.0')
        self.setGeometry(100, 100, 800, 600)

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

        # Create button to open a dictionary
        self.open_action = QAction('Open', self)
        self.open_action.triggered.connect(self.open_dict)
        self.toolbar.addAction(self.open_action)

        # Create button to create new dictionary
        self.new_action = QAction('New', self)
        self.new_action.triggered.connect(self.new_dict)
        self.toolbar.addAction(self.new_action)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setVisible(False)  # Hide initially
        layout.addWidget(self.tab_widget)

        # Create placeholder for empty workspace
        self.placeholder = QLabel('No dictionary open')
        self.placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.placeholder)

    def show_settings_menu(self):
        pass

    def open_dict(self):
        file_filter = '(' + ' '.join(f'*{ext}' for ext in self.manager.allowed_file_ext) + ')'
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            caption='Select Saving File',
            filter=file_filter,
        )
        self.manager.open_dct(file_path)

        dict_name = self.manager.dct.name
        self.create_new_tab(dict_name)

    def new_dict(self):
        new_dict_name = 'Unnamed'
        self.manager.create_dct(new_dict_name)
        self.create_new_tab(new_dict_name)

    def create_new_tab(self, title: str):
        # Create new workspace
        workspace = WorkspaceWidget(self.manager.dct)

        # Add tab
        self.tab_widget.addTab(workspace, title)

        # Set new tab as active
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

        # Show tab widget if it was hidden
        if not self.tab_widget.isVisible():
            self.tab_widget.setVisible(True)
            self.placeholder.setVisible(False)

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

        # Hide tab widget if no tabs are open
        if self.tab_widget.count() == 0:
            self.tab_widget.setVisible(False)
            self.placeholder.setVisible(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
