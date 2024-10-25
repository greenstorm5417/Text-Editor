from PyQt6.QtGui import QMouseEvent, QFontMetrics
from PyQt6.QtCore import Qt

class SelectionMixin:
    def has_selection(self):
        return self.selection_start is not None and self.selection_end is not None and self.selection_start != self.selection_end

    def get_selected_text(self):
        if self.has_selection():
            start_line, start_col, end_line, end_col = self.selection_range()
            selected_lines = self.lines[start_line:end_line + 1]
            if start_line == end_line:
                selected_lines[0] = selected_lines[0][start_col:end_col]
            else:
                selected_lines[0] = selected_lines[0][start_col:]
                selected_lines[-1] = selected_lines[-1][:end_col]
            return '\n'.join(selected_lines)
        return ''

    def delete_selection(self):
        if self.has_selection():
            start_line, start_col, end_line, end_col = self.selection_range()
            if start_line == end_line:
                line = self.lines[start_line]
                self.lines[start_line] = line[:start_col] + line[end_col:]
            else:
                start_line_text = self.lines[start_line][:start_col]
                end_line_text = self.lines[end_line][end_col:]
                self.lines[start_line:end_line + 1] = [start_line_text + end_line_text]
            self.cursor_line = start_line
            self.cursor_column = start_col
            self.clear_selection()
            self.set_modified(True)  # Mark as modified after deletion

    def selection_range(self):
        if not self.has_selection():
            return None
        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end
        if (start_line, start_col) > (end_line, end_col):
            start_line, start_col, end_line, end_col = end_line, end_col, start_line, start_col
        return start_line, start_col, end_line, end_col

    def clear_selection(self):
        self.selection_start = None
        self.selection_end = None

    def select_all(self):
        self.selection_start = (0, 0)
        self.selection_end = (len(self.lines) - 1, len(self.lines[-1]))
        self.cursor_line = len(self.lines) - 1
        self.cursor_column = len(self.lines[-1])
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            fm = QFontMetrics(self.font())
            x = event.position().x() + self.horizontalScrollBar().value()
            y = event.position().y() + self.verticalScrollBar().value()
            line_height = fm.height()

            # Calculate line index
            clicked_line = int(y // line_height)
            clicked_line = max(0, min(clicked_line, len(self.lines) - 1))
            line = self.lines[clicked_line]

            # Calculate column index
            cumulative_width = 0
            column = 0
            for i, char in enumerate(line):
                char_width = fm.horizontalAdvance(char)
                if cumulative_width + char_width / 2 >= x:
                    column = i
                    break
                cumulative_width += char_width
            else:
                column = len(line)

            self.cursor_line = clicked_line
            self.cursor_column = column

            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if self.selection_start is None:
                    self.selection_start = (self.cursor_line, self.cursor_column)
                self.selection_end = (self.cursor_line, self.cursor_column)
            else:
                # For a single click, reset the selection
                self.clear_selection()
            super().mousePressEvent(event)  
            self.update()


    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            fm = QFontMetrics(self.font())
            x = event.position().x()
            y = event.position().y()
            line_height = fm.height()

            # Calculate line index
            clicked_line = int(y // line_height)
            clicked_line = max(0, min(clicked_line, len(self.lines) - 1))
            line = self.lines[clicked_line]

            # Calculate column index
            cumulative_width = 0
            column = 0
            for i, char in enumerate(line):
                char_width = fm.horizontalAdvance(char)
                if cumulative_width + char_width / 2 >= x:
                    column = i
                    break
                cumulative_width += char_width
            else:
                column = len(line)

            if self.selection_start is None:
                self.selection_start = (self.cursor_line, self.cursor_column)

            self.cursor_line = clicked_line
            self.cursor_column = column
            self.selection_end = (self.cursor_line, self.cursor_column)
            super().mouseMoveEvent(event)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        pass  # No action needed here for now
