from PyQt6.QtWidgets import QWidget, QAbstractScrollArea, QApplication
from PyQt6.QtGui import QKeyEvent, QFontMetrics, QPainter, QPalette
from PyQt6.QtCore import Qt, QTimer, QEvent, pyqtSignal, QRect, QSize

from .themes.theme import Theme
from .mixins.cursor import CursorMixin
from .mixins.selection import SelectionMixin
from .mixins.clipboard import ClipboardMixin
from .mixins.undoredo import UndoRedoMixin
from .mixins.painting import PaintingMixin

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setFont(self.editor.font())
        
        # Set background color from theme
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, Theme.EDITOR_LINE_NUMBER_BACKGROUND)
        self.setPalette(palette)

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class TextEditorViewport(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled)
        self.setAttribute(Qt.WidgetAttribute.WA_KeyCompression, False)
        
        # Set background color from theme
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, Theme.EDITOR_BACKGROUND_COLOR)
        self.setPalette(palette)

        # Set viewport stylesheet using theme colors
        self.setStyleSheet(f"""
            background-color: {Theme.EDITOR_BACKGROUND_COLOR.name()};
            color: {Theme.EDITOR_TEXT_COLOR.name()};
            selection-background-color: {Theme.EDITOR_SELECTION_BACKGROUND.name()};
        """)

    def keyPressEvent(self, event):
        self.editor.keyPressEvent(event)

    def mousePressEvent(self, event):
        self.editor.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.editor.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.editor.mouseReleaseEvent(event)

    def focusInEvent(self, event):
        self.editor.focusInEvent(event)

    def focusOutEvent(self, event):
        self.editor.focusOutEvent(event)

    def sizeHint(self):
        return self.editor.sizeHint()

class EditorSyncMixin:
    """
    Mixin to provide standardized text editor state management and safety utilities.
    This should be the first mixin in the inheritance chain for TextEditor.
    """
    def safe_cursor_line(self):
        """Ensure cursor_line is within valid bounds."""
        if not hasattr(self, 'cursor_line'):
            self.cursor_line = 0
        if not hasattr(self, 'lines'):
            self.lines = ['']
        self.cursor_line = max(0, min(self.cursor_line, len(self.lines) - 1))
        return self.cursor_line

    def safe_cursor_column(self):
        """Ensure cursor_column is within valid bounds for the current line."""
        if not hasattr(self, 'cursor_column'):
            self.cursor_column = 0
        line = self.lines[self.safe_cursor_line()]
        self.cursor_column = max(0, min(self.cursor_column, len(line)))
        return self.cursor_column

    def ensure_valid_state(self):
        """Ensure all editor state is valid and consistent."""
        # Ensure we have at least one line
        if not self.lines:
            self.lines = ['']
        
        # Initialize highlighted_lines if it doesn't exist
        if not hasattr(self, 'highlighted_lines'):
            self.highlighted_lines = [{}]
            
        # Synchronize highlighted_lines with actual lines
        # This is critical for avoiding index out of range errors
        while len(self.highlighted_lines) > len(self.lines):
            self.highlighted_lines.pop()
        while len(self.highlighted_lines) < len(self.lines):
            self.highlighted_lines.append({})
            
        # Ensure cursor position is valid
        self.safe_cursor_line()
        self.safe_cursor_column()
        
        # Clear invalid selections
        if hasattr(self, 'has_selection') and self.has_selection():
            if not self.is_valid_selection():
                self.clear_selection()

    def is_valid_selection(self):
        """Check if current selection range is valid."""
        if not hasattr(self, 'selection_start') or not hasattr(self, 'selection_end'):
            return False
        if self.selection_start is None or self.selection_end is None:
            return False
            
        start_line, start_col = self.selection_start
        end_line, end_col = self.selection_end
        
        # Check line bounds
        if not (0 <= start_line < len(self.lines) and 0 <= end_line < len(self.lines)):
            return False
            
        # Check column bounds
        if not (0 <= start_col <= len(self.lines[start_line])):
            return False
        if not (0 <= end_col <= len(self.lines[end_line])):
            return False
            
        return True

    def synchronize_editor_state(self):
        """
        Synchronize all editor state after a change.
        This should be called after any operation that modifies the text or cursor position.
        """
        try:
            # Ensure basic state is valid
            self.ensure_valid_state()
            
            # Update syntax highlighting if enabled
            if hasattr(self, 'highlighter') and self.highlighter:
                try:
                    # Create a new highlighted_lines list with the correct size
                    self.highlighted_lines = self.highlighter.highlight(self.lines)
                    # Ensure the highlighted_lines length matches lines length
                    while len(self.highlighted_lines) < len(self.lines):
                        self.highlighted_lines.append({})
                except Exception as e:
                    logging.error(f"Error updating syntax highlighting: {e}")
                    # Reset highlighting on error
                    self.highlighted_lines = [{} for _ in self.lines]
            
            # Update scroll bars and geometry
            self.update_scrollbars()
            self.updateGeometry()
            
            # Update UI elements
            if hasattr(self, 'line_number_area'):
                self.update_line_number_area_width(0)
                self.line_number_area.update()
                
            # Ensure cursor is visible
            self.ensure_cursor_visible()
            
            # Mark as modified
            self.set_modified(True)
            
            # Final viewport update
            self.update()
            
        except Exception as e:
            logging.error(f"Error synchronizing editor state: {e}")
            # Attempt to recover to a safe state
            self.lines = ['']
            self.cursor_line = 0
            self.cursor_column = 0
            self.highlighted_lines = [{}]
            self.clear_selection()
            self.update()

    def after_text_change(self):
        """
        Standardized method to be called after any text modification.
        Replaces individual update calls scattered throughout the code.
        """
        self.synchronize_editor_state()

