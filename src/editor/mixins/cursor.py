from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt

class CursorMixin:
    def move_cursor_to_previous_word(self):
        """Move cursor to the start of the previous token."""
        line = self.lines[self.cursor_line]
        
        if self.cursor_column == 0:
            if self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_column = len(self.lines[self.cursor_line])
            return

        # Get the token boundaries for the current position
        token_start, _ = self.get_token_boundaries(line, self.cursor_column - 1)
        self.cursor_column = token_start
        self.ensure_cursor_visible()

    def move_cursor_to_next_word(self):
        """Move cursor to the start of the next token."""
        line = self.lines[self.cursor_line]
        
        if self.cursor_column >= len(line):
            if self.cursor_line < len(self.lines) - 1:
                self.cursor_line += 1
                self.cursor_column = 0
            return

        # Get the token boundaries for the current position
        _, token_end = self.get_token_boundaries(line, self.cursor_column)
        self.cursor_column = token_end
        self.ensure_cursor_visible()

    def move_cursor_left(self):
        if self.cursor_column > 0:
            self.cursor_column -= 1
        elif self.cursor_line > 0:
            self.cursor_line -= 1
            self.cursor_column = len(self.lines[self.cursor_line])
        self.ensure_cursor_visible()

    def move_cursor_right(self):
        line_length = len(self.lines[self.cursor_line])
        if self.cursor_column < line_length:
            self.cursor_column += 1
        elif self.cursor_line < len(self.lines) - 1:
            self.cursor_line += 1
            self.cursor_column = 0
        self.ensure_cursor_visible()

    def move_cursor_up(self):
        if self.cursor_line > 0:
            self.cursor_line -= 1
            self.cursor_column = min(self.cursor_column, len(self.lines[self.cursor_line]))
            self.ensure_cursor_visible()

    def move_cursor_down(self):
        if self.cursor_line < len(self.lines) - 1:
            self.cursor_line += 1
            self.cursor_column = min(self.cursor_column, len(self.lines[self.cursor_line]))
            self.ensure_cursor_visible()
