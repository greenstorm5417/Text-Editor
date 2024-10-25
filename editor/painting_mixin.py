# In editor/painting_mixin.py
from PyQt6.QtGui import QPainter, QFontMetrics
from PyQt6.QtCore import QRect, QSize
from editor.theme import Theme

class PaintingMixin:
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font())
        fm = painter.fontMetrics()

        line_height = fm.height()
        y_offset = fm.ascent()

        # Use the event's rect to get the clipping rectangle
        visible_rect = event.rect()

        # Calculate first and last visible lines
        first_visible_line = max(0, int(visible_rect.top() / line_height))
        last_visible_line = min(len(self.lines) - 1, int(visible_rect.bottom() / line_height))

        # Draw selection background if there is a selection
        selection = self.selection_range()
        if selection:
            start_line, start_col, end_line, end_col = selection
            for i in range(start_line, end_line + 1):
                if i < first_visible_line or i > last_visible_line:
                    continue  # Skip non-visible lines
                line = self.lines[i]
                line_y = y_offset + (i * line_height)
                if i == start_line:
                    sel_start_col = start_col
                else:
                    sel_start_col = 0
                if i == end_line:
                    sel_end_col = end_col
                else:
                    sel_end_col = len(line)
                if sel_start_col == sel_end_col:
                    continue
                x_start = fm.horizontalAdvance(line[:sel_start_col])
                x_end = fm.horizontalAdvance(line[:sel_end_col])
                rect = QRect(x_start, line_y - y_offset, x_end - x_start, line_height)
                painter.fillRect(rect, Theme.SELECTION_COLOR)

        # Draw each visible line of text
        painter.setPen(Theme.TEXT_COLOR)
        for i in range(first_visible_line, last_visible_line + 1):
            line = self.lines[i]
            line_y = y_offset + (i * line_height)
            painter.drawText(0, line_y, line)

        # Calculate cursor position
        cursor_x = fm.horizontalAdvance(self.lines[self.cursor_line][:self.cursor_column])
        cursor_y = self.cursor_line * line_height

        # Draw the cursor using color from Theme
        if self.hasFocus() and self.cursor_visible:
            cursor_rect = QRect(cursor_x, cursor_y, 2, line_height)
            painter.fillRect(cursor_rect, Theme.CURSOR_COLOR)

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        line_height = fm.height()
        # Limit the width to a reasonable maximum (e.g., the viewport width or a fixed value)
        max_width = self.parent().width() if self.parent() else 800
        content_width = min(max(fm.horizontalAdvance(line) for line in self.lines) + 20, max_width)
        content_height = line_height * len(self.lines) + 20  # Added padding
        return QSize(content_width, content_height)
