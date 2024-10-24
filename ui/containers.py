# ui/containers.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from editor.theme import Theme

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
