from PyQt6.QtWidgets import (
    QWidget, QTabBar, QStackedWidget, QVBoxLayout, QSplitter
)
from PyQt6.QtCore import Qt
from src.editor.themes.theme import Theme


class CustomTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the tab bar and stacked widget
        self.tab_bar = QTabBar()
        self.stacked_widget = QStackedWidget()

        # Set up the tab bar
        self.tab_bar.setMovable(True)
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.stacked_widget.setCurrentIndex)
        self.tab_bar.setExpanding(False)

        # Apply font from theme
        self.tab_bar.setFont(Theme.get_tab_font())

        # Create a splitter to allow resizing the tab bar
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.tab_bar)
        self.splitter.addWidget(self.stacked_widget)

        # Set initial sizes for splitter
        initial_tab_bar_height = Theme.scaled_size(Theme.TAB_BAR_HEIGHT)
        self.splitter.setSizes([initial_tab_bar_height, self.height() - initial_tab_bar_height])

        # Ensure the splitter handle is visible and set the cursor
        self.splitter.setHandleWidth(3)
        handle = self.splitter.handle(1)
        handle.setCursor(Qt.CursorShape.SplitVCursor)

        # Style the splitter handle
        self.splitter.setStyleSheet(f"""
        QSplitter::handle {{
            background-color: {Theme.color_to_stylesheet(Theme.TAB_BORDER_COLOR)};
        }}
        """)

        # Set up the layout for CustomTabWidget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Ensure no extra margins
        layout.setSpacing(0)  # Ensure no extra spacing between tab bar and content
        layout.addWidget(self.splitter)

        # Apply stylesheets to the tab bar
        self.apply_tab_bar_stylesheet()

    def addTab(self, widget, title):
        index = self.stacked_widget.addWidget(widget)
        self.tab_bar.addTab(title)
        self.tab_bar.setCurrentIndex(index)
        self.stacked_widget.setCurrentIndex(index)
        return index

    def removeTab(self, index):
        self.tab_bar.removeTab(index)
        widget = self.stacked_widget.widget(index)
        self.stacked_widget.removeWidget(widget)
        widget.deleteLater()

    def setCurrentIndex(self, index):
        self.tab_bar.setCurrentIndex(index)
        self.stacked_widget.setCurrentIndex(index)

    def currentIndex(self):
        return self.tab_bar.currentIndex()
    
    def currentWidget(self):
        """Return the current widget."""
        return self.stacked_widget.currentWidget()

    def count(self):
        return self.tab_bar.count()

    def widget(self, index):
        return self.stacked_widget.widget(index)

    def indexOf(self, widget):
        return self.stacked_widget.indexOf(widget)

    def tabText(self, index):
        return self.tab_bar.tabText(index)

    def setTabText(self, index, text):
        self.tab_bar.setTabText(index, text)

    def apply_tab_bar_stylesheet(self):
        """Apply custom stylesheet to the tab bar using Theme settings."""
        tab_bar_stylesheet = f"""
        QTabBar {{
            background: {Theme.color_to_stylesheet(Theme.TAB_BACKGROUND_COLOR)};
            min-height: {Theme.scaled_size(Theme.TAB_BAR_HEIGHT)}px
            

        }}
        QTabBar::tab {{
            background: {Theme.color_to_stylesheet(Theme.TAB_BACKGROUND_COLOR)};
            color: {Theme.color_to_stylesheet(Theme.TAB_TEXT_COLOR)};
            padding: 5px;
            margin-right: 2px;
            min-width: 80px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background: {Theme.color_to_stylesheet(Theme.TAB_ACTIVE_BACKGROUND_COLOR)};
            color: {Theme.color_to_stylesheet(Theme.TAB_TEXT_COLOR)};
        }}

        QTabBar::tab:hover {{
            background: {Theme.color_to_stylesheet(Theme.TAB_HOVER_BACKGROUND_COLOR)};
        }}

        QTabBar::close-button {{
            image: url(resources/icons/close_icon.svg);
            subcontrol-position: right;
            margin: 0px;
            padding: 0px;
        }}

        QTabBar::close-button:hover {{
            background: {Theme.color_to_stylesheet(Theme.CLOSE_BUTTON_HOVER_COLOR)};
        }}
        """
        self.tab_bar.setStyleSheet(tab_bar_stylesheet)

    def close_tab(self, index):
        # Forward the tab close request to the main window
        main_window = self.window()
        if main_window and hasattr(main_window, 'close_tab'):
            main_window.close_tab(index)
        else:
            print("Main window does not have close_tab")
