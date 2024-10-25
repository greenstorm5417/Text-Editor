from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt

class CursorMixin:
    def move_cursor_left(self):
        if self.cursor_column > 0:
            self.cursor_column -= 1
        elif self.cursor_line > 0:
            self.cursor_line -= 1
            self.cursor_column = len(self.lines[self.cursor_line])

    def move_cursor_right(self):
        line_length = len(self.lines[self.cursor_line])
        if self.cursor_column < line_length:
            self.cursor_column += 1
        elif self.cursor_line < len(self.lines) - 1:
            self.cursor_line += 1
            self.cursor_column = 0

    def move_cursor_up(self):
        if self.cursor_line > 0:
            self.cursor_line -= 1
            self.cursor_column = min(self.cursor_column, len(self.lines[self.cursor_line]))

    def move_cursor_down(self):
        if self.cursor_line < len(self.lines) - 1:
            self.cursor_line += 1
            self.cursor_column = min(self.cursor_column, len(self.lines[self.cursor_line]))

    def move_cursor_to_previous_word(self):
        line = self.lines[self.cursor_line]
        index = self.cursor_column - 1

        if index < 0:
            if self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_column = len(self.lines[self.cursor_line])
                return
            else:
                return  # At the very beginning

        while index >= 0 and line[index].isspace():
            index -= 1

        while index >= 0 and not line[index].isspace():
            index -= 1

        self.cursor_column = index + 1

    def move_cursor_to_next_word(self):
        line = self.lines[self.cursor_line]
        index = self.cursor_column

        if index >= len(line):
            if self.cursor_line < len(self.lines) - 1:
                self.cursor_line += 1
                self.cursor_column = 0
                return
            else:
                return  # At the very end

        while index < len(line) and not line[index].isspace():
            index += 1

        while index < len(line) and line[index].isspace():
            index += 1

        self.cursor_column = index
