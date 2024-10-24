from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from ui.custom_title_bar import CustomTitleBar
from editor.texteditor import TextEditor
from editor.theme import Theme

from actions.fileoperations import FileOperationsMixin
from actions.editactions import EditActionsMixin

from ui.custom_tab_widget import CustomTabWidget
from ui.sidebar import Sidebar

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

        # Create container area (to hold the containers)
        self.container_area = QWidget()
        self.container_area.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.container_layout = QVBoxLayout(self.container_area)
        self.container_layout.setContentsMargins(0, 0, 0, 0)  # Ensure no extra margins
        self.container_layout.setSpacing(0)
        self.container_area.setVisible(False)
        content_layout.addWidget(self.container_area)

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

        # Add an initial tab
        self.add_new_tab()

        # Initialize containers
        self.containers = {}
        self.current_container_index = None

        # Add icons to the sidebar
        self.add_sidebar_icons()

        # Connect sidebar signals
        self.sidebar.icon_clicked.connect(self.toggle_container)

    def add_sidebar_icons(self):
        # Use the same logo for both icons for now
        icon_path = "resources/icons/logo.svg"

        # Add first icon
        self.sidebar.add_icon(icon_path, index=1)
        # Create first container
        container1 = QWidget()
        container1.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        container1_layout = QVBoxLayout(container1)
        container1_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        label1 = QLabel("Container 1")
        container1_layout.addWidget(label1)
        self.containers[1] = container1

        # Add second icon
        self.sidebar.add_icon(icon_path, index=2)
        # Create second container
        container2 = QWidget()
        container2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        container2_layout = QVBoxLayout(container2)
        container2_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        label2 = QLabel("Container 2")
        container2_layout.addWidget(label2)
        self.containers[2] = container2

    def toggle_container(self, index):
        # If the container is already visible and is the current one, hide it
        if self.current_container_index == index:
            # Remove existing container
            self.clear_container_layout()
            self.container_area.setVisible(False)
            self.v_line2.setVisible(False)  # Hide vertical line
            self.current_container_index = None
        else:
            # Remove existing container if any
            self.clear_container_layout()
            # Add new container
            self.container_layout.addWidget(self.containers[index])
            self.container_area.setVisible(True)
            self.v_line2.setVisible(True)  # Show vertical line
            self.current_container_index = index

    def clear_container_layout(self):
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def new_file(self):
        """Create a new file in a new tab."""
        self.add_new_tab()

    def add_new_tab(self, content='', title='Untitled', file_path=None):
        """Add a new tab with a TextEditor widget."""
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins as needed
        layout.setSpacing(0)
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

    def show_about_dialog(self):
        """Display an About dialog."""
        QMessageBox.information(self, "About", "My Custom Text Editor\nBuilt with PyQt6")

    def new_file(self):
        """Create a new file in a new tab."""
        self.add_new_tab()

    def add_new_tab(self, content='', title='Untitled', file_path=None):
        """Add a new tab with a TextEditor widget."""
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins as needed
        layout.setSpacing(0)
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

    def show_about_dialog(self):
        """Display an About dialog."""
        QMessageBox.information(self, "About", "My Custom Text Editor\nBuilt with PyQt6")
