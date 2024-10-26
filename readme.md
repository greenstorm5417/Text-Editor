# PyQt6 Text Editor

A feature-rich text editor implementation built with PyQt6, featuring advanced text manipulation capabilities, undo/redo functionality, and comprehensive event handling.

## Overview

This text editor implementation provides a robust foundation for text editing applications, with a focus on reliability and extensibility. Built using PyQt6, it implements sophisticated text manipulation features while maintaining clean, maintainable code architecture.

## Features

### Core Functionality
- Advanced text editing capabilities
- Real-time text manipulation
- Multi-line text support
- Cursor management
- Selection handling

### Undo/Redo System
- Word-based undo/redo operations
- Smart character grouping
- Comprehensive action tracking
- Selection-aware operations
- State preservation

### Text Manipulation
- Intelligent text insertion and deletion
- Word-wise operations
- Multi-line text operations
- Selection-based editing
- Backspace handling (character-wise and word-wise)

### User Interface
- PyQt6-based interface
- Modern look and feel
- Responsive design
- Real-time updates

### Developer Features
- Comprehensive logging system
- Detailed debugging information
- Extensible architecture
- Clear separation of concerns

## Technical Architecture

### Core Components

#### Editor Base
- Text storage and manipulation
- Cursor management
- Selection handling
- Event processing

#### UndoRedoMixin
- Action tracking
- State management
- Operation history
- Reversible operations

#### Action Management
- Action recording
- State transitions
- Operation context
- History management

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
# Install required packages
pip install PyQt6

# Once requirements.txt is available:
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Usage

### Basic Operations

#### Text Editing
- Type normally to insert text
- Use arrow keys for navigation
- Click to position cursor
- Drag to select text

#### Undo/Redo
- `Ctrl+Z`: Undo last action
- `Ctrl+Shift+Z`: Redo last undone action
- `Ctrl+Backspace`: Delete previous word

#### Selection
- Click and drag to select text
- Shift + Arrow keys for keyboard selection
- Double-click to select word
- Triple-click to select line

## Implementation Details

### Text Processing

The editor handles text processing through several key mechanisms:

```python
def handle_character_input(self, text, cursor_before):
    """
    Handles character input with word grouping
    """
    # Implementation handles:
    # - Word grouping
    # - Selection replacement
    # - Cursor management
    # - State updates
```

### State Management

The system maintains various states:
- Document content
- Cursor position
- Selection state
- Modification status
- Undo/redo history

### Event Handling

Comprehensive event handling includes:
- Key events
- Mouse events
- Selection events
- Modification events

## Debugging and Logging

The system includes comprehensive logging:

```python
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

Debug information includes:
- Operation tracking
- State changes
- User interactions
- Error conditions

## Development Guide

### Adding New Features

1. Identify the appropriate component
2. Implement the feature
3. Add necessary logging
4. Update state management
5. Add undo/redo support if needed

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Include docstrings for all methods
- Add debug logging for important operations

### Testing

Create tests for:
- Basic text operations
- Undo/redo functionality
- Selection handling
- Edge cases
- State management

## Performance Considerations

- Efficient text manipulation algorithms
- Optimized state management
- Minimal memory usage
- Responsive user interface

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow existing code style
- Add appropriate documentation
- Include necessary tests
- Update README if needed

## Known Issues

- [List any known issues or limitations]

## Future Enhancements

- [List planned future features or improvements]

## License

[Your chosen license]

## Acknowledgments

- PyQt6 framework
- [Any other libraries or resources used]

## Contact

[Your contact information]

---

**Note**: This project is under active development. Features and implementations may change.

