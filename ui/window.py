from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSizePolicy, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from ui.custom_title_bar import CustomTitleBar
from editor.texteditor import TextEditor
from editor.theme import Theme

from actions.fileoperations import FileOperationsMixin
from actions.editactions import EditActionsMixin

from ui.custom_tab_widget import CustomTabWidget
from ui.sidebar import Sidebar
from ui.containers import ContainersManager, SettingsContainer, PluginsContainer, FileTreeContainer  # Import FileTreeContainer

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

        # Add an initial tab
        self.add_new_tab()

        # Add icons to the sidebar and corresponding containers
        self.add_sidebar_icons()

        # Connect sidebar signals
        self.sidebar.icon_clicked.connect(self.toggle_container)

    def add_sidebar_icons(self):
        # Define icons and their corresponding container indices
        # Assign index=1 for File Tree, index=2 for Settings, index=3 for Plugins
        icons = [
            ("resources/icons/logo.svg", 1),  
            ("resources/icons/logo.svg", 2), 
            ("resources/icons/logo.svg", 3)  
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
                    return index

        # Create a new tab widget
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing

        # Initialize the TextEditor
        text_editor = TextEditor(content, file_path, self)  # Pass self to TextEditor
        text_editor.modifiedChanged.connect(self.update_tab_title)  # Connect the signal

        # Create a QScrollArea and set the TextEditor as its widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(text_editor)
        scroll_area.setWidgetResizable(True)  # Ensure the TextEditor resizes with the scroll area

        # Add the scroll area to the tab's layout
        layout.addWidget(scroll_area)

        # Add the new tab to the tab widget
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentIndex(index)
        return index

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

    def show_about_dialog(self):
        """Display an About dialog."""
        QMessageBox.information(self, "About", "My Custom Text Editor\nBuilt with PyQt6")
