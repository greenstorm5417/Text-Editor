# ui/custom_tab_bar.py
from PyQt6.QtWidgets import QTabBar
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt
from editor.theme import Theme

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(Theme.get_tab_font())
        self.setFixedHeight(Theme.scaled_size(Theme.TAB_BAR_HEIGHT))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Enable movable tabs
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setExpanding(False)  # Prevent tabs from expanding to fill the width

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setHeight(Theme.scaled_size(Theme.TAB_BAR_HEIGHT))
        size.setWidth(Theme.scaled_size(120))  # Adjust as needed
        return size

    # Removed custom paintEvent

    # Ensure the close button works correctly
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
