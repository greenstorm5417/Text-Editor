from PyQt6.QtWidgets import QTabBar
from PyQt6.QtGui import QPainter, QPaintEvent, QMouseEvent
from PyQt6.QtCore import Qt, QRect, QPoint
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

        # Set the close button size
        self.close_button_size = Theme.scaled_size(16)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setHeight(Theme.scaled_size(Theme.TAB_BAR_HEIGHT))
        return size

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setFont(self.font())
        for index in range(self.count()):
            rect = self.tabRect(index)
            is_current = (self.currentIndex() == index)

            # Fill the background
            if is_current:
                painter.fillRect(rect, Theme.TAB_ACTIVE_BACKGROUND_COLOR)
            else:
                painter.fillRect(rect, Theme.TAB_BACKGROUND_COLOR)

            # Draw the tab text
            painter.setPen(Theme.TAB_TEXT_COLOR)
            text = self.tabText(index)
            text_rect = rect.adjusted(10, 0, -self.close_button_size - 10, 0)  # Adjust for close button
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)

            # Draw the close button if tabs are closable
            if self.tabsClosable():
                close_rect = QRect(
                    rect.right() - self.close_button_size - 5,
                    rect.top() + (rect.height() - self.close_button_size) // 2,
                    self.close_button_size,
                    self.close_button_size
                )
                # Draw the 'X' symbol
                painter.setPen(Theme.TAB_TEXT_COLOR)
                painter.drawText(close_rect, Qt.AlignmentFlag.AlignCenter, '✕')

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            index = self.tabAt(pos)
            if index != -1 and self.tabsClosable():
                rect = self.tabRect(index)
                close_rect = QRect(
                    rect.right() - self.close_button_size - 5,
                    rect.top() + (rect.height() - self.close_button_size) // 2,
                    self.close_button_size,
                    self.close_button_size
                )
                if close_rect.contains(pos):
                    self.tabCloseRequested.emit(index)
                    return
        super().mousePressEvent(event)
