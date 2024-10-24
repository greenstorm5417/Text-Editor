# ui/custom_tab_widget.py

from PyQt6.QtWidgets import (
    QWidget, QTabBar, QStackedWidget, QVBoxLayout, QFrame
)
from PyQt6.QtCore import Qt
from editor.theme import Theme


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

        # Create a vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # No spacing between widgets

        # Add the tab bar to the layout
        layout.addWidget(self.tab_bar)

        # Add a line separator
        self.separator_line = QFrame()
        self.separator_line.setFrameShape(QFrame.Shape.HLine)
        self.separator_line.setFrameShadow(QFrame.Shadow.Plain)
        # Set the color and thickness of the line
        self.separator_line.setStyleSheet(f"color: {Theme.color_to_stylesheet(Theme.TAB_BORDER_COLOR)};")
        self.separator_line.setFixedHeight(2)
        layout.addWidget(self.separator_line)

        # Add the stacked widget
        layout.addWidget(self.stacked_widget)

        # Apply stylesheets
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
