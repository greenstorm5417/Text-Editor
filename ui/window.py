from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QTabWidget, QVBoxLayout, QWidget, QLabel
)
from PyQt6.QtCore import Qt
from ui.custom_title_bar import CustomTitleBar
from editor.texteditor import TextEditor
from editor.theme import Theme
from ui.custom_tab_bar import CustomTabBar

from actions.fileoperations import FileOperationsMixin
from actions.editactions import EditActionsMixin

class MainWindow(QMainWindow, FileOperationsMixin, EditActionsMixin):
    def __init__(self):
        super().__init__()

        # Remove the default window frame
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)  # Make background opaque

        self.setWindowTitle('My Custom Text Editor')
        self.setGeometry(
            100, 100,
            Theme.scaled_size(Theme.WINDOW_WIDTH),
            Theme.scaled_size(Theme.WINDOW_HEIGHT)
        )

        # Create the no tabs label first
        self.no_tabs_label = QLabel(
            "No tabs open. Try opening something!",
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Create main container widget and layout
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove default margins
        main_layout.setSpacing(0)  # No spacing between widgets

        # Initialize custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Initialize tab widget with custom tab bar
        self.tab_widget = QTabWidget()
        self.tab_bar = CustomTabBar(self.tab_widget)
        self.tab_widget.setTabBar(self.tab_bar)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Add widgets to layout
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.no_tabs_label)

        # Set container as central widget
        self.setCentralWidget(container)

        # Add initial tab
        self.add_new_tab()
        self.no_tabs_label.hide()

    def update_tab_title(self, text_editor):
        """Update the tab title based on the TextEditor instance."""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            te = widget.findChild(TextEditor)
            if te == text_editor:
                # Remove trailing asterisks and spaces
                title = self.tab_widget.tabText(i).rstrip('* ').rstrip()
                
                if te.is_modified:
                    if not self.tab_widget.tabText(i).endswith('*'):
                        new_title = f"{title}*"
                        self.tab_widget.setTabText(i, new_title)
                else:
                    if self.tab_widget.tabText(i).endswith('*'):
                        new_title = title
                        self.tab_widget.setTabText(i, new_title)
                
                break

    def new_file(self):
        """Create a new file in a new tab."""
        self.add_new_tab()
        self.no_tabs_label.hide()  # Hide the "no tabs" message when creating a new file

    def add_new_tab(self, content='', title='Untitled', file_path=None):
        """Add a new tab with a TextEditor widget."""
        new_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        text_editor = TextEditor(content, file_path, self)  # Pass self to TextEditor
        text_editor.modifiedChanged.connect(self.update_tab_title)  # Connect the signal
        layout.addWidget(text_editor)
        new_tab.setLayout(layout)
        self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentWidget(new_tab)

    def close_tab(self, index):
        """Close the tab at the given index."""
        current_widget = self.tab_widget.widget(index)
        text_editor = current_widget.findChild(TextEditor)
        if text_editor and text_editor.is_modified:
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                f"'{self.tab_widget.tabText(index).rstrip('*')}' has unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            if reply == QMessageBox.StandardButton.Save:
                # Save the file
                if text_editor.file_path:
                    try:
                        with open(text_editor.file_path, 'w', encoding='utf-8') as file:
                            file.write(text_editor.toPlainText())
                        text_editor.set_modified(False)  # Use setter method
                        self.update_tab_title(text_editor)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
                        return  # Do not close the tab
                else:
                    file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "Untitled.txt", "Text Files (*.txt);;All Files (*)")
                    if file_path:
                        try:
                            with open(file_path, 'w', encoding='utf-8') as file:
                                file.write(text_editor.toPlainText())
                            text_editor.file_path = file_path
                            text_editor.set_modified(False)  # Use setter method
                            self.tab_widget.setTabText(index, file_path.split('/')[-1])
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
            elif reply == QMessageBox.StandardButton.Cancel:
                return  # Do not close the tab
            elif reply == QMessageBox.StandardButton.Discard:
                pass  # Proceed to close the tab

        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.no_tabs_label.show()

    def show_about_dialog(self):
        """Display an About dialog."""
        QMessageBox.information(self, "About", "My Custom Text Editor\nBuilt with PyQt6")
