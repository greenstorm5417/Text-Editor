from PyQt6.QtWidgets import QWidget, QAbstractScrollArea
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

class TextEditor(CursorMixin, SelectionMixin, ClipboardMixin, UndoRedoMixin, PaintingMixin, QAbstractScrollArea):
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

    def handle_backspace(self, cursor_before):
        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
            self.delete_selection()
        elif self.cursor_column > 0:
            line = self.lines[self.cursor_line]
            deleted_text = line[self.cursor_column - 1]
            self.add_undo_action('delete', (self.cursor_line, self.cursor_column - 1), deleted_text, cursor_before)
            self.lines[self.cursor_line] = line[:self.cursor_column - 1] + line[self.cursor_column:]
            self.cursor_column -= 1
        elif self.cursor_line > 0:
            prev_line = self.lines[self.cursor_line - 1]
            curr_line = self.lines.pop(self.cursor_line)
            deleted_text = '\n'
            self.add_undo_action('delete', (self.cursor_line - 1, len(prev_line)), deleted_text, cursor_before)
            self.cursor_line -= 1
            self.cursor_column = len(prev_line)
            self.lines[self.cursor_line] = prev_line + curr_line
        self.after_text_change()

    def handle_delete(self, cursor_before):
        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
            self.delete_selection()
        else:
            line = self.lines[self.cursor_line]
            if self.cursor_column < len(line):
                deleted_text = line[self.cursor_column]
                self.add_undo_action('delete', (self.cursor_line, self.cursor_column), deleted_text, cursor_before)
                self.lines[self.cursor_line] = line[:self.cursor_column] + line[self.cursor_column + 1:]
            elif self.cursor_line < len(self.lines) - 1:
                deleted_text = '\n'
                self.add_undo_action('delete', (self.cursor_line, len(line)), deleted_text, cursor_before)
                next_line = self.lines.pop(self.cursor_line + 1)
                self.lines[self.cursor_line] += next_line
        self.after_text_change()

    def handle_enter(self, cursor_before):
        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
            self.delete_selection()
        line = self.lines[self.cursor_line]
        self.add_undo_action('insert', (self.cursor_line, self.cursor_column), '\n', cursor_before)
        new_line = line[self.cursor_column:]
        self.lines[self.cursor_line] = line[:self.cursor_column]
        self.lines.insert(self.cursor_line + 1, new_line)
        self.cursor_line += 1
        self.cursor_column = 0
        self.clear_selection()
        self.after_text_change()
        self.update_scrollbars()

    def handle_tab(self, cursor_before):
        if self.has_selection():
            text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), text, cursor_before)
            self.delete_selection()
        tab_spaces = '    '
        self.add_undo_action('insert', (self.cursor_line, self.cursor_column), tab_spaces, cursor_before)
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[:self.cursor_column] + tab_spaces + line[self.cursor_column:]
        self.cursor_column += len(tab_spaces)
        self.after_text_change()

    def handle_character_input(self, text, cursor_before):
        if self.has_selection():
            sel_text = self.get_selected_text()
            selection = self.selection_range()
            self.add_undo_action('delete', (selection[0], selection[1]), sel_text, cursor_before)
            self.delete_selection()
        self.add_undo_action('insert', (self.cursor_line, self.cursor_column), text, cursor_before)
        line = self.lines[self.cursor_line]
        self.lines[self.cursor_line] = line[:self.cursor_column] + text + line[self.cursor_column:]
        self.cursor_column += len(text)
        self.after_text_change()

    def after_text_change(self):
        self.set_modified(True)
        self.updateGeometry()
        self.update_highlighting()
        self.update_line_number_area_width(0)
        self.line_number_area.update()
        self.update()

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
