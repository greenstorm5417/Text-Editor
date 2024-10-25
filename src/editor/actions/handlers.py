from PyQt6.QtWidgets import QMessageBox, QFileDialog
from src.editor.highlighting.pygments import PygmentsSyntaxHighlighter
from src.editor.base import TextEditor
import os 

class FileOperationsMixin:
    def open_file(self):
        """Open a file dialog to select and open a file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.add_new_tab(content,
                                 title=file_path.split('/')[-1],
                                 file_path=file_path)  # Pass the file path
                self.no_tabs_label.hide()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def open_folder(self):
        """Open a folder dialog to select a directory and load it in the FileTreeContainer."""
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", "", QFileDialog.Option.ShowDirsOnly)
        if folder_path:
            try:
                # Access the FileTreeContainer using its index (assuming index=1)
                file_tree_container = self.containers_manager.containers.get(1)
                if file_tree_container:
                    file_tree_container.set_root_directory(folder_path)
                    self.containers_manager.show_container(1)  # Show the FileTreeContainer
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open folder:\n{e}")

    def save_file(self):
        """Save the current file."""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            text_editor = current_widget.findChild(TextEditor)
            if text_editor:
                if text_editor.file_path:  # If file was previously saved
                    try:
                        with open(text_editor.file_path, 'w', encoding='utf-8') as file:
                            file.write(text_editor.toPlainText())
                        text_editor.set_modified(False)
                        self.update_tab_title(text_editor)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
                else:
                    self.save_file_as()  # This will handle updating the highlighter


    def save_file_as(self):
        """Save the current file with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "Untitled.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            current_widget = self.tab_widget.currentWidget()
            if current_widget:
                text_editor = current_widget.findChild(TextEditor)
                if text_editor:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(text_editor.toPlainText())
                        text_editor.file_path = file_path
                        text_editor.set_modified(False)
                        index = self.tab_widget.indexOf(current_widget)
                        self.tab_widget.setTabText(index, os.path.basename(file_path))

                        # **Update the syntax highlighter based on new file extension**
                        _, ext = os.path.splitext(file_path)
                        ext = ext.lower().lstrip('.')
                        language = self.get_language_from_extension(ext)
                        if language:
                            highlighter = PygmentsSyntaxHighlighter(language)
                            text_editor.set_highlighter(highlighter)
                        else:
                            text_editor.set_highlighter(None)
                        text_editor.update_highlighting()

                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")


    def closeEvent(self, event):
        """Check for unsaved changes before closing."""
        unsaved_tabs = []
        for index in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(index)
            text_editor = widget.findChild(TextEditor)
            if text_editor and text_editor.is_modified:
                unsaved_tabs.append((index, self.tab_widget.tabText(index).rstrip('*')))

        if unsaved_tabs:
            tab_names = "\n".join([f"• {name}" for _, name in unsaved_tabs])
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                f"The following files have unsaved changes:\n{tab_names}\n\nDo you want to save them before exiting?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            if reply == QMessageBox.StandardButton.Save:
                for index, name in unsaved_tabs:
                    widget = self.tab_widget.widget(index)
                    text_editor = widget.findChild(TextEditor)
                    if text_editor:
                        if text_editor.file_path:
                            try:
                                with open(text_editor.file_path, 'w', encoding='utf-8') as file:
                                    file.write(text_editor.toPlainText())
                                text_editor.set_modified(False)
                                self.update_tab_title(text_editor)
                            except Exception as e:
                                QMessageBox.critical(self, "Error", f"Could not save file '{name}':\n{e}")
                                event.ignore()
                                return
                        else:
                            file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", name,
                                                                       "Text Files (*.txt);;All Files (*)")
                            if file_path:
                                try:
                                    with open(file_path, 'w', encoding='utf-8') as file:
                                        file.write(text_editor.toPlainText())
                                    text_editor.file_path = file_path
                                    text_editor.set_modified(False)
                                    self.tab_widget.setTabText(index, file_path.split('/')[-1])
                                except Exception as e:
                                    QMessageBox.critical(self, "Error", f"Could not save file '{name}':\n{e}")
                                    event.ignore()
                                    return
                            else:
                                event.ignore()
                                return
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

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


