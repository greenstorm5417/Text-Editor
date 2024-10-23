# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.window import MainWindow
from editor.theme import Theme  # Import Theme

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Theme.initialize_scaling()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
