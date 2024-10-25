from PyQt6.QtCore import QObject, pyqtSignal

class EditorSignals(QObject):
    modifiedChanged = pyqtSignal(object)

editor_signals = EditorSignals()