from PyQt6.QtWidgets import QPushButton, QMenu
from PyQt6.QtGui import QPainter, QPaintEvent
from PyQt6.QtCore import Qt, QPoint
from src.editor.themes.theme import Theme

class CustomButton(QPushButton):
    def __init__(self, text='', parent=None,
                 background_color=Theme.BACKGROUND_COLOR,
                 hover_color=Theme.HOVER_COLOR,
                 text_color=Theme.TEXT_COLOR,
                 font_size=Theme.BUTTON_FONT_SIZE,
                 font_weight=Theme.BUTTON_FONT_WEIGHT):
        super().__init__(text, parent)
        self.default_background_color = background_color
        self.hover_background_color = hover_color
        self.current_background_color = self.default_background_color
        self.text_color = text_color
        self.font = Theme.get_button_font()
        self.setFont(self.font)
        self.setFixedSize(Theme.scaled_size(Theme.BUTTON_WIDTH), Theme.scaled_size(Theme.BUTTON_HEIGHT))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFlat(True)
        self.menu = None


    def setMenu(self, menu: QMenu):
        self.menu = menu

    def enterEvent(self, event):
        self.current_background_color = self.hover_background_color
        self.update()

    def leaveEvent(self, event):
        self.current_background_color = self.default_background_color
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.menu:
            self.menu.exec(self.mapToGlobal(QPoint(0, self.height())))
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.current_background_color)
        painter.drawRect(self.rect())

        painter.setPen(self.text_color)
        painter.setFont(self.font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
