from PyQt6.QtGui import QPainter, QFontMetrics
from PyQt6.QtCore import QRect, QSize, Qt

from src.editor.themes.theme import Theme

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PaintingMixin:
    def paintEvent(self, event):
        if not hasattr(self, 'lines') or not self.lines:
            return

        painter = QPainter(self.viewport())
        painter.setFont(self.font())
        fm = painter.fontMetrics()

        x_offset = self.horizontalScrollBar().value()
        y_offset = self.verticalScrollBar().value()
        line_height = fm.height()
        y_text_offset = fm.ascent()
        visible_rect = event.rect()

        # Calculate visible line range
        first_visible_line = max(0, int((y_offset + visible_rect.top()) / line_height))
        last_visible_line = min(len(self.lines) - 1, int((y_offset + visible_rect.bottom()) / line_height))

        # Ensure highlighted_lines exists and has correct length
        if not hasattr(self, 'highlighted_lines') or len(self.highlighted_lines) != len(self.lines):
            self.highlighted_lines = [{} for _ in self.lines]

        # Draw selection background first
        selection = self.selection_range()
        if selection:
            start_line, start_col, end_line, end_col = selection
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(Theme.SELECTION_COLOR)
            for i in range(start_line, end_line + 1):
                if i < first_visible_line or i > last_visible_line or i >= len(self.lines):
                    continue
                line = self.lines[i]
                line_y = (i * line_height) - y_offset
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
                x_start = fm.horizontalAdvance(line[:sel_start_col]) - x_offset
                x_end = fm.horizontalAdvance(line[:sel_end_col]) - x_offset
                rect = QRect(x_start, line_y, x_end - x_start, line_height)
                painter.fillRect(rect, Theme.SELECTION_COLOR)

        # Draw text with syntax highlighting
        painter.setPen(Theme.TEXT_COLOR)
        for i in range(first_visible_line, last_visible_line + 1):
            if i >= len(self.lines):
                break

            line = self.lines[i]
            line_y = y_text_offset + (i * line_height) - y_offset
            x = -x_offset

            # Get highlighting spans safely
            try:
                spans = self.highlighted_lines[i] if i < len(self.highlighted_lines) else {}
            except (IndexError, AttributeError):
                spans = {}

            if not spans:
                # No highlighting, draw the whole line with default color
                painter.setPen(Theme.TEXT_COLOR)
                painter.drawText(x, line_y, line)
            else:
                # Draw text with highlighting
                pos = 0
                for span in spans:
                    span_start, length, format_name = span
                    # Draw any text before the span
                    if pos < span_start:
                        text = line[pos:span_start]
                        painter.setPen(Theme.TEXT_COLOR)
                        painter.drawText(x, line_y, text)
                        x += fm.horizontalAdvance(text)
                        pos = span_start

                    # Draw the highlighted span
                    text = line[span_start:span_start + length]
                    color = Theme.SYNTAX_COLORS.get(format_name, Theme.TEXT_COLOR)
                    painter.setPen(color)
                    painter.drawText(x, line_y, text)
                    x += fm.horizontalAdvance(text)
                    pos += length

                # Draw any remaining text after the last span
                if pos < len(line):
                    text = line[pos:]
                    painter.setPen(Theme.TEXT_COLOR)
                    painter.drawText(x, line_y, text)

        # Draw cursor
        if self.hasFocus() and self.cursor_visible:
            # Ensure cursor position is valid
            cursor_line = min(self.cursor_line, len(self.lines) - 1)
            cursor_line = max(0, cursor_line)
            line = self.lines[cursor_line]
            cursor_column = min(self.cursor_column, len(line))
            cursor_column = max(0, cursor_column)

            cursor_x = fm.horizontalAdvance(line[:cursor_column]) - x_offset
            cursor_y = (cursor_line * line_height) - y_offset

            cursor_rect = QRect(cursor_x, cursor_y, 2, line_height)
            painter.fillRect(cursor_rect, Theme.CURSOR_COLOR)

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        line_height = fm.height()
        content_width = max(fm.horizontalAdvance(line) for line in self.lines) + 20
        content_height = line_height * len(self.lines) + 20
        return QSize(content_width, content_height)

