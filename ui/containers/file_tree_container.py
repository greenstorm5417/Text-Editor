from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QToolButton, QHBoxLayout, QInputDialog, QMessageBox, QSizePolicy,
    QTreeWidget, QTreeWidgetItem, QMenu
)
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
        self.setFont(Theme.get_default_font())
        
        # Configure drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectItems)

                
        # Apply theme styling

        self.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {Theme.FILE_TREE_BACKGROUND_COLOR.name()};
                color: {Theme.FILE_TREE_TEXT_COLOR.name()};
                border: none;
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border: none;
            }}
            QTreeWidget::item:selected {{
                background-color: {Theme.FILE_TREE_SELECTED_BACKGROUND.name()};
                color: {Theme.FILE_TREE_SELECTED_TEXT_COLOR.name()};
            }}
            QTreeWidget::item:hover {{
                background-color: {Theme.FILE_TREE_HOVER_BACKGROUND.name()};
            }}
            QTreeWidget::branch {{
                background-color: {Theme.FILE_TREE_BACKGROUND_COLOR.name()};
            }}
            QTreeWidget::branch:selected {{
                background-color: {Theme.FILE_TREE_SELECTED_BACKGROUND.name()};
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: url(resources/icons/chevron-right.svg);
                padding: 2px;
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: url(resources/icons/chevron-down.svg);
                padding: 2px;
            }}
        """)

        # Assign default icons using SVGs
        # Initialize icons
        self.dir_icon = QIcon("resources/icons/default_folder.svg")
        self.default_file_icon = QIcon("resources/icons/default_file.svg")
        self.file_icons_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'file_icons')
        self.file_icon_cache = {}
        
        # Initialize state
        self.show_hidden = False
        self.main_window = main_window
        
        # Connect signals
        self.itemExpanded.connect(self.on_item_expanded)
        self.itemClicked.connect(self.on_item_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def get_file_icon(self, file_path):
        """
        Retrieves the QIcon for a given file based on its extension.
        Caches the icons to optimize performance.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower().lstrip('.')  # Normalize extension

        if not ext:
            # Files without an extension use the default file icon
            return self.default_file_icon

        if ext in self.file_icon_cache:
            return self.file_icon_cache[ext]

        # Construct the path to the specific file icon
        icon_filename = f"{ext}.svg"
        icon_full_path = os.path.join(self.file_icons_path, icon_filename)

        if os.path.exists(icon_full_path):
            icon = QIcon(icon_full_path)
            if not icon.isNull():
                self.file_icon_cache[ext] = icon
                logging.debug(f"Loaded icon for .{ext} files from {icon_full_path}")
                return icon

        # Fallback to default file icon if specific icon not found or invalid
        logging.warning(f"No icon found for .{ext} files. Using default file icon.")
        self.file_icon_cache[ext] = self.default_file_icon
        return self.default_file_icon

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
            open_action.setIcon(QIcon("resources/icons/open_file.svg"))  # New SVG icon for Open
            open_action.triggered.connect(lambda: self.parent().open_file_in_tab(path))
            menu.addAction(open_action)

        rename_action = QAction("Rename", self)
        rename_action.setIcon(QIcon("resources/icons/rename.svg"))  # New SVG icon for Rename
        rename_action.triggered.connect(lambda: self.rename_item(item, path))
        menu.addAction(rename_action)

        delete_action = QAction("Delete", self)
        delete_action.setIcon(QIcon("resources/icons/delete.svg"))  # New SVG icon for Delete
        delete_action.triggered.connect(lambda: self.delete_item(item, path))
        menu.addAction(delete_action)

        copy_path_action = QAction("Copy Path", self)
        copy_path_action.setIcon(QIcon("resources/icons/copy_path.svg"))  # New SVG icon for Copy Path
        copy_path_action.triggered.connect(lambda: self.copy_path(path))
        menu.addAction(copy_path_action)

        if os.path.isfile(path):
            open_external_action = QAction("Open in External Editor", self)
            open_external_action.setIcon(QIcon("resources/icons/external_editor.svg"))  # New SVG icon
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
                    dir_item.setIcon(0, self.dir_icon)  # Set directory icon
                    dir_item.setExpanded(False)  # Collapse by default
                    dir_item.setData(0, Qt.ItemDataRole.UserRole, entry_path)  # Store the full path

                    # Add a dummy child to make the item expandable
                    dummy_child = QTreeWidgetItem(dir_item)
                    dummy_child.setText(0, "Loading...")
                    logging.debug(f"Added dummy child to directory: {entry_path}")
                else:
                    file_item = QTreeWidgetItem(parent_item)
                    file_item.setText(0, entry)
                    file_item.setIcon(0, self.get_file_icon(entry_path))  # Corrected line
                    file_item.setData(0, Qt.ItemDataRole.UserRole, entry_path)  # Store the full path
                    logging.debug(f"Added file: {entry_path}")
        except PermissionError:
            # Skip directories for which the user does not have permissions
            logging.warning(f"Permission denied: {parent_path}")
            pass
        except Exception as e:
            logging.error(f"Error accessing {parent_path}: {e}")


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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Set container width from theme
        self.setFixedWidth(Theme.scaled_size(Theme.FILE_TREE_CONTAINER_WIDTH))
        
        # Create toolbar widget
        self.toolbar = QWidget()
        self.toolbar.setFixedHeight(Theme.scaled_size(Theme.TOOLBAR_BUTTON_HEIGHT))
        self.toolbar.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.FILE_TREE_HEADER_BACKGROUND.name()};
                border-bottom: 1px solid {Theme.FILE_TREE_GRID_COLOR.name()};
            }}
        """)
        
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(
            Theme.TOOLBAR_BUTTON_MARGIN,
            Theme.TOOLBAR_BUTTON_MARGIN,
            Theme.TOOLBAR_BUTTON_MARGIN,
            Theme.TOOLBAR_BUTTON_MARGIN
        )
        toolbar_layout.setSpacing(Theme.TOOLBAR_BUTTON_MARGIN)

        # Create toolbar buttons with theme styling
        button_style = f"""
            QToolButton {{
                background-color: {Theme.SIDEBAR_BUTTON_COLOR.name()};
                border: none;
                border-radius: {Theme.TOOLBAR_BUTTON_RADIUS}px;
                padding: 4px;
            }}
            QToolButton:hover {{
                background-color: {Theme.SIDEBAR_BUTTON_HOVER_COLOR.name()};
            }}
            QToolButton:pressed {{
                background-color: {Theme.SIDEBAR_BUTTON_ACTIVE_COLOR.name()};
            }}
        """

        # Create File Button
        self.create_file_button = QToolButton()
        self.create_file_button.setIcon(QIcon("resources/icons/new_file.svg"))
        self.create_file_button.setToolTip("Create New File")
        self.create_file_button.setStyleSheet(button_style)
        self.create_file_button.clicked.connect(self.create_file)
        toolbar_layout.addWidget(self.create_file_button)

        # Create Folder Button
        self.create_folder_button = QToolButton()
        self.create_folder_button.setIcon(QIcon("resources/icons/new_folder.svg"))
        self.create_folder_button.setToolTip("Create New Folder")
        self.create_folder_button.setStyleSheet(button_style)
        self.create_folder_button.clicked.connect(self.create_folder)
        toolbar_layout.addWidget(self.create_folder_button)

        # Toggle Hidden Files Button
        self.toggle_hidden_button = QToolButton()
        self.toggle_hidden_button.setIcon(QIcon("resources/icons/show_hidden.svg"))
        self.toggle_hidden_button.setCheckable(True)
        self.toggle_hidden_button.setToolTip("Show Hidden Files")
        self.toggle_hidden_button.setStyleSheet(button_style)
        self.toggle_hidden_button.clicked.connect(self.toggle_hidden_files)
        toolbar_layout.addWidget(self.toggle_hidden_button)

        # Add stretch to push the title to the right
        toolbar_layout.addStretch()

        # Create Title Label with theme styling
        self.title_label = QLabel("File Tree")
        self.title_label.setFont(Theme.get_default_font())
        self.title_label.setStyleSheet(f"color: {Theme.FILE_TREE_HEADER_TEXT_COLOR.name()};")
        toolbar_layout.addWidget(self.title_label)

        # Add toolbar to main layout
        layout.addWidget(self.toolbar)

        # Initialize tree widget
        self.tree = FileTreeWidget(self.main_window, self)
        layout.addWidget(self.tree)

        # Initialize and style placeholder label
        self.placeholder_label = QLabel("Open a folder to display its contents.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setFont(Theme.get_default_font())
        self.placeholder_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.FILE_TREE_TEXT_COLOR.name()};
                background-color: {Theme.FILE_TREE_BACKGROUND_COLOR.name()};
                padding: 20px;
            }}
        """)
        layout.addWidget(self.placeholder_label)

        # Set initial visibility
        self.tree.setVisible(False)
        self.toolbar.setVisible(False)
        self.placeholder_label.setVisible(True)

    def create_context_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {Theme.FILE_TREE_BACKGROUND_COLOR.name()};
                color: {Theme.FILE_TREE_TEXT_COLOR.name()};
                border: 1px solid {Theme.FILE_TREE_GRID_COLOR.name()};
            }}
            QMenu::item:selected {{
                background-color: {Theme.FILE_TREE_SELECTED_BACKGROUND.name()};
            }}
        """)
        return menu

    
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
            self.toolbar.setVisible(True)
            self.toggle_hidden_button.setChecked(False)
            self.toggle_hidden_button.setToolTip("Show Hidden Files")
            self.toggle_hidden_button.setIcon(QIcon("resources/icons/show_hidden.svg"))
        else:
            self.placeholder_label.setVisible(True)
            self.tree.setVisible(False)
            self.toolbar.setVisible(False)

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
                    file_item.setIcon(0, self.tree.get_file_icon(entry_path))  # Corrected line
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
            self.toggle_hidden_button.setIcon(QIcon("resources/icons/hide_hidden.svg"))  # Updated to SVG
        else:
            self.toggle_hidden_button.setToolTip("Show Hidden Files")
            self.toggle_hidden_button.setIcon(QIcon("resources/icons/show_hidden.svg"))  # Updated to SVG
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
