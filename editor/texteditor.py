# editor/texteditor.py

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, QTimer, QEvent, pyqtSignal

from editor.theme import Theme
from editor.cursor_mixin import CursorMixin
from editor.selection_mixin import SelectionMixin
from editor.clipboard_mixin import ClipboardMixin
from editor.undoredo_mixin import UndoRedoMixin
from editor.painting_mixin import PaintingMixin

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TextEditor(QWidget, CursorMixin, SelectionMixin, ClipboardMixin, UndoRedoMixin, PaintingMixin):
    # Signal to notify MainWindow about modification state changes
    modifiedChanged = pyqtSignal(object)  # Emits the TextEditor instance

    def __init__(self, content='', file_path=None, main_window=None):
        super().__init__()

        # Store reference to main window
        self.main_window = main_window

        # Use the font from Theme
        self.font = Theme.get_default_font()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Enable keyboard focus
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled)
        self.setAttribute(Qt.WidgetAttribute.WA_KeyCompression, False)

        # Initialize text content
        self.lines = content.split('\n') if content else ['']
        self.cursor_line = 0
        self.cursor_column = 0

        self.file_path = file_path
        self._is_modified = False  # Private flag to track unsaved changes

        self.cursor_visible = True
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.blink_cursor)
        self.cursor_timer.start(500)  # Blink every 500ms

        # For selection handling
        self.selection_start = None  # tuple (line, column)
        self.selection_end = None    # tuple (line, column)

    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update()  # Trigger a repaint

    def event(self, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                self.keyPressEvent(event)
                return True
        return super().event(event)

    def keyPressEvent(self, event: QKeyEvent):
        modifiers = event.modifiers()

        # Handle undo/redo shortcuts
        if event.key() == Qt.Key.Key_Z and modifiers & Qt.KeyboardModifier.ControlModifier:
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.redo()
            else:
                self.undo()
            return
        elif event.key() == Qt.Key.Key_Y and modifiers & Qt.KeyboardModifier.ControlModifier:
            self.redo()
            return

        # Delegate to CursorMixin for movement keys
        if event.key() in [Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down]:
            CursorMixin.keyPressEvent(self, event)
            return

        # Record the state before the action
        cursor_before = (self.cursor_line, self.cursor_column)

        if event.key() == Qt.Key.Key_Backspace:
            if self.has_selection():
                text = self.get_selected_text()
                selection = self.selection_range()
                self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
                self.delete_selection()
            elif self.cursor_column > 0:
                # Remove character before cursor
                line = self.lines[self.cursor_line]
                deleted_text = line[self.cursor_column - 1]
                self.add_undo_action('delete', (self.cursor_line, self.cursor_column - 1), deleted_text, cursor_before)
                self.lines[self.cursor_line] = line[:self.cursor_column - 1] + line[self.cursor_column:]
                self.cursor_column -= 1
            elif self.cursor_line > 0:
                # Merge with previous line
                prev_line = self.lines[self.cursor_line - 1]
                curr_line = self.lines.pop(self.cursor_line)
                deleted_text = '\n'
                self.add_undo_action('delete', (self.cursor_line - 1, len(prev_line)), deleted_text, cursor_before)
                self.cursor_line -= 1
                self.cursor_column = len(prev_line)
                self.lines[self.cursor_line] = prev_line + curr_line
            self.set_modified(True)
            self.update()
        elif event.key() == Qt.Key.Key_Delete:
            if self.has_selection():
                text = self.get_selected_text()
                selection = self.selection_range()
                self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
                self.delete_selection()
            else:
                line = self.lines[self.cursor_line]
                if self.cursor_column < len(line):
                    # Remove character at cursor
                    deleted_text = line[self.cursor_column]
                    self.add_undo_action('delete', (self.cursor_line, self.cursor_column), deleted_text, cursor_before)
                    self.lines[self.cursor_line] = line[:self.cursor_column] + line[self.cursor_column + 1:]
                elif self.cursor_line < len(self.lines) - 1:
                    # Merge with next line
                    deleted_text = '\n'
                    self.add_undo_action('delete', (self.cursor_line, len(line)), deleted_text, cursor_before)
                    next_line = self.lines.pop(self.cursor_line + 1)
                    self.lines[self.cursor_line] += next_line
            self.set_modified(True)
            self.update()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.has_selection():
                text = self.get_selected_text()
                selection = self.selection_range()
                self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
                self.delete_selection()
            # Handle Enter key
            line = self.lines[self.cursor_line]
            self.add_undo_action('insert', (self.cursor_line, self.cursor_column), '\n', cursor_before)
            # Split the current line at the cursor position
            new_line = line[self.cursor_column:]
            self.lines[self.cursor_line] = line[:self.cursor_column]
            self.lines.insert(self.cursor_line + 1, new_line)
            self.cursor_line += 1
            self.cursor_column = 0
            self.clear_selection()
            self.set_modified(True)
            self.update()
        elif event.key() == Qt.Key.Key_Tab:
            if self.has_selection():
                text = self.get_selected_text()
                selection = self.selection_range()
                self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
                self.delete_selection()
            # Handle Tab key (insert spaces)
            tab_spaces = '    '  # 4 spaces
            self.add_undo_action('insert', (self.cursor_line, self.cursor_column), tab_spaces, cursor_before)
            line = self.lines[self.cursor_line]
            self.lines[self.cursor_line] = line[:self.cursor_column] + tab_spaces + line[self.cursor_column:]
            self.cursor_column += len(tab_spaces)
            self.set_modified(True)
            self.update()
        elif len(event.text()) > 0 and event.text().isprintable():
            if self.has_selection():
                text = self.get_selected_text()
                selection = self.selection_range()
                self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
                self.delete_selection()
            # Handle character input
            text = event.text()
            if text:
                self.add_undo_action('insert', (self.cursor_line, self.cursor_column), text, cursor_before)
                line = self.lines[self.cursor_line]
                self.lines[self.cursor_line] = line[:self.cursor_column] + text + line[self.cursor_column:]
                self.cursor_column += len(text)
                self.set_modified(True)
                self.update()
        else:
            # Handle other keys
            super().keyPressEvent(event)

    def set_modified(self, value: bool):
        """Setter method for is_modified flag."""
        if self._is_modified != value:
            self._is_modified = value
            logging.debug(f"TextEditor modifiedChanged emitted for instance {id(self)} with value {value}")
            self.modifiedChanged.emit(self)  # Emit signal with self

    @property
    def is_modified(self):
        return self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool):
        self.set_modified(value)

    def focusInEvent(self, event):
        self.cursor_visible = True
        self.cursor_timer.start(500)
        self.update()

    def focusOutEvent(self, event):
        self.cursor_visible = False
        self.cursor_timer.stop()
        self.update()

    def toPlainText(self):
        return '\n'.join(self.lines)
