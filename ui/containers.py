from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QToolButton, QHBoxLayout, QInputDialog, QMessageBox, QSizePolicy,
    QTreeWidget, QTreeWidgetItem, QMenu
)
# import QAction

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QDrag, QPainter, QAction
from editor.theme import Theme
import os
import sys
import shutil
import logging
import subprocess
from PyQt6.QtWidgets import QApplication

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class FileTreeWidget(QTreeWidget):
    """
    Custom QTreeWidget to handle internal drag and drop for moving files and folders.
    Implements lazy loading to ensure expand arrows are always visible.
    """
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectItems)
        self.setFont(Theme.get_default_font())  # Set font directly

        # Assign icons for directories and files
        self.dir_icon = QIcon.fromTheme("folder") or QIcon("resources/icons/folder_icon.png")
        self.file_icon = QIcon.fromTheme("text-x-generic") or QIcon("resources/icons/file_icon.png")

        # Connect signals
        self.itemExpanded.connect(self.on_item_expanded)
        self.itemClicked.connect(self.on_item_clicked)  # Connect itemClicked signal

        # Enable custom context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.main_window = main_window


    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Slot to handle item click events.
        Opens the file in a new tab if the clicked item is a file.
        """
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if os.path.isfile(path):
            logging.debug(f"File clicked: {path}")
            self.parent().open_file_in_tab(path)
        else:
            logging.debug(f"Directory clicked: {path}")
            # Optionally, expand/collapse the directory on single click
            item.setExpanded(not item.isExpanded())

    def open_context_menu(self, position):
        """
        Opens a context menu with actions based on whether a file or folder is clicked.
        """
        item = self.itemAt(position)
        if not item:
            return  # No item was clicked

        path = item.data(0, Qt.ItemDataRole.UserRole)
        if not path:
            return

        menu = QMenu()

        if os.path.isfile(path):
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.parent().open_file_in_tab(path))
            menu.addAction(open_action)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_item(item, path))
        menu.addAction(rename_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_item(item, path))
        menu.addAction(delete_action)

        copy_path_action = QAction("Copy Path", self)
        copy_path_action.triggered.connect(lambda: self.copy_path(path))
        menu.addAction(copy_path_action)

        if os.path.isfile(path):
            open_external_action = QAction("Open in External Editor", self)
            open_external_action.triggered.connect(lambda: self.open_in_external_editor(path))
            menu.addAction(open_external_action)

        menu.exec(self.viewport().mapToGlobal(position))

    def rename_item(self, item, path):
        """
        Renames the selected file or folder.
        """
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=os.path.basename(path))
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            if os.path.exists(new_path):
                QMessageBox.warning(self, "Rename Failed", f"'{new_name}' already exists.")
                return
            try:
                os.rename(path, new_path)
                logging.info(f"Renamed '{path}' to '{new_path}'")
                self.parent().populate_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename:\n{e}")
                logging.error(f"Error renaming '{path}' to '{new_path}': {e}")

    def delete_item(self, item, path):
        """
        Deletes the selected file or folder after confirmation.
        """
        reply = QMessageBox.question(
            self, "Delete", f"Are you sure you want to delete '{os.path.basename(path)}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    logging.info(f"Deleted file: {path}")
                else:
                    shutil.rmtree(path)
                    logging.info(f"Deleted folder: {path}")
                self.parent().populate_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete:\n{e}")
                logging.error(f"Error deleting '{path}': {e}")

    def copy_path(self, path):
        """
        Copies the full path of the selected item to the clipboard.
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(path)
        logging.info(f"Copied path to clipboard: {path}")

    def open_in_external_editor(self, path):
        """
        Opens the file in the system's default external editor.
        """
        try:
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', path))
            elif os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                subprocess.call(('xdg-open', path))
            logging.info(f"Opened '{path}' in external editor.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open in external editor:\n{e}")
            logging.error(f"Error opening '{path}' in external editor: {e}")

    def on_item_expanded(self, item: QTreeWidgetItem):
        """
        Handler for the itemExpanded signal.
        Populates the item with actual child items if it only contains the dummy child.
        """
        if item.childCount() == 1 and item.child(0).text(0) == "Loading...":
            # Remove the dummy child
            item.removeChild(item.child(0))
            # Populate with actual children
            parent_path = item.data(0, Qt.ItemDataRole.UserRole)
            self.parent().add_sub_items(item, parent_path)
    
    def open_file_in_tab(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            file_name = os.path.basename(file_path)
            logging.info(f"Opening file in tab: {file_path}")
            # Corrected: Navigate up to MainWindow and call add_new_tab
            main_window = self.parent().parent().parent()
            if hasattr(main_window, 'add_new_tab'):
                main_window.add_new_tab(content, title=file_name, file_path=file_path)
            else:
                logging.error("MainWindow does not have add_new_tab method.")
                QMessageBox.critical(self, "Error", "Internal error: Could not open the file in a new tab.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
            logging.error(f"Error opening file '{file_path}': {e}")




class FileTreeContainer(QWidget):
    """
    Container widget for displaying the file tree with functionalities to create files/folders,
    toggle hidden files, and handle drag-and-drop operations.
    """
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.current_root = None  # Tracks the current root directory
        self.show_hidden = False  # Flag to track hidden files visibility
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Minimal padding for a slimmer look
        layout.setSpacing(5)

        # Create a widget to hold the buttons
        self.button_widget = QWidget()
        self.button_layout = QHBoxLayout(self.button_widget)
        self.button_layout.setSpacing(5)

        # Create File Button
        self.create_file_button = QToolButton()
        self.create_file_button.setIcon(QIcon.fromTheme("document-new") or QIcon("resources/icons/document_new.png"))
        self.create_file_button.setToolTip("Create New File")
        self.create_file_button.clicked.connect(self.create_file)
        self.button_layout.addWidget(self.create_file_button)

        # Create Folder Button
        self.create_folder_button = QToolButton()
        self.create_folder_button.setIcon(QIcon.fromTheme("folder-new") or QIcon("resources/icons/folder_new.png"))
        self.create_folder_button.setToolTip("Create New Folder")
        self.create_folder_button.clicked.connect(self.create_folder)
        self.button_layout.addWidget(self.create_folder_button)

        # Toggle Hidden Files Button
        self.toggle_hidden_button = QToolButton()
        self.toggle_hidden_button.setIcon(QIcon.fromTheme("view-hidden") or QIcon("resources/icons/view_hidden.png"))
        self.toggle_hidden_button.setCheckable(True)
        self.toggle_hidden_button.setToolTip("Show Hidden Files")
        self.toggle_hidden_button.clicked.connect(self.toggle_hidden_files)
        self.button_layout.addWidget(self.toggle_hidden_button)

        # Add button_widget to the main layout
        layout.addWidget(self.button_widget)
        self.button_widget.setVisible(False)  # Initially hidden

        # Initialize QTreeWidget
        self.tree = FileTreeWidget(self.main_window, self)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {Theme.BACKGROUND_COLOR.name()};
                color: {Theme.TEXT_COLOR.name()};
                border: none;
            }}
            QTreeWidget::item {{
                padding-left: 20px;  /* Adjusted padding to make space for arrows */
                padding-top: 4px;
                padding-bottom: 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {Theme.SELECTION_COLOR.name()};
                color: {Theme.TEXT_COLOR.name()};
            }}
        """)
        self.tree.setVisible(False)  # Hidden initially

        # Placeholder Label
        self.placeholder_label = QLabel("Open a folder to display its contents.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setFont(Theme.get_default_font())
        self.placeholder_label.setStyleSheet(f"color: {Theme.TEXT_COLOR.name()};")
        layout.addWidget(self.placeholder_label)

        layout.addWidget(self.tree)

    def set_root_directory(self, path):
        """
        Set the root directory and populate the tree.
        Show buttons and tree widget, hide placeholder.
        """
        self.current_root = path
        if path:
            self.populate_tree()
            self.placeholder_label.setVisible(False)
            self.tree.setVisible(True)
            self.button_widget.setVisible(True)
            self.toggle_hidden_button.setChecked(False)
            self.toggle_hidden_button.setToolTip("Show Hidden Files")
            self.toggle_hidden_button.setIcon(QIcon.fromTheme("view-hidden") or QIcon("resources/icons/view_hidden.png"))
        else:
            self.placeholder_label.setVisible(True)
            self.tree.setVisible(False)
            self.button_widget.setVisible(False)

    def populate_tree(self):
        """Populate the tree widget with the directory structure."""
        if not self.current_root:
            return

        # Step 1: Save currently expanded paths
        expanded_paths = self.get_expanded_paths()

        self.tree.clear()

        # Add the root item
        root_name = os.path.basename(self.current_root) or self.current_root
        root_item = QTreeWidgetItem(self.tree)
        root_item.setText(0, root_name)
        root_item.setIcon(0, self.tree.dir_icon)  # Set directory icon
        root_item.setExpanded(True)
        root_item.setData(0, Qt.ItemDataRole.UserRole, self.current_root)  # Store the full path

        # Add a dummy child to enable expand arrow
        dummy_child = QTreeWidgetItem(root_item)
        dummy_child.setText(0, "Loading...")
        logging.debug(f"Added dummy child to root: {self.current_root}")

        # After populating, load actual contents for already expanded items
        self.load_expanded_items()

        # Step 2: Restore expanded paths
        self.restore_expanded_paths(expanded_paths)

    def get_expanded_paths(self):
        """
        Traverse the tree and collect the full paths of all expanded items.
        """
        expanded_paths = []

        def traverse(item):
            if item.isExpanded():
                path = item.data(0, Qt.ItemDataRole.UserRole)
                if path:
                    expanded_paths.append(path)
                for i in range(item.childCount()):
                    traverse(item.child(i))

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            traverse(root.child(i))

        logging.debug(f"Expanded paths before refresh: {expanded_paths}")
        return expanded_paths

    def restore_expanded_paths(self, paths):
        """
        Traverse the tree and expand items whose paths are in the provided list.
        """
        def traverse(item):
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path in paths:
                item.setExpanded(True)
                # Populate children if not already populated
                if item.childCount() == 1 and item.child(0).text(0) == "Loading...":
                    item.removeChild(item.child(0))
                    self.add_sub_items(item, path)
            for i in range(item.childCount()):
                traverse(item.child(i))

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            traverse(root.child(i))

        logging.debug(f"Restored expanded paths: {paths}")

    def add_sub_items(self, parent_item, parent_path):
        """Recursively add subdirectories and files to the tree."""
        try:
            entries = os.listdir(parent_path)
            # Sort entries: directories first, then files
            entries.sort(key=lambda x: (not os.path.isdir(os.path.join(parent_path, x)), x.lower()))
            for entry in entries:
                if not self.show_hidden and entry.startswith('.'):
                    continue  # Skip hidden files and folders
                entry_path = os.path.join(parent_path, entry)
                if os.path.isdir(entry_path):
                    dir_item = QTreeWidgetItem(parent_item)
                    dir_item.setText(0, entry)
                    dir_item.setIcon(0, self.tree.dir_icon)  # Set directory icon
                    dir_item.setExpanded(False)  # Collapse by default
                    dir_item.setData(0, Qt.ItemDataRole.UserRole, entry_path)  # Store the full path

                    # Add a dummy child to make the item expandable
                    dummy_child = QTreeWidgetItem(dir_item)
                    dummy_child.setText(0, "Loading...")
                    logging.debug(f"Added dummy child to directory: {entry_path}")
                else:
                    file_item = QTreeWidgetItem(parent_item)
                    file_item.setText(0, entry)
                    file_item.setIcon(0, self.tree.file_icon)  # Set file icon
                    file_item.setData(0, Qt.ItemDataRole.UserRole, entry_path)  # Store the full path
                    logging.debug(f"Added file: {entry_path}")
        except PermissionError:
            # Skip directories for which the user does not have permissions
            logging.warning(f"Permission denied: {parent_path}")
            pass
        except Exception as e:
            logging.error(f"Error accessing {parent_path}: {e}")

    def create_file(self):
        """Create a new file in the current directory."""
        if not self.current_root:
            QMessageBox.warning(self, "No Folder Open", "Please open a folder first.")
            return

        # Prompt the user for the file name
        file_name, ok = QInputDialog.getText(self, "Create File", "Enter file name:")
        if ok and file_name:
            # Validate the file name
            if not self.is_valid_name(file_name):
                QMessageBox.warning(self, "Invalid Name", "The file name contains invalid characters.")
                return

            new_file_path = os.path.join(self.current_root, file_name)
            if os.path.exists(new_file_path):
                QMessageBox.warning(self, "File Exists", f"A file named '{file_name}' already exists.")
                return
            try:
                # Create the new file
                with open(new_file_path, 'w', encoding='utf-8') as f:
                    pass  # Create an empty file
                logging.info(f"Created file: {new_file_path}")
                # Refresh the tree
                self.populate_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create file:\n{e}")
                logging.error(f"Error creating file '{new_file_path}': {e}")

    def create_folder(self):
        """Create a new folder in the current directory."""
        if not self.current_root:
            QMessageBox.warning(self, "No Folder Open", "Please open a folder first.")
            return

        # Prompt the user for the folder name
        folder_name, ok = QInputDialog.getText(self, "Create Folder", "Enter folder name:")
        if ok and folder_name:
            # Validate the folder name
            if not self.is_valid_name(folder_name):
                QMessageBox.warning(self, "Invalid Name", "The folder name contains invalid characters.")
                return

            new_folder_path = os.path.join(self.current_root, folder_name)
            if os.path.exists(new_folder_path):
                QMessageBox.warning(self, "Folder Exists", f"A folder named '{folder_name}' already exists.")
                return
            try:
                # Create the new folder
                os.makedirs(new_folder_path)
                logging.info(f"Created folder: {new_folder_path}")
                # Refresh the tree
                self.populate_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create folder:\n{e}")
                logging.error(f"Error creating folder '{new_folder_path}': {e}")

    def is_valid_name(self, name):
        """Validate the file or folder name."""
        invalid_chars = set('/\\?%*:|"<>')
        return not any(char in invalid_chars for char in name)

    def toggle_hidden_files(self):
        """Toggle the visibility of hidden files."""
        self.show_hidden = self.toggle_hidden_button.isChecked()
        if self.show_hidden:
            self.toggle_hidden_button.setToolTip("Hide Hidden Files")
            self.toggle_hidden_button.setIcon(QIcon.fromTheme("view-visible") or QIcon("resources/icons/view_visible.png"))
        else:
            self.toggle_hidden_button.setToolTip("Show Hidden Files")
            self.toggle_hidden_button.setIcon(QIcon.fromTheme("view-hidden") or QIcon("resources/icons/view_hidden.png"))
        self.populate_tree()

    def load_expanded_items(self):
        """Recursively load actual children for expanded items."""
        def traverse(item):
            if item.isExpanded():
                if item.childCount() == 1 and item.child(0).text(0) == "Loading...":
                    # Remove dummy child
                    item.removeChild(item.child(0))
                    # Populate actual children
                    parent_path = item.data(0, Qt.ItemDataRole.UserRole)
                    self.add_sub_items(item, parent_path)
                # Recursively traverse children
                for i in range(item.childCount()):
                    traverse(item.child(i))

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            traverse(root.child(i))

    def open_file_in_tab(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            file_name = os.path.basename(file_path)
            logging.info(f"Opening file in tab: {file_path}")
            if hasattr(self.main_window, 'add_new_tab'):
                self.main_window.add_new_tab(content, title=file_name, file_path=file_path)
            else:
                logging.error("MainWindow does not have add_new_tab method.")
                QMessageBox.critical(self, "Error", "Internal error: Could not open the file in a new tab.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")
            logging.error(f"Error opening file '{file_path}': {e}")

class SettingsContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        label = QLabel("Settings Container")
        layout.addWidget(label)
        # Add more complex widgets here

class PluginsContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        label = QLabel("Plugins Container")
        layout.addWidget(label)
        # Add more complex widgets here

class ContainersManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize layout for containers
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Dictionary to hold container widgets
        self.containers = {}
        self.current_container = None

    def add_container(self, index, title, content_widget=None):
        """
        Adds a new container.
        :param index: Unique identifier for the container.
        :param title: Title of the container.
        :param content_widget: The widget/content to display in the container.
        """
        if content_widget is None:
            content_widget = QLabel(f"{title} Content")
            content_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ensure the container stretches appropriately
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.containers[index] = content_widget

    def show_container(self, index):
        """
        Shows the specified container and hides others.
        :param index: Identifier of the container to show.
        """
        if self.current_container == index:
            self.hide_current_container()
            return

        # Hide the currently visible container
        if self.current_container is not None:
            self.layout.removeWidget(self.containers[self.current_container])
            self.containers[self.current_container].setVisible(False)

        # Show the new container
        self.layout.addWidget(self.containers[index])
        self.containers[index].setVisible(True)
        self.current_container = index

    def hide_current_container(self):
        """
        Hides the currently visible container.
        """
        if self.current_container is not None:
            self.layout.removeWidget(self.containers[self.current_container])
            self.containers[self.current_container].setVisible(False)
            self.current_container = None

    def clear_containers(self):
        """
        Removes all containers from the layout.
        """
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        self.current_container = None