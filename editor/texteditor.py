from PyQt6.QtWidgets import QWidget, QApplication, QSizePolicy, QAbstractScrollArea
from PyQt6.QtGui import QKeyEvent, QFontMetrics, QPainter
from PyQt6.QtCore import Qt, QTimer, QEvent, pyqtSignal, QRect, QSize
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerJavaScript

from editor.theme import Theme
from editor.mixins.cursor_mixin import CursorMixin
from editor.mixins.selection_mixin import SelectionMixin
from editor.mixins.clipboard_mixin import ClipboardMixin
from editor.mixins.undoredo_mixin import UndoRedoMixin
from editor.mixins.painting_mixin import PaintingMixin
from editor.syntax_highlighter import PygmentsSyntaxHighlighter

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

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

    def paintEvent(self, event):
        # Move the painting code here
        logging.debug("TextEditorViewport.paintEvent called")
        painter = QPainter(self)
        painter.setFont(self.editor.font())
        fm = painter.fontMetrics()

        # Get the scroll positions
        x_offset = self.editor.horizontalScrollBar().value()
        y_offset = self.editor.verticalScrollBar().value()

        line_height = fm.height()
        y_text_offset = fm.ascent()

        # Use the event's rect to get the clipping rectangle
        visible_rect = event.rect()

        # Calculate first and last visible lines
        first_visible_line = max(0, int((y_offset + visible_rect.top()) / line_height))
        last_visible_line = min(len(self.editor.lines) - 1, int((y_offset + visible_rect.bottom()) / line_height))

        # Draw selection background if there is a selection
        selection = self.editor.selection_range()
        if selection:
            start_line, start_col, end_line, end_col = selection
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(Theme.SELECTION_COLOR)
            for i in range(start_line, end_line + 1):
                if i < first_visible_line or i > last_visible_line:
                    continue  # Skip non-visible lines
                line = self.editor.lines[i]
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
        for i in range(first_visible_line, last_visible_line + 1):
            line = self.editor.lines[i]
            line_y = y_text_offset + (i * line_height) - y_offset
            painter.drawText(-x_offset, line_y, line)

        # Calculate cursor position
        if self.hasFocus() and self.editor.cursor_visible:
            cursor_x = fm.horizontalAdvance(self.editor.lines[self.editor.cursor_line][:self.editor.cursor_column]) - x_offset
            cursor_y = (self.editor.cursor_line * line_height) - y_offset

            # Draw the cursor using color from Theme
            cursor_rect = QRect(cursor_x, cursor_y, 2, line_height)
            painter.fillRect(cursor_rect, Theme.CURSOR_COLOR)

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


