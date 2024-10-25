from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QApplication

class Theme:
    # Initialize scaling factor
    SCALING_FACTOR = 1.0

    # Font Definitions
    DEFAULT_FONT_FAMILY = "Consolas"
    ALTERNATIVE_FONT_FAMILY = "Courier New"
    FONT_SIZE = 12

    BUTTON_FONT_SIZE = 14
    BUTTON_FONT_WEIGHT = QFont.Weight.Bold

    TAB_FONT_SIZE = 12
    TAB_FONT_WEIGHT = QFont.Weight.Bold

    # Window Sizes
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    TITLE_BAR_HEIGHT = 40
    TAB_BAR_HEIGHT = 35

    # UI Element Sizes
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 40
    ICON_SIZE = 24
    ICON_CONTAINER_SIZE = 40
    LINE_WIDTH = 2

    # Editor Layout
    EDITOR_MARGIN_TOP = 5
    EDITOR_MARGIN_BOTTOM = 5
    EDITOR_MARGIN_LEFT = 5
    EDITOR_MARGIN_RIGHT = 5
    EDITOR_LINE_SPACING = 1.2
    EDITOR_LINE_NUMBER_AREA_WIDTH = 50
    CONTENT_WIDTH_PADDING = 20
    CONTENT_HEIGHT_PADDING = 20
    LINE_NUMBER_PADDING = 10
    LINE_NUMBER_PADDING_RIGHT = 5

    # Scrollbar Settings
    EDITOR_SCROLLBAR_WIDTH = 12

    # Color Definitions
    # Main UI Colors
    BACKGROUND_COLOR = QColor("#1E1E1E")
    TEXT_COLOR = QColor("#D4D4D4")
    HOVER_COLOR = QColor("#333333")
    LINE_COLOR = QColor("#3C3C3C")

    # Editor Colors
    EDITOR_BACKGROUND_COLOR = QColor("#1E1E1E")
    EDITOR_TEXT_COLOR = QColor("#D4D4D4")
    EDITOR_CURSOR_COLOR = QColor("#AEAFAD")
    EDITOR_SELECTION_BACKGROUND = QColor("#264F78")
    EDITOR_CURRENT_LINE_COLOR = QColor("#2A2D2E")
    EDITOR_WHITESPACE_COLOR = QColor("#3B3B3B")

    # Line Number Colors
    EDITOR_LINE_NUMBER_BACKGROUND = QColor("#1E1E1E")
    EDITOR_LINE_NUMBER_COLOR = QColor("#858585")
    EDITOR_ACTIVE_LINE_NUMBER_COLOR = QColor("#D7BA7D")

    # Scrollbar Colors
    EDITOR_SCROLLBAR_BACKGROUND = QColor("#333333")
    EDITOR_SCROLLBAR_HANDLE = QColor("#5A5A5A")
    EDITOR_SCROLLBAR_HANDLE_HOVER = QColor("#6E6E6E")

    # Tab Colors
    TAB_BACKGROUND_COLOR = QColor("#2D2D2D")
    TAB_ACTIVE_BACKGROUND_COLOR = QColor("#1E1E1E")
    TAB_HOVER_BACKGROUND_COLOR = QColor("#3E3E3E")
    TAB_TEXT_COLOR = QColor("#D4D4D4")
    TAB_BORDER_COLOR = QColor("#252526")

    # Special Colors
    CLOSE_BUTTON_HOVER_COLOR = QColor("#F48771")
    ICON_TEXT_COLOR = QColor("#D4D4D4")
    CURSOR_COLOR = QColor("#AEAFAD")
    CURSOR_WIDTH = 2
    SELECTION_COLOR = QColor("#264F78")


    SYNTAX_COLORS = {
        'text': QColor('#D4D4D4'),
        'keyword': QColor('#569CD6'),
        'keyword_declaration': QColor('#C586C0'),
        'keyword_namespace': QColor('#C586C0'),
        'keyword_pseudo': QColor('#C586C0'),
        'keyword_reserved': QColor('#C586C0'),
        'keyword_type': QColor('#4EC9B0'),
        'name': QColor('#9CDCFE'),
        'name_builtin': QColor('#DCDCAA'),
        'name_function': QColor('#DCDCAA'),
        'name_class': QColor('#4EC9B0'),
        'name_decorator': QColor('#C586C0'),
        'name_exception': QColor('#C586C0'),
        'name_variable': QColor('#9CDCFE'),
        'name_constant': QColor('#9CDCFE'),
        'name_attribute': QColor('#9CDCFE'),
        'string': QColor('#CE9178'),
        'string_doc': QColor('#608B4E'),
        'string_interpol': QColor('#CE9178'),
        'string_escape': QColor('#D7BA7D'),
        'number': QColor('#B5CEA8'),
        'operator': QColor('#D4D4D4'),
        'punctuation': QColor('#D4D4D4'),
        'comment': QColor('#6A9955'),
        'comment_multiline': QColor('#6A9955'),
        'comment_preproc': QColor('#C586C0'),
        'generic_deleted': QColor('#D16969'),
        'generic_emph': QColor('#D4D4D4'),
        'generic_error': QColor('#F44747'),
        'generic_heading': QColor('#4EC9B0'),
        'generic_inserted': QColor('#B5CEA8'),
        'generic_output': QColor('#D4D4D4'),
        'generic_prompt': QColor('#D4D4D4'),
        'generic_strong': QColor('#D4D4D4'),
        'generic_subheading': QColor('#4EC9B0'),
        'generic_traceback': QColor('#F44747'),
        'error': QColor('#F44747'),
    }

    @staticmethod
    def initialize_scaling():
        """Initialize the scaling factor based on screen resolution."""
        app = QApplication.instance()
        if not app:
            return
        screen = app.primaryScreen()
        size = screen.size()
        Theme.SCALING_FACTOR = size.height() / 1000.0

    @staticmethod
    def scaled_size(value):
        """Scale a size value based on the screen resolution."""
        return int(value * Theme.SCALING_FACTOR)

    @staticmethod
    def get_default_font():
        """Get the default editor font."""
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
        """Get the font for buttons."""
        font = QFont()
        font.setPointSize(int(Theme.BUTTON_FONT_SIZE * Theme.SCALING_FACTOR))
        font.setWeight(Theme.BUTTON_FONT_WEIGHT)
        return font

    @staticmethod
    def get_tab_font():
        """Get the font for tabs."""
        font = QFont()
        font.setPointSize(int(Theme.TAB_FONT_SIZE * Theme.SCALING_FACTOR))
        font.setWeight(Theme.TAB_FONT_WEIGHT)
        return font

    @staticmethod
    def color_to_stylesheet(qcolor):
        """Convert a QColor to a stylesheet color string."""
        return qcolor.name()

    @staticmethod
    def get_editor_stylesheet():
        """Get the stylesheet for the text editor."""
        return f"""
            QWidget {{
                background-color: {Theme.EDITOR_BACKGROUND_COLOR.name()};
                color: {Theme.EDITOR_TEXT_COLOR.name()};
            }}
            QScrollBar:vertical {{
                background: {Theme.EDITOR_SCROLLBAR_BACKGROUND.name()};
                width: {Theme.EDITOR_SCROLLBAR_WIDTH}px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.EDITOR_SCROLLBAR_HANDLE.name()};
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.EDITOR_SCROLLBAR_HANDLE_HOVER.name()};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {Theme.EDITOR_SCROLLBAR_BACKGROUND.name()};
                height: {Theme.EDITOR_SCROLLBAR_WIDTH}px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {Theme.EDITOR_SCROLLBAR_HANDLE.name()};
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Theme.EDITOR_SCROLLBAR_HANDLE_HOVER.name()};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """