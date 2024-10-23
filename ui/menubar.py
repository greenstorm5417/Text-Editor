from PyQt6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog

def init_menu_bar(main_window):
    """Initialize the menu bar with File, Edit, Selection, and Help menus."""
    menu_bar = QMenuBar(main_window)

    # ----- File Menu -----
    file_menu = menu_bar.addMenu('File')

    new_action = QAction('New', main_window)
    new_action.setShortcut('Ctrl+N')
    new_action.triggered.connect(main_window.new_file)
    file_menu.addAction(new_action)

    open_action = QAction('Open...', main_window)
    open_action.setShortcut('Ctrl+O')
    open_action.triggered.connect(main_window.open_file)
    file_menu.addAction(open_action)

    save_action = QAction('Save', main_window)
    save_action.setShortcut('Ctrl+S')
    save_action.triggered.connect(main_window.save_file)
    file_menu.addAction(save_action)

    save_as_action = QAction('Save As...', main_window)
    save_as_action.triggered.connect(main_window.save_file_as)
    file_menu.addAction(save_as_action)

    file_menu.addSeparator()

    exit_action = QAction('Exit', main_window)
    exit_action.setShortcut('Ctrl+Q')
    exit_action.triggered.connect(main_window.close)
    file_menu.addAction(exit_action)

    # ----- Edit Menu -----
    edit_menu = menu_bar.addMenu('Edit')

    undo_action = QAction('Undo', main_window)
    undo_action.setShortcut('Ctrl+Z')
    undo_action.triggered.connect(main_window.undo_edit)
    edit_menu.addAction(undo_action)

    redo_action = QAction('Redo', main_window)
    redo_action.setShortcut('Ctrl+Y')
    redo_action.triggered.connect(main_window.redo_edit)
    edit_menu.addAction(redo_action)

    edit_menu.addSeparator()

    cut_action = QAction('Cut', main_window)
    cut_action.setShortcut('Ctrl+X')
    cut_action.triggered.connect(main_window.cut_text)
    edit_menu.addAction(cut_action)

    copy_action = QAction('Copy', main_window)
    copy_action.setShortcut('Ctrl+C')
    copy_action.triggered.connect(main_window.copy_text)
    edit_menu.addAction(copy_action)

    paste_action = QAction('Paste', main_window)
    paste_action.setShortcut('Ctrl+V')
    paste_action.triggered.connect(main_window.paste_text)
    edit_menu.addAction(paste_action)

    # ----- Selection Menu -----
    selection_menu = menu_bar.addMenu('Select')

    select_all_action = QAction('Select All', main_window)
    select_all_action.setShortcut('Ctrl+A')
    select_all_action.triggered.connect(main_window.select_all_text)
    selection_menu.addAction(select_all_action)

    # ----- Help Menu -----
    help_menu = menu_bar.addMenu('Help')

    about_action = QAction('About', main_window)
    about_action.triggered.connect(main_window.show_about_dialog)
    help_menu.addAction(about_action)
    
    return menu_bar  # Return the menu bar instance
