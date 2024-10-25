import sys
from PyQt6.QtWidgets import QApplication
from src.ui.window import MainWindow
from src.editor.themes.theme import Theme

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Theme.initialize_scaling()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