class TextEditor(CursorMixin, SelectionMixin, ClipboardMixin, UndoRedoMixin, PaintingMixin, QAbstractScrollArea):
    modifiedChanged = pyqtSignal(object) 

    def __init__(self, content='', file_path=None, main_window=None):
        super().__init__()

        # Store reference to main window
        self.main_window = main_window

        # Use the font from Theme
        self.editor_font = Theme.get_default_font()
        self.setFont(self.editor_font)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Enable keyboard focus
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled)
        self.setAttribute(Qt.WidgetAttribute.WA_KeyCompression, False)

        # Initialize text content
        self.lines = content.split('\n') if content else ['']
        self.cursor_line = 0
        self.cursor_column = 0

                # Initialize LineNumberArea
        # Update these specific lines in the __init__ method
        self.line_number_area = LineNumberArea(self)
        self.update_line_number_area_width(0)

        # Adjust viewport margins
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

        self.verticalScrollBar().valueChanged.connect(self.line_number_area.update)


        self.file_path = file_path
        self._is_modified = False  # Private flag to track unsaved changes

        self.highlighter = None  # Add this line
        self.highlighted_lines = [{} for _ in self.lines]

        self.cursor_visible = True
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.blink_cursor)
        self.cursor_timer.start(500)  # Blink every 500ms

        # For selection handling
        self.selection_start = None  # tuple (line, column)
        self.selection_end = None    # tuple (line, column)

        # Remove size policy as QAbstractScrollArea handles it
        # self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Initialize scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

                # Initialize custom viewport
        self.viewport_widget = TextEditorViewport(self)
        self.setViewport(self.viewport_widget)
        
        self.update_scrollbars()

    def set_highlighter(self, highlighter):
        self.highlighter = highlighter
        self.update_highlighting()

    def update_highlighting(self):
        if self.highlighter:
            self.highlighted_lines = self.highlighter.highlight(self.lines)
        else:
            self.highlighted_lines = [[] for _ in self.lines]
        self.update()        

    def ensure_cursor_visible(self):
        """Adjust the scrollbars to ensure the cursor is visible."""
        fm = QFontMetrics(self.font())
        line_height = fm.height()
        char_width = fm.horizontalAdvance(' ')  # Average character width

        # Calculate cursor position in pixels
        cursor_x = fm.horizontalAdvance(self.lines[self.cursor_line][:self.cursor_column])
        cursor_y = self.cursor_line * line_height

        # Get the viewport size
        viewport_width = self.viewport().width()
        viewport_height = self.viewport().height()

        # Get current scroll positions
        x_offset = self.horizontalScrollBar().value()
        y_offset = self.verticalScrollBar().value()

        # Define some padding
        horizontal_padding = Theme.scaled_size(20)
        vertical_padding = Theme.scaled_size(20)

        # Adjust horizontal scrollbar
        if cursor_x < x_offset:
            # Move scrollbar to the left to bring cursor into view
            self.horizontalScrollBar().setValue(cursor_x - horizontal_padding)
        elif cursor_x > x_offset + viewport_width - char_width:
            # Move scrollbar to the right
            self.horizontalScrollBar().setValue(cursor_x - viewport_width + char_width + horizontal_padding)

        # Adjust vertical scrollbar
        if cursor_y < y_offset:
            # Scroll up to bring cursor into view
            self.verticalScrollBar().setValue(cursor_y - vertical_padding)
        elif cursor_y > y_offset + viewport_height - line_height:
            # Scroll down
            self.verticalScrollBar().setValue(cursor_y - viewport_height + line_height + vertical_padding)


    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update()  # Trigger a repaint

    def event(self, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                self.keyPressEvent(event)
                return True
        return super().event(event)
    
    def line_number_area_width(self):
        """Calculate the width needed for the line numbers."""
        max_width = 0
        digits = len(str(max(1, len(self.lines))))
        fm = QFontMetrics(self.font())
        
        # Calculate width based on widest possible number plus padding
        max_width = fm.horizontalAdvance('9' * digits) + Theme.scaled_size(20)
        
        return max_width

    def update_line_number_area_width(self, _):
        """Update the viewport margins based on the line number area width."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def resizeEvent(self, event):
        """Handle the resize event to adjust the line number area."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """Paint the line numbers."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Theme.BACKGROUND_COLOR)

        # Get metrics for text positioning
        fm = QFontMetrics(self.font())
        line_height = fm.height()
        block_top = self.verticalScrollBar().value()
        
        # Get visible region
        viewport_offset = block_top
        paint_rect = event.rect()
        
        # Calculate first and last visible lines
        first_visible_line = max(0, int(viewport_offset / line_height))
        last_visible_line = min(
            len(self.lines) - 1,
            int((viewport_offset + self.viewport().height()) / line_height) + 1
        )

        # Set up painter for numbers
        painter.setPen(Theme.LINE_NUMBER_COLOR)
        painter.setFont(self.font())

        # Width of the line number area
        number_width = self.line_number_area.width()

        for line_number in range(first_visible_line, last_visible_line + 1):
            # Calculate the y position for this line number
            y_pos = (line_number * line_height) - viewport_offset
            
            # Only draw if the line number is visible
            if y_pos >= paint_rect.top() - line_height and y_pos <= paint_rect.bottom():
                number = str(line_number + 1)
                painter.drawText(
                    0,  # x position
                    y_pos,  # y position
                    number_width,  # width
                    line_height,  # height
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    number
                )



    def update_scrollbars(self):
        """Update the scrollbars based on the content size."""
        fm = QFontMetrics(self.font())
        line_height = fm.height()
        content_width = max(fm.horizontalAdvance(line) for line in self.lines) + Theme.scaled_size(20)
        content_height = line_height * len(self.lines) + Theme.scaled_size(20)

        self.verticalScrollBar().setRange(0, max(0, content_height - self.viewport().height()))
        self.verticalScrollBar().setPageStep(int(self.viewport().height() * 0.1))
        self.verticalScrollBar().setSingleStep(int(line_height * 1))

        self.horizontalScrollBar().setRange(0, max(0, content_width - self.viewport().width()))
        self.horizontalScrollBar().setPageStep(int(self.viewport().width() * 0.2))
        self.horizontalScrollBar().setSingleStep(int(fm.horizontalAdvance(' ') * 1))

        # Update the line number area when scrollbars change
        self.line_number_area.update()



    def keyPressEvent(self, event: QKeyEvent):
        modifiers = event.modifiers()
        key = event.key()

        # Handle undo/redo shortcuts
        if key == Qt.Key.Key_Z and modifiers & Qt.KeyboardModifier.ControlModifier:
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.redo()
            else:
                self.undo()
            return
        elif key == Qt.Key.Key_Y and modifiers & Qt.KeyboardModifier.ControlModifier:
            self.redo()
            return

        # Handle cursor movement keys
        if key == Qt.Key.Key_Left:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.move_cursor_to_previous_word()
            else:
                self.move_cursor_left()
            self.clear_selection()
            self.update()
            return
        elif key == Qt.Key.Key_Right:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.move_cursor_to_next_word()
            else:
                self.move_cursor_right()
            self.clear_selection()
            self.update()
            return
        elif key == Qt.Key.Key_Up:
            self.move_cursor_up()
            self.clear_selection()
            self.update()
            return
        elif key == Qt.Key.Key_Down:
            self.move_cursor_down()
            self.clear_selection()
            self.update()
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
            self.updateGeometry()  # Notify layout system
            self.update_highlighting() 
            self.update_line_number_area_width(0)
            self.line_number_area.update()
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
            self.updateGeometry()  # Notify layout system
            self.update_highlighting() 
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
            self.updateGeometry()  # Notify layout system
            self.update_scrollbars()
            self.update_highlighting() 
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
            self.updateGeometry()  # Notify layout system
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
                self.updateGeometry()  # Notify layout system
                self.update_highlighting() 
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
