from src.editor.actions.action import Action
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import time

class UndoRedoMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.undo_stack = []
        self.redo_stack = []
        self.current_text = ''
        self.text_start_position = None

    def handle_character_input(self, text, cursor_before):
        """Handle character input by grouping characters into words for undo/redo."""
        if self.has_selection():
            sel_text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), sel_text, cursor_before, "Replace Selection")
            self.delete_selection()

        # If this is a word-breaking character, commit any pending text
        is_word_break = text in ' \t\n.,;:!?()[]{}"\'+-*/=<>@#$%^&|\\~'
        
        if is_word_break and self.current_text:
            # First commit the accumulated text
            self.add_undo_action('insert', self.text_start_position, self.current_text, cursor_before, f"Insert Text")
            self.current_text = ''
            self.text_start_position = None
            # Then add the breaking character as its own action
            self.add_undo_action('insert', (self.cursor_line, self.cursor_column), text, cursor_before, f"Insert '{text}'")
        else:
            # Start a new word if needed
            if not self.current_text:
                self.text_start_position = (self.cursor_line, self.cursor_column)
            self.current_text += text

        # Update the text in the editor
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[:self.cursor_column] + text + line[self.cursor_column:]
        self.cursor_column += len(text)
        
        self.redo_stack.clear()
        self.after_text_change()

    def commit_pending_text(self):
        """Commit any pending text as an undo action."""
        if self.current_text and self.text_start_position:
            self.add_undo_action('insert', self.text_start_position, self.current_text, 
                               (self.text_start_position[0], self.text_start_position[1]), 
                               f"Insert Text")
            self.current_text = ''
            self.text_start_position = None

    def add_undo_action(self, action_type, position, text, cursor_before, description=""):
        """Add a new action to the undo stack."""
        cursor_after = (self.cursor_line, self.cursor_column)
        action = Action(
            action_type=action_type,
            position=position,
            text=text,
            cursor_before=cursor_before,
            cursor_after=cursor_after,
            description=description
        )
        self.undo_stack.append(action)
        self.redo_stack.clear()
        if not self._is_modified:
            self.set_modified(True)
        if self.main_window:
            self.modifiedChanged.emit(self)

    def undo(self):
        """Undo the last action."""
        self.commit_pending_text()  # Commit any pending text before undoing
        if not self.undo_stack:
            return
        action = self.undo_stack.pop()
        self.apply_action(action, undo=True)
        self.redo_stack.append(action)
        self.update()

    def redo(self):
        """Redo the previously undone action."""
        self.commit_pending_text()  # Commit any pending text before redoing
        if not self.redo_stack:
            return
        action = self.redo_stack.pop()
        self.apply_action(action, undo=False)
        self.undo_stack.append(action)
        self.update()

    def apply_action(self, action, undo=False):
        """Apply an undo/redo action."""
        if undo:
            if action.action_type == 'insert':
                self.delete_text(action.position, action.text)
                self.cursor_line, self.cursor_column = action.cursor_before
            elif action.action_type == 'delete':
                self.insert_text(action.position, action.text)
                self.cursor_line, self.cursor_column = action.cursor_before
        else:
            if action.action_type == 'insert':
                self.insert_text(action.position, action.text)
                self.cursor_line, self.cursor_column = action.cursor_after
            elif action.action_type == 'delete':
                self.delete_text(action.position, action.text)
                self.cursor_line, self.cursor_column = action.cursor_after

        if hasattr(self, 'highlighter') and self.highlighter:
            self.highlighted_lines = self.highlighter.highlight(self.lines)
        else:
            self.highlighted_lines = [{} for _ in self.lines]

        self.synchronize_editor_state()
        self.update()

    def insert_text(self, position, text):
        """Insert text at the given position."""
        line_idx, col_idx = position
        lines_to_insert = text.split('\n')
        line = self.lines[line_idx]
        before = line[:col_idx]
        after = line[col_idx:]
        
        if len(lines_to_insert) == 1:
            # Single line insertion
            self.lines[line_idx] = before + lines_to_insert[0] + after
        else:
            # Multi-line insertion
            self.lines[line_idx] = before + lines_to_insert[0]
            for i in range(1, len(lines_to_insert) - 1):
                self.lines.insert(line_idx + i, lines_to_insert[i])
            last_line_idx = line_idx + len(lines_to_insert) - 1
            self.lines.insert(last_line_idx, lines_to_insert[-1] + after)

    def delete_text(self, position, text):
        """Delete text at the given position."""
        start_line, start_col = position
        lines = text.split('\n')
        
        if len(lines) == 1:
            # Single line deletion
            line = self.lines[start_line]
            self.lines[start_line] = line[:start_col] + line[start_col + len(text):]
        else:
            # Multi-line deletion
            first_line = self.lines[start_line]
            last_line = self.lines[start_line + len(lines) - 1]
            self.lines[start_line] = first_line[:start_col] + last_line[len(lines[-1]):]
            del self.lines[start_line + 1:start_line + len(lines)]

    def handle_backspace(self, cursor_before):
        """Handle backspace with word-based undo support."""
        self.commit_pending_text()  # Commit any pending text before backspace

        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before, "Delete Selection")
            self.delete_selection()
            return

        line = self.lines[self.cursor_line]
        if self.cursor_column > 0:
            # Ctrl+Backspace: Delete the previous word
            if QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier:
                # Find start of current word
                pos = self.cursor_column - 1
                while pos > 0 and line[pos-1].isspace():
                    pos -= 1
                while pos > 0 and not line[pos-1].isspace():
                    pos -= 1
                
                deleted_text = line[pos:self.cursor_column]
                self.add_undo_action('delete', (self.cursor_line, pos), deleted_text, cursor_before, f"Delete Word")
                self.lines[self.cursor_line] = line[:pos] + line[self.cursor_column:]
                self.cursor_column = pos
            else:
                # Regular backspace
                deleted_text = line[self.cursor_column - 1]
                self.add_undo_action('delete', (self.cursor_line, self.cursor_column - 1), deleted_text, cursor_before)
                self.lines[self.cursor_line] = line[:self.cursor_column - 1] + line[self.cursor_column:]
                self.cursor_column -= 1
        elif self.cursor_line > 0:
            # Join with previous line
            prev_line = self.lines[self.cursor_line - 1]
            curr_line = self.lines.pop(self.cursor_line)
            deleted_text = '\n'
            self.add_undo_action('delete', (self.cursor_line - 1, len(prev_line)), deleted_text, cursor_before, "Join Lines")
            self.cursor_line -= 1
            self.cursor_column = len(prev_line)
            self.lines[self.cursor_line] = prev_line + curr_line

        self.after_text_change()