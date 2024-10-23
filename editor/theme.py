# editor/theme.py
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QApplication

class Theme:
    # Initialize scaling factor
    SCALING_FACTOR = 1.0

    @staticmethod
    def initialize_scaling():
        """Compute scaling factor based on screen size."""
        app = QApplication.instance()
        if not app:
            return
        screen = app.primaryScreen()
        size = screen.size()
        # Base scaling on a reference height (e.g., 1000px)
        Theme.SCALING_FACTOR = size.height() / 1000.0

    @staticmethod
    def scaled_size(value):
        """Scale a given size based on the scaling factor."""
        return int(value * Theme.SCALING_FACTOR)

    # Fonts
    DEFAULT_FONT_FAMILY = "Consolas"
    ALTERNATIVE_FONT_FAMILY = "Courier New"
    FONT_SIZE = 12  # Base font size

    BUTTON_FONT_SIZE = 14
    BUTTON_FONT_WEIGHT = QFont.Weight.Bold

    TAB_FONT_SIZE = 12
    TAB_FONT_WEIGHT = QFont.Weight.Bold

    # Colors
    CURSOR_COLOR = QColor('white')
    SELECTION_COLOR = QColor('lightgray')
    TEXT_COLOR = QColor('white')

    BACKGROUND_COLOR = QColor("#444444")
    HOVER_COLOR = QColor("#555555")
    TEXT_COLOR = QColor("white")
    CLOSE_BUTTON_HOVER_COLOR = QColor("red")
    ICON_TEXT_COLOR = QColor("white")

    TAB_BACKGROUND_COLOR = QColor("#444444")
    TAB_ACTIVE_BACKGROUND_COLOR = QColor("#555555")
    TAB_TEXT_COLOR = QColor("white")

    # Sizes
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 40
    TITLE_BAR_HEIGHT = 40
    ICON_SIZE = 24
    ICON_CONTAINER_SIZE = 40
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    TAB_BAR_HEIGHT = 30

    @staticmethod
    def get_default_font():
        font = QFont()
        if QFont(Theme.DEFAULT_FONT_FAMILY).exactMatch():
            font.setFamily(Theme.DEFAULT_FONT_FAMILY)
        elif QFont(Theme.ALTERNATIVE_FONT_FAMILY).exactMatch():
            font.setFamily(Theme.ALTERNATIVE_FONT_FAMILY)
        else:
            font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(int(Theme.FONT_SIZE * Theme.SCALING_FACTOR))
        return font

    @staticmethod
    def get_button_font():
        font = QFont()
        font.setPointSize(int(Theme.BUTTON_FONT_SIZE * Theme.SCALING_FACTOR))
        font.setWeight(Theme.BUTTON_FONT_WEIGHT)
        return font

    @staticmethod
    def get_tab_font():
        font = QFont()
        font.setPointSize(int(Theme.TAB_FONT_SIZE * Theme.SCALING_FACTOR))
        font.setWeight(Theme.TAB_FONT_WEIGHT)
        return font
