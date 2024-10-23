from PyQt6.QtWidgets import QTabBar
from PyQt6.QtGui import QPainter, QPaintEvent, QMouseEvent, QFontMetrics, QCursor, QColor
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
        self.setTabsClosable(True)
        self.setExpanding(False)  # Prevent tabs from expanding to fill the width

        # Close button size
        self.close_button_size = Theme.scaled_size(16)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setHeight(Theme.scaled_size(Theme.TAB_BAR_HEIGHT))
        size.setWidth(Theme.scaled_size(120))  # Adjust as needed
        return size

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(Theme.get_tab_font())
        font_metrics = QFontMetrics(painter.font())

        for index in range(self.count()):
            rect = self.tabRect(index)
            is_selected = (index == self.currentIndex())

            # Background
            if is_selected:
                painter.setBrush(Theme.TAB_ACTIVE_BACKGROUND_COLOR)
            else:
                painter.setBrush(Theme.TAB_BACKGROUND_COLOR)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)

            # Text
            painter.setPen(Theme.TAB_TEXT_COLOR)
            tab_text = self.tabText(index)
            text_rect = QRect(
                rect.left() + Theme.scaled_size(10),
                rect.top(),
                rect.width() - self.close_button_size - Theme.scaled_size(20),
                rect.height()
            )
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, tab_text)

            # Close Button
            close_rect = QRect(
                rect.right() - self.close_button_size - Theme.scaled_size(5),
                rect.top() + (rect.height() - self.close_button_size) // 2,
                self.close_button_size,
                self.close_button_size
            )
            cursor_pos = self.mapFromGlobal(QCursor.pos())
            if close_rect.contains(cursor_pos):
                painter.setBrush(Theme.CLOSE_BUTTON_HOVER_COLOR)
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(close_rect)

            # Draw 'X' symbol for close button
            painter.setPen(Theme.TAB_TEXT_COLOR)
            painter.drawLine(
                close_rect.topLeft() + QPoint(3, 3),
                close_rect.bottomRight() - QPoint(3, 3)
            )
            painter.drawLine(
                close_rect.topRight() + QPoint(-3, 3),
                close_rect.bottomLeft() + QPoint(3, -3)
            )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            for index in range(self.count()):
                rect = self.tabRect(index)
                close_rect = QRect(
                    rect.right() - self.close_button_size - Theme.scaled_size(5),
                    rect.top() + (rect.height() - self.close_button_size) // 2,
                    self.close_button_size,
                    self.close_button_size
                )
                if close_rect.contains(pos):
                    self.tabCloseRequested.emit(index)
                    return
        super().mousePressEvent(event)
