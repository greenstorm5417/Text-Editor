from PyQt6.QtGui import QPainter, QFontMetrics
from PyQt6.QtCore import QRect, QSize, Qt

from editor.theme import Theme

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PaintingMixin:
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setFont(self.font())
        fm = painter.fontMetrics()

        # Get the scroll positions
        x_offset = self.horizontalScrollBar().value()
        y_offset = self.verticalScrollBar().value()

        line_height = fm.height()
        y_text_offset = fm.ascent()

        # Use the event's rect to get the clipping rectangle
        visible_rect = event.rect()

        # Calculate first and last visible lines
        first_visible_line = max(0, int((y_offset + visible_rect.top()) / line_height))
        last_visible_line = min(len(self.lines) - 1, int((y_offset + visible_rect.bottom()) / line_height))

        # Draw selection background if there is a selection
        selection = self.selection_range()
        if selection:
            start_line, start_col, end_line, end_col = selection
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(Theme.SELECTION_COLOR)
            for i in range(start_line, end_line + 1):
                if i < first_visible_line or i > last_visible_line:
                    continue  # Skip non-visible lines
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

        # Draw each visible line of text
        painter.setPen(Theme.TEXT_COLOR)
        # For each visible line
        for i in range(first_visible_line, last_visible_line + 1):
            line = self.lines[i]
            line_y = y_text_offset + (i * line_height) - y_offset
            x = -x_offset
            spans = self.highlighted_lines[i] if self.highlighted_lines else []

            if not spans:
                # No highlighting info, draw the entire line
                painter.setPen(Theme.TEXT_COLOR)
                painter.drawText(x, line_y, line)
            else:
                # Draw each span
                pos = 0
                for span in spans:
                    span_start, length, format_name = span
                    if pos < span_start:
                        # Draw text between spans
                        text = line[pos:span_start]
                        painter.setPen(Theme.TEXT_COLOR)
                        painter.drawText(x, line_y, text)
                        x += fm.horizontalAdvance(text)
                        pos = span_start
                    # Draw the span
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

        # Calculate cursor position
        if self.hasFocus() and self.cursor_visible:
            cursor_x = fm.horizontalAdvance(self.lines[self.cursor_line][:self.cursor_column]) - x_offset
            cursor_y = (self.cursor_line * line_height) - y_offset

            # Draw the cursor using color from Theme
            cursor_rect = QRect(cursor_x, cursor_y, 2, line_height)
            painter.fillRect(cursor_rect, Theme.CURSOR_COLOR)



    def sizeHint(self):
        fm = QFontMetrics(self.font())
        line_height = fm.height()
        content_width = max(fm.horizontalAdvance(line) for line in self.lines) + 20  # Added padding
        content_height = line_height * len(self.lines) + 20  # Added padding
        return QSize(content_width, content_height)

