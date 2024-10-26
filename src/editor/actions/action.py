class Action:
    def __init__(self, action_type, position, text, selection_start=None, selection_end=None, cursor_before=None, cursor_after=None, description=None):
        self.action_type = action_type  # 'insert' or 'delete'
        self.position = position        # (line, column)
        self.text = text                # Text inserted or deleted
        self.selection_start = selection_start  # For selections
        self.selection_end = selection_end
        self.cursor_before = cursor_before      # Cursor position before the action
        self.cursor_after = cursor_after        # Cursor position after the action
        self.description = description
