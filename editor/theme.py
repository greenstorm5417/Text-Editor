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
    TAB_HOVER_BACKGROUND_COLOR = QColor("#666666")
    TAB_TEXT_COLOR = QColor("white")
    TAB_BORDER_COLOR = QColor("#888888")

    LINE_NUMBER_COLOR = QColor('gray')

    # Sizes
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 40
    TITLE_BAR_HEIGHT = 40
    ICON_SIZE = 24
    ICON_CONTAINER_SIZE = 40
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    TAB_BAR_HEIGHT = 35

    # Lines
    LINE_COLOR = QColor("#888888")  # Default gray color
    LINE_WIDTH = 2  # Default line width (in pixels)



    # Syntax highlighting colors
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

    @staticmethod
    def color_to_stylesheet(qcolor):
        """Converts a QColor to a stylesheet-compatible string."""
        return qcolor.name()