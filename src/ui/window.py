# src/ui/window.py

from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Relative imports for custom widgets and containers
from .widgets.titlebar import CustomTitleBar
from .widgets.tabs import CustomTabWidget
from .widgets.sidebar import Sidebar
from .containers.base import ContainersManager
from .containers.files import FileTreeContainer
from .containers.settings import SettingsContainer
from .containers.plugins import PluginsContainer

from src.editor import (
    TextEditor,
    Theme,
    PygmentsSyntaxHighlighter,
    FileOperationsMixin,
    EditActionsMixin,
)

import json
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class MainWindow(FileOperationsMixin, EditActionsMixin, QMainWindow):
    SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".my_text_editor_settings.json")

    def __init__(self):
        super().__init__()

        # Remove the default window frame
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Set application icon
        app_icon = QIcon("resources/icons/logo.svg")
        self.setWindowIcon(app_icon)

        if os.name == 'nt':  # Windows
            # Set the app user model ID to ensure the taskbar icon is displayed correctly
            import ctypes
            myappid = 'mycompany.myproduct.subproduct.version'  # Arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.setWindowTitle('TextForge')
        self.setGeometry(
            100, 100,
            Theme.scaled_size(Theme.WINDOW_WIDTH),
            Theme.scaled_size(Theme.WINDOW_HEIGHT)
        )

        # Create main container widget and layout
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        main_layout.setSpacing(0)

        # Initialize custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Add a horizontal line separator below the title bar
        h_line = QFrame()
        h_line.setFrameShape(QFrame.Shape.HLine)
        h_line.setFixedHeight(Theme.LINE_WIDTH)
        h_line.setStyleSheet(f"background-color: {Theme.color_to_stylesheet(Theme.LINE_COLOR)};")
        main_layout.addWidget(h_line)

        # Create content area widget and layout
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        content_layout.setSpacing(0)

        # Initialize Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.sidebar)

        # Add a vertical line separator between the sidebar and containers
        v_line1 = QFrame()
        v_line1.setFrameShape(QFrame.Shape.VLine)
        v_line1.setFixedWidth(Theme.LINE_WIDTH)
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
        self.v_line2.setFixedWidth(Theme.LINE_WIDTH)
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

        # Load application settings
        self.load_settings()

    def add_sidebar_icons(self):
        """Add icons to the sidebar and corresponding containers."""
        # Define icons and their corresponding container indices
        icons = [
            ("resources/icons/file_manager.svg", 1),  # File Tree
            ("resources/icons/settings.svg", 2),      # Settings
            ("resources/icons/plugins.svg", 3)        # Plugins
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
        """Toggle the visibility of a container based on the clicked sidebar icon."""
        self.containers_manager.show_container(index)
        if self.containers_manager.current_container is not None:
            self.v_line2.setVisible(True)
            self.containers_manager.setVisible(True)
        else:
            self.v_line2.setVisible(False)
            self.containers_manager.setVisible(False)

    def add_new_tab(self, content='', title='Untitled', file_path=None):
        """Add a new tab with a TextEditor widget."""
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
        layout.setSpacing(0)

        # Initialize the TextEditor
        text_editor = TextEditor(content, file_path, self)  # Pass self to TextEditor
        text_editor.modifiedChanged.connect(self.update_tab_title)

        # Set the syntax highlighter based on file extension
        if file_path:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower().lstrip('.')
            language = self.get_language_from_extension(ext)
            highlighter = PygmentsSyntaxHighlighter(language)
            text_editor.set_highlighter(highlighter)
        else:
            # Default to plain text (no highlighting)
            text_editor.set_highlighter(None)

        # Add the TextEditor to the layout
        layout.addWidget(text_editor)

        # Add the new tab to the tab widget
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentIndex(index)
        text_editor.setFocus()  # Set focus to new TextEditor
        return index

    def get_language_from_extension(self, ext):
        """Map file extensions to Pygments lexer names."""
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
                        text_editor.set_modified(False)
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
                            text_editor.set_modified(False)
                            self.tab_widget.setTabText(index, os.path.basename(file_path))
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
        if index == -1:
            return

        current_title = self.tab_widget.tabText(index)
        title = current_title.rstrip('*').strip()

        if text_editor.is_modified:
            new_title = f"{title}*"
        else:
            new_title = title

        if current_title != new_title:
            self.tab_widget.setTabText(index, new_title)

    def save_settings(self):
        """Save the current state of the application to a JSON file."""
        settings = {
            "window": {
                "geometry": {
                    "x": self.x(),
                    "y": self.y(),
                    "width": self.width(),
                    "height": self.height(),
                    "maximized": self.isMaximized()
                }
            },
            "file_tree": {
                "current_root": None,
                "expanded_paths": [],
                "visible": False
            },
            "open_tabs": []
        }

        # Save File Tree State
        file_tree_container = self.containers_manager.containers.get(1)
        if file_tree_container and file_tree_container.current_root:
            settings["file_tree"].update({
                "current_root": file_tree_container.current_root,
                "expanded_paths": file_tree_container.get_expanded_paths(),
                "visible": (self.containers_manager.current_container == 1)
            })

        # Save Open Tabs with additional metadata
        for index in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(index)
            text_editor = widget.findChild(TextEditor)
            if text_editor:
                tab_data = {
                    "file_path": text_editor.file_path,
                    "cursor_position": (text_editor.cursor_line, text_editor.cursor_column),
                    "scroll_position": {
                        "vertical": text_editor.verticalScrollBar().value(),
                        "horizontal": text_editor.horizontalScrollBar().value()
                    }
                }
                if text_editor.file_path:  # Only save if it's a real file
                    settings["open_tabs"].append(tab_data)

        try:
            os.makedirs(os.path.dirname(self.SETTINGS_FILE), exist_ok=True)
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            logging.info(f"Settings saved to {self.SETTINGS_FILE}")
        except Exception as e:
            logging.error(f"Error saving settings: {e}")

    def load_settings(self):
        """Load the application state from a JSON file."""
        if not os.path.exists(self.SETTINGS_FILE):
            logging.info("No settings file found. Starting with default settings.")
            return

        try:
            with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Restore window geometry
            if "window" in settings:
                geometry = settings["window"].get("geometry", {})
                if geometry:
                    self.move(geometry.get("x", 100), geometry.get("y", 100))
                    self.resize(geometry.get("width", 1000), geometry.get("height", 700))
                    if geometry.get("maximized", False):
                        self.showMaximized()

            # Restore File Tree State
            if "file_tree" in settings:
                file_tree_settings = settings["file_tree"]
                file_tree_container = self.containers_manager.containers.get(1)
                if file_tree_container and file_tree_settings.get("current_root"):
                    root_path = file_tree_settings["current_root"]
                    if os.path.exists(root_path):
                        file_tree_container.set_root_directory(root_path)
                        file_tree_container.restore_expanded_paths(
                            file_tree_settings.get("expanded_paths", [])
                        )
                        if file_tree_settings.get("visible", False):
                            self.toggle_container(1)

            # Clear existing tabs before restoring
            while self.tab_widget.count() > 0:
                self.tab_widget.removeTab(0)

            # Restore Open Tabs
            restored_tabs = []
            for tab_data in settings.get("open_tabs", []):
                file_path = tab_data.get("file_path")
                if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()

                        # Create new tab without focusing it yet
                        index = self.add_new_tab(
                            content=content,
                            title=os.path.basename(file_path),
                            file_path=file_path
                        )

                        if index >= 0:
                            widget = self.tab_widget.widget(index)
                            text_editor = widget.findChild(TextEditor)
                            if text_editor:
                                # Restore cursor position
                                cursor_pos = tab_data.get("cursor_position")
                                if cursor_pos:
                                    line = min(cursor_pos[0], len(text_editor.lines) - 1)
                                    column = min(cursor_pos[1], len(text_editor.lines[line]))
                                    text_editor.cursor_line = line
                                    text_editor.cursor_column = column

                                # Restore scroll position
                                scroll_pos = tab_data.get("scroll_position", {})
                                if scroll_pos:
                                    text_editor.verticalScrollBar().setValue(scroll_pos.get("vertical", 0))
                                    text_editor.horizontalScrollBar().setValue(scroll_pos.get("horizontal", 0))

                                restored_tabs.append(index)
                                text_editor.set_modified(False)  # Mark as unmodified after loading

                    except Exception as e:
                        logging.error(f"Error loading tab for '{file_path}': {e}")
                else:
                    logging.warning(f"File '{file_path}' does not exist or is not accessible")

            # Set focus to the first tab if any were restored
            if restored_tabs:
                self.tab_widget.setCurrentIndex(restored_tabs[0])
                current_widget = self.tab_widget.currentWidget()
                if current_widget:
                    text_editor = current_widget.findChild(TextEditor)
                    if text_editor:
                        text_editor.setFocus()
            else:
                # If no tabs were restored, create a new empty tab
                self.new_file()

            logging.info(f"Settings loaded from {self.SETTINGS_FILE}")
            logging.info(f"Restored {len(restored_tabs)} tabs")
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            # If there's an error loading settings, create a new empty tab
            self.new_file()

    def show_about_dialog(self):
        """Display an About dialog."""
        QMessageBox.information(self, "About", "My Custom Text Editor\nBuilt with PyQt6")

    def closeEvent(self, event):
        """Handle the window close event to save settings."""
        # First, handle unsaved changes
        super().closeEvent(event)  # Calls FileOperationsMixin.closeEvent

        if event.isAccepted():
            # Save settings before closing
            self.save_settings()
