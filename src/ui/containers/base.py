import logging
import os
import shutil
import subprocess
import sys

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QDrag, QPainter, QAction
from PyQt6.QtWidgets import ( QWidget, QVBoxLayout, QLabel, QSizePolicy, )

from src.editor.themes.theme import Theme

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ContainersManager(QWidget):
    """Manages multiple container widgets within a parent widget."""

    def __init__(self, parent=None):
        """
        Initialize the ContainersManager.

        :param parent: The parent widget.
        """
        super().__init__(parent)

        # Set up the main vertical layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Dictionary to store container widgets with their unique identifiers
        self.containers = {}
        self.current_container = None

    def add_container(self, index, title, content_widget=None):
        """
        Add a new container to the manager.

        :param index: Unique identifier for the container.
        :param title: Title of the container.
        :param content_widget: Optional widget to display inside the container.
                               If not provided, a QLabel with placeholder text is used.
        """
        if content_widget is None:
            content_widget = QLabel(f"{title} Content")
            content_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ensure the content widget expands to fill available space
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.containers[index] = content_widget
        logging.debug(f"Added container '{title}' with index '{index}'.")

    def show_container(self, index):
        """
        Display the specified container and hide the currently visible one.

        :param index: Identifier of the container to display.
        """
        if self.current_container == index:
            self.hide_current_container()
            logging.debug(f"Toggled visibility of container '{index}'.")
            return

        # Hide the currently visible container, if any
        if self.current_container is not None:
            current_widget = self.containers[self.current_container]
            self.layout.removeWidget(current_widget)
            current_widget.setVisible(False)
            logging.debug(f"Hidden container '{self.current_container}'.")

        # Show the new container
        new_widget = self.containers.get(index)
        if new_widget:
            self.layout.addWidget(new_widget)
            new_widget.setVisible(True)
            self.current_container = index
            logging.debug(f"Displayed container '{index}'.")
        else:
            logging.warning(f"Container with index '{index}' does not exist.")

    def hide_current_container(self):
        """
        Hide the currently visible container, if any.
        """
        if self.current_container is not None:
            current_widget = self.containers[self.current_container]
            self.layout.removeWidget(current_widget)
            current_widget.setVisible(False)
            logging.debug(f"Hidden container '{self.current_container}'.")
            self.current_container = None

    def clear_containers(self):
        """
        Remove all containers from the layout and reset the manager.
        """
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                logging.debug(f"Removed container '{widget}'.")
        self.containers.clear()
        self.current_container = None
        logging.debug("Cleared all containers.")
