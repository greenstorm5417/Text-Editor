from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QVBoxLayout, QWidget, QLabel, QTabWidget
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

        # Initialize QTabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(CustomTabBar())
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.change_tab)

        # Apply theme to QTabWidget
        self.apply_theme_to_tab_widget()

        # Add widgets to layout
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.no_tabs_label)

        # Set container as central widget
        self.setCentralWidget(container)

        # Add initial tab
        self.add_new_tab()
        self.no_tabs_label.hide()

    def apply_theme_to_tab_widget(self):
        """Apply the theme styling to the QTabWidget."""
        font = Theme.get_tab_font()
        font_size = font.pointSize()
        font_family = font.family()
        font_weight = font.weight()

        # Apply stylesheet for theming
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
            }}
            QTabBar {{
                font-family: "{font_family}";
                font-size: {font_size}pt;
                font-weight: {font_weight};
            }}
            QTabBar::tab {{
                background: {Theme.TAB_BACKGROUND_COLOR.name()};
                color: {Theme.TAB_TEXT_COLOR.name()};
                padding: {Theme.scaled_size(5)}px;
                min-width: {Theme.scaled_size(100)}px;
                max-width: {Theme.scaled_size(150)}px;
            }}
            QTabBar::tab:selected {{
                background: {Theme.TAB_ACTIVE_BACKGROUND_COLOR.name()};
            }}
            QTabBar::tab:hover {{
                background: {Theme.HOVER_COLOR.name()};
            }}
            QTabBar::close-button {{
                subcontrol-position: right;
                image: url('resources/icons/close.png');  /* Update with your icon path */
            }}
            QTabBar::close-button:hover {{
                background: {Theme.CLOSE_BUTTON_HOVER_COLOR.name()};
            }}
        """)

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
        self.no_tabs_label.hide()  # Hide the "no tabs" message when creating a new file

    def add_new_tab(self, content='', title='Untitled', file_path=None):
        """Add a new tab with a TextEditor widget."""
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
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
        if self.tab_widget.count() == 0:
            self.no_tabs_label.show()

    def change_tab(self, index):
        """Change the current tab."""
        if index != -1:
            self.no_tabs_label.hide()
        else:
            self.no_tabs_label.show()

    def show_about_dialog(self):
        """Display an About dialog."""
        QMessageBox.information(self, "About", "My Custom Text Editor\nBuilt with PyQt6")
