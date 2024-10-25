from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QMenu, QSizePolicy
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QAction, QPalette
from src.ui.widgets.buttons import CustomButton
from src.editor.themes.theme import Theme

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setFixedHeight(Theme.scaled_size(Theme.TITLE_BAR_HEIGHT))

        # Layout for the title bar
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Set the background color of the title bar
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Theme.BACKGROUND_COLOR)
        self.setPalette(palette)

        # Icon Label
        self.icon_label = QLabel()
        icon_container_size = Theme.scaled_size(Theme.ICON_CONTAINER_SIZE)
        self.icon_label.setFixedSize(icon_container_size, icon_container_size)

        pixmap = QPixmap("resources/icons/logo.svg")
        if pixmap.isNull():
            # Handle missing icon
            self.icon_label.setText("Icon")
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Set text color
            icon_palette = self.icon_label.palette()
            icon_palette.setColor(QPalette.ColorRole.WindowText, Theme.ICON_TEXT_COLOR)
            self.icon_label.setPalette(icon_palette)
        else:
            # Render SVG using QPixmap
            icon_size = Theme.scaled_size(Theme.ICON_SIZE)
            self.icon_label.setPixmap(
                pixmap.scaled(
                    icon_size,
                    icon_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the icon to the layout
        self.layout.addWidget(self.icon_label)

        # Initialize menu buttons
        self.init_menu_buttons()

        # Spacer to push window control buttons to the far right
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.layout.addWidget(self.spacer)

        # Window control buttons with text labels
        button_size = Theme.scaled_size(Theme.BUTTON_HEIGHT)
        self.button_minimize = CustomButton("_", self,
                                            background_color=Theme.BACKGROUND_COLOR,
                                            hover_color=Theme.HOVER_COLOR,
                                            text_color=Theme.TEXT_COLOR)
        self.button_minimize.setFixedSize(button_size, button_size)
        self.button_maximize = CustomButton("□", self,
                                            background_color=Theme.BACKGROUND_COLOR,
                                            hover_color=Theme.HOVER_COLOR,
                                            text_color=Theme.TEXT_COLOR)
        self.button_maximize.setFixedSize(button_size, button_size)
        self.button_close = CustomButton("✕", self,
                                         background_color=Theme.BACKGROUND_COLOR,
                                         hover_color=Theme.CLOSE_BUTTON_HOVER_COLOR,
                                         text_color=Theme.TEXT_COLOR)
        self.button_close.setFixedSize(button_size, button_size)

        # Connect the buttons
        self.button_minimize.clicked.connect(self.parent.showMinimized)
        self.button_maximize.clicked.connect(self.toggle_maximize)
        self.button_close.clicked.connect(self.parent.close)

        # Add window control buttons to the layout
        self.layout.addWidget(self.button_minimize)
        self.layout.addWidget(self.button_maximize)
        self.layout.addWidget(self.button_close)

        self.setLayout(self.layout)

        # Variables to handle window dragging
        self.is_dragging = False
        self.drag_position = QPoint()

    def init_menu_buttons(self):
        button_width = Theme.scaled_size(Theme.BUTTON_WIDTH)
        button_height = Theme.scaled_size(Theme.BUTTON_HEIGHT)

        # File Button
        self.button_file = CustomButton("File", self,
                                        background_color=Theme.BACKGROUND_COLOR,
                                        hover_color=Theme.HOVER_COLOR,
                                        text_color=Theme.TEXT_COLOR)
        self.button_file.setFixedSize(button_width, button_height)
        self.button_file.setMenu(self.create_file_menu())
        self.layout.addWidget(self.button_file)

        # Edit Button
        self.button_edit = CustomButton("Edit", self,
                                        background_color=Theme.BACKGROUND_COLOR,
                                        hover_color=Theme.HOVER_COLOR,
                                        text_color=Theme.TEXT_COLOR)
        self.button_edit.setFixedSize(button_width, button_height)
        self.button_edit.setMenu(self.create_edit_menu())
        self.layout.addWidget(self.button_edit)

        # Selection Button
        self.button_selection = CustomButton("Select", self,
                                             background_color=Theme.BACKGROUND_COLOR,
                                             hover_color=Theme.HOVER_COLOR,
                                             text_color=Theme.TEXT_COLOR)
        self.button_selection.setFixedSize(button_width, button_height)
        self.button_selection.setMenu(self.create_selection_menu())
        self.layout.addWidget(self.button_selection)

        # Help Button
        self.button_help = CustomButton("Help", self,
                                        background_color=Theme.BACKGROUND_COLOR,
                                        hover_color=Theme.HOVER_COLOR,
                                        text_color=Theme.TEXT_COLOR)
        self.button_help.setFixedSize(button_width, button_height)
        self.button_help.setMenu(self.create_help_menu())
        self.layout.addWidget(self.button_help)

    def create_file_menu(self):
        menu = QMenu()

        # Actions
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        new_action.triggered.connect(self.parent.new_file)
        menu.addAction(new_action)
        self.parent.addAction(new_action)  # Add action to the main window

        open_action = QAction('Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        open_action.triggered.connect(self.parent.open_file)
        menu.addAction(open_action)
        self.parent.addAction(open_action)

        # **Add "Open Folder" Action**
        open_folder_action = QAction('Open Folder...', self)
        open_folder_action.setShortcut('Ctrl+Shift+O')
        open_folder_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        open_folder_action.triggered.connect(self.parent.open_folder)  # Connect to open_folder method
        menu.addAction(open_folder_action)
        self.parent.addAction(open_folder_action)

        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        save_action.triggered.connect(self.parent.save_file)
        menu.addAction(save_action)
        self.parent.addAction(save_action)

        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        save_as_action.triggered.connect(self.parent.save_file_as)
        menu.addAction(save_as_action)
        self.parent.addAction(save_as_action)

        menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        exit_action.triggered.connect(self.parent.close)
        menu.addAction(exit_action)
        self.parent.addAction(exit_action)

        return menu

    def create_edit_menu(self):
        menu = QMenu()

        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        undo_action.triggered.connect(self.parent.undo_edit)
        menu.addAction(undo_action)
        self.parent.addAction(undo_action)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        redo_action.triggered.connect(self.parent.redo_edit)
        menu.addAction(redo_action)
        self.parent.addAction(redo_action)

        menu.addSeparator()

        cut_action = QAction('Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        cut_action.triggered.connect(self.parent.cut_text)
        menu.addAction(cut_action)
        self.parent.addAction(cut_action)

        copy_action = QAction('Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        copy_action.triggered.connect(self.parent.copy_text)
        menu.addAction(copy_action)
        self.parent.addAction(copy_action)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        paste_action.triggered.connect(self.parent.paste_text)
        menu.addAction(paste_action)
        self.parent.addAction(paste_action)

        return menu

    def create_selection_menu(self):
        menu = QMenu()

        select_all_action = QAction('Select All', self)
        select_all_action.setShortcut('Ctrl+A')
        select_all_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        select_all_action.triggered.connect(self.parent.select_all_text)
        menu.addAction(select_all_action)
        self.parent.addAction(select_all_action)

        return menu

    def create_help_menu(self):
        menu = QMenu()

        about_action = QAction('About', self)
        about_action.triggered.connect(self.parent.show_about_dialog)
        menu.addAction(about_action)

        return menu

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.button_maximize.setText("□")
        else:
            self.parent.showMaximized()
            self.button_maximize.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.parent.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
