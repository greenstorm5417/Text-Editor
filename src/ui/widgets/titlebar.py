from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QAction, QPalette
from src.ui.widgets.buttons import CustomButton
from src.editor.themes.theme import Theme


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_dragging = False
        self.drag_position = QPoint()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Initialize the user interface components."""
        self.set_fixed_height()
        self.set_background()
        self.create_layout()
        self.create_icon_label()
        self.init_menu_buttons()
        self.add_spacer()
        self.create_window_controls()
        self.setLayout(self.layout)

    def set_fixed_height(self):
        """Set the fixed height for the title bar."""
        self.setFixedHeight(Theme.scaled_size(Theme.TITLE_BAR_HEIGHT))

    def set_background(self):
        """Set the background color of the title bar."""
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Theme.BACKGROUND_COLOR)
        self.setPalette(palette)

    def create_layout(self):
        """Create the main layout for the title bar."""
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def create_icon_label(self):
        """Create and add the icon label to the layout."""
        self.icon_label = QLabel()
        icon_container_size = Theme.scaled_size(Theme.ICON_CONTAINER_SIZE)
        self.icon_label.setFixedSize(icon_container_size, icon_container_size)

        pixmap = QPixmap("resources/icons/logo.svg")
        if pixmap.isNull():
            self.icon_label.setText("Icon")
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_palette = self.icon_label.palette()
            icon_palette.setColor(QPalette.ColorRole.WindowText, Theme.ICON_TEXT_COLOR)
            self.icon_label.setPalette(icon_palette)
        else:
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

        self.layout.addWidget(self.icon_label)

    def init_menu_buttons(self):
        """Initialize the menu buttons and add them to the layout."""
        button_width = Theme.scaled_size(Theme.BUTTON_WIDTH)
        button_height = Theme.scaled_size(Theme.BUTTON_HEIGHT)

        # File Button
        self.button_file = self.create_menu_button("File", button_width, button_height, self.create_file_menu())
        self.layout.addWidget(self.button_file)

        # Edit Button
        self.button_edit = self.create_menu_button("Edit", button_width, button_height, self.create_edit_menu())
        self.layout.addWidget(self.button_edit)

        # Select Button
        self.button_selection = self.create_menu_button("Select", button_width, button_height, self.create_selection_menu())
        self.layout.addWidget(self.button_selection)

        # Help Button
        self.button_help = self.create_menu_button("Help", button_width, button_height, self.create_help_menu())
        self.layout.addWidget(self.button_help)

    def create_menu_button(self, text, width, height, menu):
        """Create a menu button with the given properties."""
        button = CustomButton(
            text, self,
            background_color=Theme.BACKGROUND_COLOR,
            hover_color=Theme.HOVER_COLOR,
            text_color=Theme.TEXT_COLOR
        )
        button.setFixedSize(width, height)
        button.setMenu(menu)
        return button

    def add_spacer(self):
        """Add a spacer to push window control buttons to the far right."""
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.layout.addWidget(spacer)

    def create_window_controls(self):
        """Create window control buttons and add them to the layout."""
        button_size = Theme.scaled_size(Theme.BUTTON_HEIGHT)

        self.button_minimize = self.create_control_button("_", button_size)
        self.layout.addWidget(self.button_minimize)

        self.button_maximize = self.create_control_button("□", button_size)
        self.layout.addWidget(self.button_maximize)

        self.button_close = self.create_control_button("✕", button_size, Theme.CLOSE_BUTTON_HOVER_COLOR)
        self.layout.addWidget(self.button_close)

    def create_control_button(self, text, size, hover_color=None):
        """Create a window control button with the given properties."""
        button = CustomButton(
            text, self,
            background_color=Theme.BACKGROUND_COLOR,
            hover_color=hover_color or Theme.HOVER_COLOR,
            text_color=Theme.TEXT_COLOR
        )
        button.setFixedSize(size, size)
        return button

    def connect_signals(self):
        """Connect signals to their respective slots."""
        self.button_minimize.clicked.connect(self.parent.showMinimized)
        self.button_maximize.clicked.connect(self.toggle_maximize)
        self.button_close.clicked.connect(self.parent.close)

    def create_file_menu(self):
        """Create and return the File menu."""
        menu = QMenu()

        new_action = self.create_action('New', 'Ctrl+N', self.parent.new_file)
        menu.addAction(new_action)

        open_action = self.create_action('Open...', 'Ctrl+O', self.parent.open_file)
        menu.addAction(open_action)

        open_folder_action = self.create_action('Open Folder...', 'Ctrl+Shift+O', self.parent.open_folder)
        menu.addAction(open_folder_action)

        save_action = self.create_action('Save', 'Ctrl+S', self.parent.save_file)
        menu.addAction(save_action)

        save_as_action = self.create_action('Save As...', None, self.parent.save_file_as)
        menu.addAction(save_as_action)

        menu.addSeparator()

        exit_action = self.create_action('Exit', 'Ctrl+Q', self.parent.close)
        menu.addAction(exit_action)

        return menu

    def create_edit_menu(self):
        """Create and return the Edit menu."""
        menu = QMenu()

        undo_action = self.create_action('Undo', 'Ctrl+Z', self.parent.undo_edit)
        menu.addAction(undo_action)

        redo_action = self.create_action('Redo', 'Ctrl+Y', self.parent.redo_edit)
        menu.addAction(redo_action)

        menu.addSeparator()

        cut_action = self.create_action('Cut', 'Ctrl+X', self.parent.cut_text)
        menu.addAction(cut_action)

        copy_action = self.create_action('Copy', 'Ctrl+C', self.parent.copy_text)
        menu.addAction(copy_action)

        paste_action = self.create_action('Paste', 'Ctrl+V', self.parent.paste_text)
        menu.addAction(paste_action)

        return menu

    def create_selection_menu(self):
        """Create and return the Selection menu."""
        menu = QMenu()

        select_all_action = self.create_action('Select All', 'Ctrl+A', self.parent.select_all_text)
        menu.addAction(select_all_action)

        return menu

    def create_help_menu(self):
        """Create and return the Help menu."""
        menu = QMenu()

        about_action = QAction('About', self)
        about_action.triggered.connect(self.parent.show_about_dialog)
        menu.addAction(about_action)

        return menu

    def create_action(self, text, shortcut, slot):
        """Create an action with the given properties."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
            action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        action.triggered.connect(slot)
        self.parent.addAction(action)  # Add action to the main window
        return action

    def toggle_maximize(self):
        """Toggle between maximized and normal window states."""
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.button_maximize.setText("□")
        else:
            self.parent.showMaximized()
            self.button_maximize.setText("❐")

    def mousePressEvent(self, event):
        """Handle the mouse press event for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle the mouse move event for window dragging."""
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.parent.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle the mouse release event after dragging."""
        self.is_dragging = False
