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

        # Split clipboard text into lines
        lines_to_paste = clipboard_text.split('\n')
        if not lines_to_paste:
            return

        # Add paste action to undo stack
        self.add_undo_action('insert', (self.cursor_line, self.cursor_column), clipboard_text, cursor_before)

        # Handle first line
        line = self.lines[self.cursor_line]
        before_cursor = line[:self.cursor_column]
        after_cursor = line[self.cursor_column:]
        self.lines[self.cursor_line] = before_cursor + lines_to_paste[0]

        # Insert any additional lines
        for i in range(1, len(lines_to_paste)):
            self.lines.insert(self.cursor_line + i, lines_to_paste[i])

        # Append the remaining text after the cursor to the last inserted line
        if len(lines_to_paste) > 1:
            self.lines[self.cursor_line + len(lines_to_paste) - 1] += after_cursor

        # Update cursor position safely
        self.cursor_line = min(self.cursor_line + len(lines_to_paste) - 1, len(self.lines) - 1)
        last_line = self.lines[self.cursor_line]
        if len(lines_to_paste) == 1:
            # For single-line paste, cursor should be at the end of pasted content plus original position
            self.cursor_column = len(before_cursor) + len(lines_to_paste[0])
        else:
            # For multi-line paste, cursor should be at the end of pasted content before the remaining text
            self.cursor_column = len(last_line) - len(after_cursor)
        
        # Ensure cursor position is valid
        self.cursor_column = min(self.cursor_column, len(last_line))
        
        # Clear selection after paste
        self.clear_selection()
        
        self.after_text_change()
        self.ensure_cursor_visible()
        self.updateGeometry()
        self.update_highlighting()
        self.update_line_number_area_width(0)
        self.line_number_area.update()
        self.update_scrollbars()
        