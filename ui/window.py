from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSizePolicy, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from ui.custom_title_bar import CustomTitleBar
from editor.texteditor import TextEditor
from editor.theme import Theme
from editor.syntax_highlighter import PygmentsSyntaxHighlighter

from actions.fileoperations import FileOperationsMixin
from actions.editactions import EditActionsMixin

from ui.custom_tab_widget import CustomTabWidget
from ui.sidebar import Sidebar
from ui.containers import ContainersManager, SettingsContainer, PluginsContainer, FileTreeContainer  

import json
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Inside the MainWindow class, define the settings file path
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".my_text_editor_settings.json")


class MainWindow(QMainWindow, FileOperationsMixin, EditActionsMixin):
    def __init__(self):
        super().__init__()

        # Remove the default window frame
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self.setWindowTitle('Text Editor')
        self.setGeometry(
            100, 100,
            Theme.scaled_size(Theme.WINDOW_WIDTH),
            Theme.scaled_size(Theme.WINDOW_HEIGHT)
        )

        # Create main container widget and layout
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Ensure no extra margins
        main_layout.setSpacing(0)

        

        # Initialize custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Add a horizontal line separator below the title bar
        h_line = QFrame()
        h_line.setFrameShape(QFrame.Shape.HLine)
        h_line.setFixedHeight(Theme.LINE_WIDTH)  # Use the theme width
        h_line.setStyleSheet(f"background-color: {Theme.color_to_stylesheet(Theme.LINE_COLOR)};")
        main_layout.addWidget(h_line)

        # Create content area widget and layout
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)  # Ensure no extra margins
        content_layout.setSpacing(0)

        # Initialize Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.sidebar)

        # Add a vertical line separator between the sidebar and containers
        v_line1 = QFrame()
        v_line1.setFrameShape(QFrame.Shape.VLine)
        v_line1.setFixedWidth(Theme.LINE_WIDTH)  # Use the theme width
        v_line1.setStyleSheet(f"background-color: {Theme.color_to_stylesheet(Theme.LINE_COLOR)};")
        content_layout.addWidget(v_line1)

        # Initialize ContainersManager
        self.containers_manager = ContainersManager(self)
        self.containers_manager.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.containers_manager.setVisible(False)  # Initially hidden
        content_layout.addWidget(self.containers_manager)

        # Add a vertical line separator between containers and tab widget
        self.v_line2 = QFrame()
        self.v_line2.setFrameShape(QFrame.Shape.VLine)
        self.v_line2.setFixedWidth(Theme.LINE_WIDTH)  # Use the theme width
        self.v_line2.setStyleSheet(f"background-color: {Theme.color_to_stylesheet(Theme.LINE_COLOR)};")
        self.v_line2.setVisible(False)  # Initially hidden
        content_layout.addWidget(self.v_line2)

        # Initialize CustomTabWidget (main content area)
        self.tab_widget = CustomTabWidget(self)
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.tab_widget)

        # Add content_widget to main_layout
        main_layout.addWidget(content_widget)

        # Set container as central widget
        self.setCentralWidget(container)

        # Add icons to the sidebar and corresponding containers
        self.add_sidebar_icons()

        # Connect sidebar signals
        self.sidebar.icon_clicked.connect(self.toggle_container)

        self.load_settings()


    def add_sidebar_icons(self):
        # Define icons and their corresponding container indices
        # Assign index=1 for File Tree, index=2 for Settings, index=3 for Plugins
        icons = [
            ("resources/icons/file_manager.svg", 1),  
            ("resources/icons/settings.svg", 2), 
            ("resources/icons/plugins.svg", 3)  
        ]

        for icon_path, index in icons:
            self.sidebar.add_icon(icon_path, index)
            # Create and add containers through ContainersManager
            if index == 1:
                container = FileTreeContainer(self)
            elif index == 2:
                container = SettingsContainer()
            elif index == 3:
                container = PluginsContainer()
            else:
                container = QLabel(f"Container {index} Content")
                container.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.containers_manager.add_container(index, f"Container {index}", content_widget=container)

    def toggle_container(self, index):
        """
        Toggles the visibility of a container based on the clicked sidebar icon.
        """
        self.containers_manager.show_container(index)
        if self.containers_manager.current_container is not None:
            self.v_line2.setVisible(True)
            self.containers_manager.setVisible(True)
        else:
            self.v_line2.setVisible(False)
            self.containers_manager.setVisible(False)

    def add_new_tab(self, content='', title='Untitled', file_path=None):
        """Add a new tab with a TextEditor widget inside a QScrollArea."""
        
        # Check if the file is already open
        if file_path:
            for index in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(index)
                text_editor = widget.findChild(TextEditor)
                if text_editor and text_editor.file_path == file_path:
                    self.tab_widget.setCurrentIndex(index)
                    text_editor.setFocus()  # Set focus to existing TextEditor
                    return index

        # Create a new tab widget
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing

        # Initialize the TextEditor
        text_editor = TextEditor(content, file_path, self)  # Pass self to TextEditor
        text_editor.modifiedChanged.connect(self.update_tab_title)  # Connect the signal



        # Set the syntax highlighter based on file extension
        if file_path:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower().lstrip('.')
            language = self.get_language_from_extension(ext)
            highlighter = PygmentsSyntaxHighlighter(language)
            text_editor.set_highlighter(highlighter)
        else:
            # For new files, you might prompt the user to select a language
            # For now, we'll default to plain text (no highlighting)
            text_editor.set_highlighter(None)

        # Directly add the TextEditor to the layout
        layout.addWidget(text_editor)

        # Add the new tab to the tab widget
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentIndex(index)
        text_editor.setFocus()  # Set focus to new TextEditor
        return index

    def get_language_from_extension(self, ext):
        """
        Map file extensions to Pygments lexer names.
        """
        extension_mapping = {
            'py': 'python',
            'js': 'javascript',
            'html': 'html',
            'css': 'css',
            'cpp': 'cpp',
            'c': 'c',
            'java': 'java',
            'json': 'json',
            'xml': 'xml',
            'md': 'markdown',
            'yaml': 'yaml',
            'yml': 'yaml',
            'php': 'php',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust',
            # Add more extensions as needed
        }
        return extension_mapping.get(ext, None)

    def new_file(self):
        """Create a new file in a new tab."""
        self.add_new_tab()

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
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, "Save File As", "Untitled.txt", "Text Files (*.txt);;All Files (*)"
                    )
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
            self.tab_widget.setCurrentIndex(index)

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

    def save_settings(self):
        """Save the current state of the application to a JSON file."""
        settings = {}

        # ===== Save File Tree State =====
        file_tree_container = self.containers_manager.containers.get(1)  # Assuming index=1 for FileTreeContainer
        if file_tree_container and file_tree_container.current_root:
            settings["current_root"] = file_tree_container.current_root
            settings["expanded_paths"] = file_tree_container.get_expanded_paths()
            settings["file_tree_container_open"] = (self.containers_manager.current_container == 1)
        else:
            settings["current_root"] = None
            settings["expanded_paths"] = []
            settings["file_tree_container_open"] = False

        # ===== Save Open Tabs =====
        open_tabs = []
        for index in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(index)
            text_editor = widget.findChild(TextEditor)
            if text_editor and text_editor.file_path:
                open_tabs.append(text_editor.file_path)
            else:
                # For unsaved files, you might want to handle them differently
                pass  # Currently skipping unsaved files
        settings["open_tabs"] = open_tabs

        # ===== Save to JSON =====
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            logging.info(f"Settings saved to {SETTINGS_FILE}")
        except Exception as e:
            logging.error(f"Error saving settings: {e}")

    def load_settings(self):
        """Load the application state from a JSON file."""
        if not os.path.exists(SETTINGS_FILE):
            logging.info("No settings file found. Starting with default settings.")
            return  # No settings to load

        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # ===== Restore File Tree State =====
            file_tree_container = self.containers_manager.containers.get(1)  # Assuming index=1 for FileTreeContainer
            if file_tree_container and settings.get("current_root"):
                file_tree_container.set_root_directory(settings["current_root"])
                file_tree_container.restore_expanded_paths(settings.get("expanded_paths", []))

                # Restore visibility
                if settings.get("file_tree_container_open", False):
                    self.toggle_container(1)
                else:
                    self.containers_manager.hide_current_container()

            # ===== Restore Open Tabs =====
            open_tabs = settings.get("open_tabs", [])
            for file_path in open_tabs:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                        self.add_new_tab(content, title=os.path.basename(file_path), file_path=file_path)
                    except Exception as e:
                        logging.error(f"Error loading tab for '{file_path}': {e}")
                else:
                    logging.warning(f"File '{file_path}' does not exist and cannot be opened.")

            logging.info(f"Settings loaded from {SETTINGS_FILE}")
        except Exception as e:
            logging.error(f"Error loading settings: {e}")

    def show_about_dialog(self):
        """Display an About dialog."""
        QMessageBox.information(self, "About", "My Custom Text Editor\nBuilt with PyQt6")

    def closeEvent(self, event):
        """Handle the window close event to save settings."""
        # First, handle unsaved changes as per existing logic in FileOperationsMixin.closeEvent
        super().closeEvent(event)  # Calls FileOperationsMixin.closeEvent

        if event.isAccepted():
            # Now save the settings
            self.save_settings()
