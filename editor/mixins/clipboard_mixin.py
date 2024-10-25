from PyQt6.QtWidgets import QApplication

class ClipboardMixin:
    def copy(self):
        clipboard = QApplication.instance().clipboard()
        if self.has_selection():
            selected_text = self.get_selected_text()
            clipboard.setText(selected_text)

    def cut(self):
        clipboard = QApplication.instance().clipboard()
        if self.has_selection():
            self.copy()
            self.delete_selection()
            self.update()

    def paste(self):
        clipboard = QApplication.instance().clipboard()
        clipboard_text = clipboard.text()
        cursor_before = (self.cursor_line, self.cursor_column)

        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
            self.delete_selection()

        # Add paste action to undo stack
        self.add_undo_action('insert', (self.cursor_line, self.cursor_column), clipboard_text, cursor_before)

        lines_to_paste = clipboard_text.split('\n')

        # Insert the first line at the cursor position
        line = self.lines[self.cursor_line]
        before_cursor = line[:self.cursor_column]
        after_cursor = line[self.cursor_column:]
        self.lines[self.cursor_line] = before_cursor + lines_to_paste[0]

        # Insert any additional lines
        for i in range(1, len(lines_to_paste)):
            self.lines.insert(self.cursor_line + i, lines_to_paste[i])

        # Append the remaining text after the cursor to the last inserted line
        self.lines[self.cursor_line + len(lines_to_paste) - 1] += after_cursor

        # Update cursor position
        self.cursor_line += len(lines_to_paste) - 1
        self.cursor_column = len(self.lines[self.cursor_line]) - len(after_cursor)

        self.update()
