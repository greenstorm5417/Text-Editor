from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon
from src.editor.themes.theme import Theme

class Sidebar(QWidget):
    icon_clicked = pyqtSignal(int)  # Signal to indicate which icon was clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setFixedWidth(Theme.scaled_size(50))  # Adjust width as needed
        self.buttons = []

    def add_icon(self, icon_path, index):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        icon_size = Theme.scaled_size(30)
        button.setIconSize(QSize(icon_size, icon_size))
        button.setFixedSize(Theme.scaled_size(50), Theme.scaled_size(50))
        button.setFlat(True)
        button.setStyleSheet("background-color: transparent;")
        button.clicked.connect(lambda _, idx=index: self.icon_clicked.emit(idx))
        self.layout.addWidget(button)
        self.buttons.append(button)
