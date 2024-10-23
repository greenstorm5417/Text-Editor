from editor.texteditor import TextEditor

class EditActionsMixin:
    # ----- Edit Menu Actions -----
    def undo_edit(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            text_editor = current_widget.findChild(TextEditor)
            if text_editor:
                text_editor.undo()

    def redo_edit(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            text_editor = current_widget.findChild(TextEditor)
            if text_editor:
                text_editor.redo()

    def cut_text(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            text_editor = current_widget.findChild(TextEditor)
            if text_editor:
                text_editor.cut()

    def copy_text(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            text_editor = current_widget.findChild(TextEditor)
            if text_editor:
                text_editor.copy()

    def paste_text(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            text_editor = current_widget.findChild(TextEditor)
            if text_editor:
                text_editor.paste()

    def select_all_text(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            text_editor = current_widget.findChild(TextEditor)
            if text_editor:
                text_editor.select_all()
