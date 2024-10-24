from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QVBoxLayout, QWidget, QLabel, QTabWidget
)
from PyQt6.QtCore import Qt
from ui.custom_title_bar import CustomTitleBar
from editor.texteditor import TextEditor
from editor.theme import Theme

from actions.fileoperations import FileOperationsMixin
from actions.editactions import EditActionsMixin

class MainWindow(QMainWindow, FileOperationsMixin, EditActionsMixin):
    def __init__(self):
        super().__init__()

        # Remove the default window frame
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)  # Make background opaque

        self.setWindowTitle(' Text Editor')
        self.setGeometry(
            100, 100,
            Theme.scaled_size(Theme.WINDOW_WIDTH),
            Theme.scaled_size(Theme.WINDOW_HEIGHT)
        )

        # Create main container widget and layout
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove default margins
        main_layout.setSpacing(5)  # No spacing between widgets

        # Initialize custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Initialize QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.change_tab)

        # Set the font for the tab bar
        self.tab_widget.tabBar().setFont(Theme.get_tab_font())

        # Apply stylesheet to the tab bar
        self.apply_tab_bar_stylesheet()

        # Add tab widget to the main layout
        main_layout.addWidget(self.tab_widget)

        # Set container as central widget
        self.setCentralWidget(container)

    def apply_tab_bar_stylesheet(self):
        """Apply custom stylesheet to the tab bar using Theme settings."""
        tab_bar_stylesheet = f"""
        QTabWidget::pane {{
            border-top: 2px solid {Theme.color_to_stylesheet(Theme.TAB_BORDER_COLOR)};
        }}

        QTabBar::tab {{
            background: {Theme.color_to_stylesheet(Theme.TAB_BACKGROUND_COLOR)};
            color: {Theme.color_to_stylesheet(Theme.TAB_TEXT_COLOR)};
            padding: 5px;
            margin-right: 2px;
            min-width: 80px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background: {Theme.color_to_stylesheet(Theme.TAB_ACTIVE_BACKGROUND_COLOR)};
            color: {Theme.color_to_stylesheet(Theme.TAB_TEXT_COLOR)};
        }}

        QTabBar::tab:hover {{
            background: {Theme.color_to_stylesheet(Theme.TAB_HOVER_BACKGROUND_COLOR)};
        }}

        QTabBar::close-button {{
            image: url(resources/icons/close_icon.svg);
            subcontrol-position: right;
            margin: 0px;
            padding: 0px;
        }}

        QTabBar::close-button:hover {{
            background: {Theme.color_to_stylesheet(Theme.CLOSE_BUTTON_HOVER_COLOR)};
        }}
        """
        self.tab_widget.setStyleSheet(tab_bar_stylesheet)

    def update_tab_title(self, text_editor):
        """Update the tab title based on the TextEditor instance."""
        index = self.tab_widget.indexOf(text_editor.parent())
        if index != -1:
            # Remove trailing asterisks and spaces
            title = self.tab_widget.tabText(index).rstrip('* ').rstrip()

            if text_editor.is_modified:
                if not self.tab_widget.tabText(index).endswith('*'):
                    new_title = f"{title}*"
                    self.tab_widget.setTabText(index, new_title)
            else:
                if self.tab_widget.tabText(index).endswith('*'):
                    new_title = title
                    self.tab_widget.setTabText(index, new_title)

    def new_file(self):
        """Create a new file in a new tab."""
        self.add_new_tab()
        # Remove or comment out the no_tabs_label if it's causing issues

    def add_new_tab(self, content='', title='Untitled', file_path=None):
        """Add a new tab with a TextEditor widget."""
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.setContentsMargins(0, 10, 0, 0)  # Set margins as needed
        layout.setSpacing(5)
        text_editor = TextEditor(content, file_path, self)  # Pass self to TextEditor
        text_editor.modifiedChanged.connect(self.update_tab_title)  # Connect the signal
        layout.addWidget(text_editor)

        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentIndex(index)

    def close_tab(self, index):
        """Close the tab at the given index."""
        widget = self.tab_widget.widget(index)
        text_editor = widget.findChild(TextEditor)
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
                    else:
                        return  # Do not close the tab
            elif reply == QMessageBox.StandardButton.Cancel:
                return  # Do not close the tab
            elif reply == QMessageBox.StandardButton.Discard:
                pass  # Proceed to close the tab

        self.tab_widget.removeTab(index)
        widget.deleteLater()

    def change_tab(self, index):
        """Change the current tab."""
        if index != -1:
            pass
        else:
            pass
    def show_about_dialog(self):
        """Display an About dialog."""
        QMessageBox.information(self, "About", "My Custom Text Editor\nBuilt with PyQt6")