class TextEditor(EditorSyncMixin, CursorMixin, SelectionMixin, ClipboardMixin, UndoRedoMixin, PaintingMixin, QAbstractScrollArea):
    modifiedChanged = pyqtSignal(object)

    def __init__(self, content='', file_path=None, main_window=None):
        super().__init__()
        
        self.main_window = main_window
        
        # Set editor font
        self.editor_font = Theme.get_default_font()
        self.setFont(self.editor_font)
        
        # Configure editor colors using theme
        self.setStyleSheet(f"""
            QAbstractScrollArea {{
                background-color: {Theme.EDITOR_BACKGROUND_COLOR.name()};
                color: {Theme.EDITOR_TEXT_COLOR.name()};
                selection-background-color: {Theme.EDITOR_SELECTION_BACKGROUND.name()};
            }}
            QScrollBar:vertical {{
                background: {Theme.EDITOR_SCROLLBAR_BACKGROUND.name()};
                width: {Theme.EDITOR_SCROLLBAR_WIDTH}px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.EDITOR_SCROLLBAR_HANDLE.name()};
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.EDITOR_SCROLLBAR_HANDLE_HOVER.name()};
            }}
            QScrollBar:horizontal {{
                background: {Theme.EDITOR_SCROLLBAR_BACKGROUND.name()};
                height: {Theme.EDITOR_SCROLLBAR_WIDTH}px;
            }}
            QScrollBar::handle:horizontal {{
                background: {Theme.EDITOR_SCROLLBAR_HANDLE.name()};
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Theme.EDITOR_SCROLLBAR_HANDLE_HOVER.name()};
            }}
        """)
        
        # Configure margins and spacing
        self.setViewportMargins(
            Theme.EDITOR_MARGIN_LEFT,
            Theme.EDITOR_MARGIN_TOP,
            Theme.EDITOR_MARGIN_RIGHT,
            Theme.EDITOR_MARGIN_BOTTOM
        )

        # Initialize viewport with theme colors
        self.viewport_widget = TextEditorViewport(self)
        self.setViewport(self.viewport_widget)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled)
        self.setAttribute(Qt.WidgetAttribute.WA_KeyCompression, False)

        self.lines = content.split('\n') if content else ['']
        self.cursor_line = 0
        self.cursor_column = 0

        # Initialize line number area with theme colors
        self.line_number_area = LineNumberArea(self)
        self.update_line_number_area_width(0)
        self.verticalScrollBar().valueChanged.connect(self.line_number_area.update)

        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

        self.file_path = file_path
        self._is_modified = False

        self.highlighter = None
        self.highlighted_lines = [{} for _ in self.lines]

        # Cursor blinking setup
        self.cursor_visible = True
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.blink_cursor)
        self.cursor_timer.start(500)

        # Selection setup
        self.selection_start = None
        self.selection_end = None

        # Scrollbar setup
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.update_scrollbars()

    def set_highlighter(self, highlighter):
        self.highlighter = highlighter
        self.update_highlighting()

    def update_highlighting(self):
        if self.highlighter:
            self.highlighted_lines = self.highlighter.highlight(self.lines)
        else:
            self.highlighted_lines = [{} for _ in self.lines]
        self.update()

    def ensure_cursor_visible(self):
        fm = QFontMetrics(self.font())
        line_height = fm.height()
        char_width = fm.horizontalAdvance(' ')

        cursor_x = fm.horizontalAdvance(self.lines[self.cursor_line][:self.cursor_column])
        cursor_y = self.cursor_line * line_height

        viewport_width = self.viewport().width()
        viewport_height = self.viewport().height()

        x_offset = self.horizontalScrollBar().value()
        y_offset = self.verticalScrollBar().value()

        horizontal_padding = Theme.scaled_size(20)
        vertical_padding = Theme.scaled_size(20)

        if cursor_x < x_offset:
            self.horizontalScrollBar().setValue(cursor_x - horizontal_padding)
        elif cursor_x > x_offset + viewport_width - char_width:
            self.horizontalScrollBar().setValue(cursor_x - viewport_width + char_width + horizontal_padding)

        if cursor_y < y_offset:
            self.verticalScrollBar().setValue(cursor_y - vertical_padding)
        elif cursor_y > y_offset + viewport_height - line_height:
            self.verticalScrollBar().setValue(cursor_y - viewport_height + line_height + vertical_padding)

    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update()

    def event(self, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Tab:
            self.keyPressEvent(event)
            return True
        return super().event(event)

    def line_number_area_width(self):
        digits = len(str(max(1, len(self.lines))))
        fm = QFontMetrics(self.font())
        max_width = fm.horizontalAdvance('9' * digits) + Theme.LINE_NUMBER_PADDING
        return max_width

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """Paint the line numbers."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Theme.EDITOR_LINE_NUMBER_BACKGROUND)

        fm = QFontMetrics(self.font())
        line_height = fm.height()
        block_top = self.verticalScrollBar().value()

        viewport_offset = block_top
        paint_rect = event.rect()

        first_visible_line = max(0, int(viewport_offset / line_height))
        last_visible_line = min(
            len(self.lines) - 1,
            int((viewport_offset + self.viewport().height()) / line_height) + 1
        )

        painter.setPen(Theme.EDITOR_LINE_NUMBER_COLOR)
        painter.setFont(self.font())
        number_width = self.line_number_area.width()

        for line_number in range(first_visible_line, last_visible_line + 1):

            y_pos = (line_number * line_height) - viewport_offset

            if y_pos >= paint_rect.top() - line_height and y_pos <= paint_rect.bottom():
                number = str(line_number + 1)
                painter.drawText(
                    0, 
                    y_pos,
                    number_width,
                    line_height,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    number
                )

    def get_line_indentation(self, line):
        """Get the indentation level (number of leading spaces) of a line."""
        indent_length = 0
        for char in line:
            if char == ' ':
                indent_length += 1
            elif char == '\t':
                indent_length += 4  # Convert tabs to 4 spaces
            else:
                break
        return indent_length

    def should_increase_indent(self, line):
        """
        Determine if the next line should have increased indentation.
        This is language-specific, but here's a simple implementation for Python-like languages.
        """
        # Strip comments first
        code_line = line.split('#')[0].rstrip()
        
        # Look for lines ending in colon (Python blocks)
        if code_line.rstrip().endswith(':'):
            return True
            
        # Additional language-specific rules can be added here
        return False

    def update_scrollbars(self):
        fm = QFontMetrics(self.font())
        line_height = fm.height()
        content_width = max(fm.horizontalAdvance(line) for line in self.lines) + Theme.CONTENT_WIDTH_PADDING
        content_height = line_height * len(self.lines) + Theme.CONTENT_HEIGHT_PADDING

        self.verticalScrollBar().setRange(0, max(0, content_height - self.viewport().height()))
        self.verticalScrollBar().setPageStep(int(self.viewport().height() * 0.1))
        self.verticalScrollBar().setSingleStep(int(line_height))

        self.horizontalScrollBar().setRange(0, max(0, content_width - self.viewport().width()))
        self.horizontalScrollBar().setPageStep(int(self.viewport().width() * 0.2))
        self.horizontalScrollBar().setSingleStep(int(fm.horizontalAdvance(' ')))

        self.line_number_area.update()

    def keyPressEvent(self, event: QKeyEvent):
        modifiers = event.modifiers()
        key = event.key()

        cursor_before = (self.cursor_line, self.cursor_column)

        if key == Qt.Key.Key_Z and modifiers & Qt.KeyboardModifier.ControlModifier:
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.redo()
            else:
                self.undo()
            return
        elif key == Qt.Key.Key_Y and modifiers & Qt.KeyboardModifier.ControlModifier:
            self.redo()
            return
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            self.handle_cursor_movement(key, modifiers)
            return
        elif key == Qt.Key.Key_Backspace:
            self.handle_backspace(cursor_before)
        elif key == Qt.Key.Key_Delete:
            self.handle_delete(cursor_before)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.handle_enter(cursor_before)
        elif key == Qt.Key.Key_Tab:
            self.handle_tab(cursor_before)
        elif len(event.text()) > 0 and event.text().isprintable():
            self.handle_character_input(event.text(), cursor_before)
        else:
            super().keyPressEvent(event)

    def handle_cursor_movement(self, key, modifiers):
        if key == Qt.Key.Key_Left:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.move_cursor_to_previous_word()
            else:
                self.move_cursor_left()
        elif key == Qt.Key.Key_Right:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.move_cursor_to_next_word()
            else:
                self.move_cursor_right()
        elif key == Qt.Key.Key_Up:
            self.move_cursor_up()
        elif key == Qt.Key.Key_Down:
            self.move_cursor_down()
        self.clear_selection()
        self.update()

    def is_identifier_char(self, char):
        """Check if a character can be part of an identifier."""
        return char.isalnum() or char == '_'

    def is_operator_char(self, char):
        """Check if a character is an operator symbol."""
        operators = set('+-*/%=<>!&|^~@')
        return char in operators

    def is_delimiter(self, char):
        """Check if a character is a delimiter."""
        delimiters = set('()[]{},;.')
        return char in delimiters

    def get_token_boundaries(self, line, column):
        """
        Get the start and end positions of the token at the given column in the line.
        Handles special cases like:
        - Consecutive whitespace as a single token
        - Trailing whitespace as part of the previous word token
        - Leading whitespace as its own token
        - Regular tokens (identifiers, strings, operators, etc.)
        
        Args:
            line (str): The line of text
            column (int): Current cursor position
            
        Returns:
            tuple: (start_col, end_col)
        """
        if column >= len(line):
            return column, column

        # Handle start of line
        if column == 0:
            return 0, self.find_token_end(line, 0)

        current_char = line[column]
        
        # Special case: if we're at whitespace after a word, look backwards
        # to see if this is trailing whitespace after a word
        if current_char.isspace():
            # Look backwards to find start of whitespace
            start = column
            while start > 0 and line[start - 1].isspace():
                start -= 1
                
            # If there's a word before this whitespace, include it
            if start > 0 and self.is_identifier_char(line[start - 1]):
                # Find start of the word
                word_start = start - 1
                while word_start > 0 and self.is_identifier_char(line[word_start - 1]):
                    word_start -= 1
                    
                # Find end of whitespace
                end = column
                while end < len(line) and line[end].isspace():
                    end += 1
                    
                return word_start, end
            else:
                # Just handle the whitespace itself
                end = column
                while end < len(line) and line[end].isspace():
                    end += 1
                return start, end

        # If we're on an identifier character
        if self.is_identifier_char(current_char):
            # Find start of word
            start = column
            while start > 0 and self.is_identifier_char(line[start - 1]):
                start -= 1
                
            # Find end of word and include any trailing whitespace
            end = column
            while end < len(line) and self.is_identifier_char(line[end]):
                end += 1
                
            # Include trailing whitespace
            while end < len(line) and line[end].isspace():
                end += 1
                
            return start, end

        # Handle operators
        elif self.is_operator_char(current_char):
            start = column
            while start > 0 and self.is_operator_char(line[start - 1]):
                start -= 1
                
            end = column + 1
            while end < len(line) and self.is_operator_char(line[end]):
                end += 1
                
            # Include trailing whitespace
            while end < len(line) and line[end].isspace():
                end += 1
                
            return start, end

        # Handle delimiters
        elif self.is_delimiter(current_char):
            end = column + 1
            while end < len(line) and line[end].isspace():
                end += 1
            return column, end

        # Handle string literals
        elif current_char in ('"', "'"):
            quote_char = current_char
            end = column + 1
            while end < len(line):
                if line[end] == quote_char and line[end - 1] != '\\':
                    end += 1
                    break
                end += 1
                
            # Include trailing whitespace
            while end < len(line) and line[end].isspace():
                end += 1
                
            return column, end

        # Default case: treat as single character plus trailing whitespace
        end = column + 1
        while end < len(line) and line[end].isspace():
            end += 1
        return column, end

    def find_token_end(self, line, start_pos):
        """
        Find the end of the next token starting from start_pos.
        Now includes trailing whitespace with word tokens.
        """
        pos = start_pos
        
        # Handle leading whitespace as a single token
        if pos < len(line) and line[pos].isspace():
            while pos < len(line) and line[pos].isspace():
                pos += 1
            return pos
        
        # Handle word tokens and their trailing whitespace
        if pos < len(line) and self.is_identifier_char(line[pos]):
            # Skip the word
            while pos < len(line) and self.is_identifier_char(line[pos]):
                pos += 1
            # Include trailing whitespace
            while pos < len(line) and line[pos].isspace():
                pos += 1
            return pos
            
        # Handle other tokens with trailing whitespace
        while pos < len(line) and not line[pos].isspace():
            if line[pos] in ('"', "'"):
                quote_char = line[pos]
                pos += 1
                while pos < len(line):
                    if line[pos] == quote_char and line[pos - 1] != '\\':
                        pos += 1
                        break
                    pos += 1
            else:
                pos += 1
                
        # Include trailing whitespace for any token
        while pos < len(line) and line[pos].isspace():
            pos += 1
                
        return pos

    def delete_next_token(self, cursor_before):
        """Delete the token after the cursor."""
        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before, "Delete Selection")
            self.delete_selection()
            return

        line = self.lines[self.cursor_line]
        if self.cursor_column >= len(line):
            if self.cursor_line < len(self.lines) - 1:
                # At end of line - delete newline and combine with next line
                deleted_text = '\n'
                self.add_undo_action('delete', (self.cursor_line, len(line)), deleted_text, cursor_before, "Delete Line Break")
                next_line = self.lines.pop(self.cursor_line + 1)
                self.lines[self.cursor_line] += next_line
        else:
            # Find token boundaries
            _, token_end = self.get_token_boundaries(line, self.cursor_column)
            
            # Delete the token
            deleted_text = line[self.cursor_column:token_end]
            description = f"Delete Token: '{deleted_text}'"
            self.add_undo_action('delete', (self.cursor_line, self.cursor_column), deleted_text, cursor_before, description)
            self.lines[self.cursor_line] = line[:self.cursor_column] + line[token_end:]

        self.after_text_change()

    def delete_previous_token(self, cursor_before):
        """Delete the token before the cursor."""
        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before, "Delete Selection")
            self.delete_selection()
            return

        line = self.lines[self.cursor_line]
        if self.cursor_column == 0:
            if self.cursor_line > 0:
                # At start of line - delete newline and combine with previous line
                prev_line = self.lines[self.cursor_line - 1]
                deleted_text = '\n'
                self.add_undo_action('delete', (self.cursor_line - 1, len(prev_line)), deleted_text, cursor_before, "Delete Line Break")
                self.cursor_line -= 1
                self.cursor_column = len(prev_line)
                self.lines[self.cursor_line] = prev_line + line
                self.lines.pop(self.cursor_line + 1)
        else:
            # Find token boundaries
            token_start, _ = self.get_token_boundaries(line, self.cursor_column - 1)
            
            # Delete the token
            deleted_text = line[token_start:self.cursor_column]
            description = f"Delete Token: '{deleted_text}'"
            self.add_undo_action('delete', (self.cursor_line, token_start), deleted_text, cursor_before, description)
            self.lines[self.cursor_line] = line[:token_start] + line[self.cursor_column:]
            self.cursor_column = token_start

        self.after_text_change()

    def handle_delete(self, cursor_before):
        """Enhanced delete handling with Ctrl+Delete support for tokens."""
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            self.delete_next_token(cursor_before)
        else:
            if self.has_selection():
                text = self.get_selected_text()
                selection = self.selection_range()
                self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before, "Delete Selection")
                self.delete_selection()
            else:
                line = self.lines[self.cursor_line]
                if self.cursor_column < len(line):
                    deleted_text = line[self.cursor_column]
                    self.add_undo_action('delete', (self.cursor_line, self.cursor_column), deleted_text, cursor_before, "Delete Character")
                    self.lines[self.cursor_line] = line[:self.cursor_column] + line[self.cursor_column + 1:]
                elif self.cursor_line < len(self.lines) - 1:
                    deleted_text = '\n'
                    self.add_undo_action('delete', (self.cursor_line, len(line)), deleted_text, cursor_before, "Join Lines")
                    next_line = self.lines.pop(self.cursor_line + 1)
                    self.lines[self.cursor_line] += next_line
            self.after_text_change()

    def handle_backspace(self, cursor_before):
        """Enhanced backspace handling with Ctrl+Backspace support for tokens."""
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            self.delete_previous_token(cursor_before)
        else:
            if self.has_selection():
                text = self.get_selected_text()
                selection = self.selection_range()
                self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before, "Delete Selection")
                self.delete_selection()
            else:
                line = self.lines[self.cursor_line]
                if self.cursor_column > 0:
                    # Check if we're at the end of a tab (multiple spaces)
                    if self.cursor_column >= 4:
                        preceding = line[self.cursor_column - 4:self.cursor_column]
                        if preceding == '    ':  # If previous 4 characters are spaces
                            deleted_text = preceding
                            self.add_undo_action('delete', (self.cursor_line, self.cursor_column - 4), deleted_text, cursor_before, "Delete Tab")
                            self.lines[self.cursor_line] = line[:self.cursor_column - 4] + line[self.cursor_column:]
                            self.cursor_column -= 4
                        else:  # Normal single character deletion
                            deleted_text = line[self.cursor_column - 1]
                            self.add_undo_action('delete', (self.cursor_line, self.cursor_column - 1), deleted_text, cursor_before, "Delete Character")
                            self.lines[self.cursor_line] = line[:self.cursor_column - 1] + line[self.cursor_column:]
                            self.cursor_column -= 1
                    else:  # Normal single character deletion
                        deleted_text = line[self.cursor_column - 1]
                        self.add_undo_action('delete', (self.cursor_line, self.cursor_column - 1), deleted_text, cursor_before, "Delete Character")
                        self.lines[self.cursor_line] = line[:self.cursor_column - 1] + line[self.cursor_column:]
                        self.cursor_column -= 1
                elif self.cursor_line > 0:  # Join with previous line
                    prev_line = self.lines[self.cursor_line - 1]
                    curr_line = self.lines.pop(self.cursor_line)
                    deleted_text = '\n'
                    self.add_undo_action('delete', (self.cursor_line - 1, len(prev_line)), deleted_text, cursor_before, "Join Lines")
                    self.cursor_line -= 1
                    self.cursor_column = len(prev_line)
                    self.lines[self.cursor_line] = prev_line + curr_line

            self.after_text_change()

    def handle_enter(self, cursor_before):
        """Handle the enter key press with auto-indentation."""
        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
            self.delete_selection()

        current_line = self.lines[self.cursor_line]
        current_indent = self.get_line_indentation(current_line)
        
        # Split the current line at cursor position
        line_before_cursor = current_line[:self.cursor_column]
        line_after_cursor = current_line[self.cursor_column:]
        
        # Calculate the new indentation level
        new_indent = current_indent
        if self.should_increase_indent(line_before_cursor):
            new_indent += 4  # Increase indent by 4 spaces
        elif line_before_cursor.strip() == '':
            # If the line is empty (only whitespace), maintain the indentation
            new_indent = current_indent
        
        # Create the indentation string
        indent_str = ' ' * new_indent
        
        # Add the enter action to undo stack
        full_text = '\n' + indent_str
        self.add_undo_action('insert', (self.cursor_line, self.cursor_column), full_text, cursor_before)
        
        # Update the lines
        self.lines[self.cursor_line] = line_before_cursor
        self.lines.insert(self.cursor_line + 1, indent_str + line_after_cursor)
        
        # Update cursor position
        self.cursor_line += 1
        self.cursor_column = new_indent
        
        # Clear selection
        self.clear_selection()
        
        # Update the editor state
        self.after_text_change()

    def handle_tab(self, cursor_before):
        """Handle tab key press with improved undo/redo support."""
        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before, "Delete Selection")
            self.delete_selection()

        tab_spaces = '    '
        self.add_undo_action('insert', (self.cursor_line, self.cursor_column), tab_spaces, cursor_before, "Insert Tab")
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[:self.cursor_column] + tab_spaces + line[self.cursor_column:]
        self.cursor_column += len(tab_spaces)
        self.after_text_change()

    def handle_character_input(self, text, cursor_before):
        """Handle character input with improved undo/redo descriptions."""
        if self.has_selection():
            sel_text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), sel_text, cursor_before, "Replace Selection")
            self.delete_selection()
        
        self.add_undo_action('insert', (self.cursor_line, self.cursor_column), text, cursor_before, f"Insert '{text}'")
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[:self.cursor_column] + text + line[self.cursor_column:]
        self.cursor_column += len(text)
        self.after_text_change()

    def after_text_change(self):
        """
        Standardized method to be called after any text modification.
        """
        self.synchronize_editor_state()

    def set_modified(self, value: bool):
        if self._is_modified != value:
            self._is_modified = value
            logging.debug(f"TextEditor modifiedChanged emitted for instance {id(self)} with value {value}")
            self.modifiedChanged.emit(self)

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
