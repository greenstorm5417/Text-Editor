from actions.actions import Action

class UndoRedoMixin:
    # Undo and redo stacks
    undo_stack = []
    redo_stack = []

    def add_undo_action(self, action_type, position, text, cursor_before):
        """Add an action to the undo stack."""
        cursor_after = (self.cursor_line, self.cursor_column)
        action = Action(action_type, position, text,
                        cursor_before=cursor_before,
                        cursor_after=cursor_after)
        self.undo_stack.append(action)
        self.redo_stack.clear()
        if not self._is_modified:
            self.set_modified(True)  # Use the setter method
        if self.main_window:
            self.modifiedChanged.emit(self)  # Emit signal with self

    def undo(self):
        if not self.undo_stack:
            return
        action = self.undo_stack.pop()
        self.apply_action(action, undo=True)
        self.redo_stack.append(action)
        self.update()

    def redo(self):
        if not self.redo_stack:
            return
        action = self.redo_stack.pop()
        self.apply_action(action, undo=False)
        self.undo_stack.append(action)
        self.update()

    def apply_action(self, action, undo=False):
        if undo:
            if action.action_type == 'insert':
                self.delete_text(action.position, action.text)
                self.cursor_line, self.cursor_column = action.cursor_before
            elif action.action_type == 'delete':
                self.insert_text(action.position, action.text)
                self.cursor_line, self.cursor_column = action.cursor_before
            self.set_modified(True)
        else:
            if action.action_type == 'insert':
                self.insert_text(action.position, action.text)
                self.cursor_line, self.cursor_column = action.cursor_after
            elif action.action_type == 'delete':
                self.delete_text(action.position, action.text)
                self.cursor_line, self.cursor_column = action.cursor_after
            self.set_modified(True)
        self.update()

    def insert_text(self, position, text):
        line_idx, col_idx = position
        lines_to_insert = text.split('\n')
        line = self.lines[line_idx]
        before = line[:col_idx]
        after = line[col_idx:]
        if len(lines_to_insert) == 1:
            self.lines[line_idx] = before + lines_to_insert[0] + after
        else:
            self.lines[line_idx] = before + lines_to_insert[0]
            for i in range(1, len(lines_to_insert)):
                self.lines.insert(line_idx + i, lines_to_insert[i])
            self.lines[line_idx + len(lines_to_insert) - 1] += after

    def delete_text(self, position, text):
        start_line, start_col = position
        end_line, end_col = self.get_end_position(position, text)
        if start_line == end_line:
            line = self.lines[start_line]
            self.lines[start_line] = line[:start_col] + line[end_col:]
        else:
            start_line_text = self.lines[start_line][:start_col]
            end_line_text = self.lines[end_line][end_col:]
            self.lines[start_line:end_line + 1] = [start_line_text + end_line_text]

    def get_end_position(self, position, text):
        lines = text.split('\n')
        line_idx, col_idx = position
        if len(lines) == 1:
            end_line = line_idx
            end_col = col_idx + len(lines[0])
        else:
            end_line = line_idx + len(lines) - 1
            end_col = len(lines[-1])
        return end_line, end_col
