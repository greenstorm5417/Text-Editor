from PyQt6.QtWidgets import QProxyStyle
from PyQt6.QtGui import QStyleOptionTab
from PyQt6.QtCore import QStyle
from editor.theme import Theme

class CustomTabStyle(QProxyStyle):
    def drawControl(self, element, option, painter, widget=None):
        if element == QStyle.ControlElement.CE_TabBarTab:
            if isinstance(option, QStyleOptionTab):
                option = QStyleOptionTab(option)
                option.font = Theme.get_tab_font()
        super().drawControl(element, option, painter, widget)
