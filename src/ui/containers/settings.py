from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QToolButton, QHBoxLayout, QInputDialog, QMessageBox, QSizePolicy,
    QTreeWidget, QTreeWidgetItem, QMenu
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QDrag, QPainter, QAction
from src.editor.themes.theme import Theme
import os
import sys
import shutil
import logging
import subprocess
from PyQt6.QtWidgets import QApplication

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SettingsContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        label = QLabel("Settings Container")
        layout.addWidget(label)
