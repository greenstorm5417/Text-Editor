from abc import ABC, abstractmethod


class SyntaxHighlighter(ABC):
    @abstractmethod
    def highlight(self, lines):
        pass

