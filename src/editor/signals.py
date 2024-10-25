from PyQt6.QtCore import QObject, pyqtSignal

class EditorSignals(QObject):
    modifiedChanged = pyqtSignal(object)

# Create a global instance
editor_signals = EditorSignals()