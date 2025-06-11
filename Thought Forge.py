__version__ = "1.0.0"

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QTextEdit, QHBoxLayout, QMenuBar, QMenu,
    QStatusBar, QFileDialog, QMessageBox, QTreeView,
    QSplitter, QTextBrowser
)
from PyQt6.QtGui import QAction, QIcon, QFileSystemModel
from PyQt6 import QtCore
import sys
import os

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super(MarkdownEditor, self).__init__()
        
        self.window_width, self.window_height = 1000, 600
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowIcon(QIcon("thoughtForge.ico"))
        self.setWindowTitle("Untitled - ThoughtForge")
        self.setStyleSheet("""
                            QWidget {
                                font-size: 18px;
                            }
                           """)
        
        # Track the current file path
        self.current_file_path = None
        
        self.init_ui()
        self.init_config_signals()
        
    def init_ui(self):
        # Create a central widget and a horizontal layout
        self.main_window = QWidget()
        self.layout = QHBoxLayout(self.main_window)
        self.setCentralWidget(self.main_window)
        
        # Create a splitter to divide the window into two parts
        self.splitter = QSplitter(QtCore.Qt.Orientation.Horizontal, self.main_window)
        self.layout.addWidget(self.splitter)
        
        # Add a file explorer (QTreeView with QFileSystemModel)
        current_dir = os.path.abspath(__file__)
        self.file_explorer = QTreeView(self.splitter)
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(os.path.dirname(current_dir))
        self.file_explorer.setModel(self.file_model)
        self.file_explorer.setRootIndex(self.file_model.index(os.path.dirname(current_dir)))
        self.file_explorer.setColumnWidth(0, 250)
        self.file_explorer.setStyleSheet("QTreeView { font-size: 14px; }")
        # Filter to only show .md files
        self.file_model.setNameFilters(["*.md"])
        self.file_model.setNameFilterDisables(False)
        
        # Replace the container widget with a QSplitter for toggling orientation
        self.editor_viewer_splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)  # Default: Horizontal
        self.md_editor = QTextEdit()
        self.md_viewer = QTextBrowser()
        self.md_viewer.setOpenExternalLinks(True)
        
        self.editor_viewer_splitter.addWidget(self.md_editor)
        self.editor_viewer_splitter.addWidget(self.md_viewer)
        
        # Add the file explorer and the editor/viewer splitter to the main splitter
        self.splitter.addWidget(self.file_explorer)
        self.splitter.addWidget(self.editor_viewer_splitter)
        
        # Set initial splitter sizes
        self.splitter.setSizes([200, 800])
        self.editor_viewer_splitter.setSizes([500, 500])
        
        # Menu Bar and its submenus
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1000, 18))
        self.menu_bar.setStyleSheet("""
                                        QWidget {
                                            font-size: 9pt;
                                        }
                                    """)
        self.setMenuBar(self.menu_bar)
        
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.setStyleSheet("""
                                        QWidget {
                                            font-size: 9pt;
                                        }
                                    """)
        
        # File menu in menu bar
        self.menuFile = QMenu(self.menu_bar)
        self.menuFile.setTitle("File")
        # File -> New
        self.actionNew = QAction(self)
        self.actionNew.setText("New")
        self.actionNew.setStatusTip("Create a new entry")
        self.actionNew.setShortcut("Ctrl+N")
        # File -> Open
        self.actionOpen = QAction(self)
        self.actionOpen.setText("Open")
        self.actionOpen.setStatusTip("Open an existing entry")
        self.actionOpen.setShortcut("Ctrl+O")
        # File -> Save
        self.actionSave = QAction(self)
        self.actionSave.setText("Save")
        self.actionSave.setStatusTip("Save entry")
        self.actionSave.setShortcut("Ctrl+S")
        # File -> Save As
        self.actionSave_As = QAction(self)
        self.actionSave_As.setText("Save As")
        self.actionSave_As.setStatusTip("Save entry as...")
        self.actionSave_As.setShortcut("Ctrl+Shift+S")
        # File -> Open Folder
        self.actionOpenFolder = QAction(self)
        self.actionOpenFolder.setText("Open Folder")
        self.actionOpenFolder.setStatusTip("Open a new folder in the file explorer")
        self.actionOpenFolder.setShortcut("Ctrl+Shift+O")
        # Adding Actions to File menu
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpenFolder)
        
        # View menu in menu bar
        self.menuView = QMenu(self.menu_bar)
        self.menuView.setTitle("View")
        # View -> Editor Only
        self.actionEditor_Only = QAction(self)
        self.actionEditor_Only.setText("Editor Only")
        self.actionEditor_Only.setStatusTip("View Editor Only")
        self.actionEditor_Only.setShortcut("Ctrl+1")
        # View -> Viewer Only
        self.actionViewer_Only = QAction(self)
        self.actionViewer_Only.setText("Viewer Only")
        self.actionViewer_Only.setStatusTip("Viewer Only")
        self.actionViewer_Only.setShortcut("Ctrl+2")
        # View -> Split View
        self.actionSplit_View = QAction(self)
        self.actionSplit_View.setText("Split View")
        self.actionSplit_View.setStatusTip("Vertical Split Between Editor and Viewer")
        self.actionSplit_View.setShortcut("Ctrl+3")
        # View -> Toggle Explorer
        self.toggle_explorer_action = QAction("Toggle Explorer", self)
        self.toggle_explorer_action.setShortcut("Ctrl+E")
        # View -> Toggle Split (for switching orientation)
        self.actionToggleLayout = QAction(self)
        self.actionToggleLayout.setText("Switch to Vertical Split")  # Default text
        self.actionToggleLayout.setStatusTip("Toggle between horizontal and vertical layouts")
        self.actionToggleLayout.setShortcut("Ctrl+R")
        # Adding Actions to View menu
        self.menuView.addAction(self.actionEditor_Only)
        self.menuView.addAction(self.actionViewer_Only)
        self.menuView.addAction(self.actionSplit_View)
        self.menuView.addAction(self.actionToggleLayout)
        self.menuView.addSeparator()
        self.menuView.addAction(self.toggle_explorer_action)
        
        # Edit menu in menu bar
        self.menuEdit = QMenu(self.menu_bar)
        self.menuEdit.setTitle("Edit")
        # Edit -> Undo
        self.actionUndo = QAction(self)
        self.actionUndo.setText("Undo")
        self.actionUndo.setShortcut("Ctrl+Z")
        # Edit -> Redo
        self.actionRedo = QAction(self)
        self.actionRedo.setText("Redo")
        self.actionRedo.setShortcut("Ctrl+Shift+Z")
        # Edit -> Cut
        self.actionCut = QAction(self)
        self.actionCut.setText("Cut")
        self.actionCut.setShortcut("Ctrl+X")
        # Edit -> Copy
        self.actionCopy = QAction(self)
        self.actionCopy.setText("Copy")
        self.actionCopy.setShortcut("Ctrl+C")
        # Edit -> Paste
        self.actionPaste = QAction(self)
        self.actionPaste.setText("Paste")
        self.actionPaste.setShortcut("Ctrl+V")
        # Edit -> Select All
        self.actionSelectAll = QAction(self)
        self.actionSelectAll.setText("Select All")
        self.actionSelectAll.setShortcut("Ctrl+A")
        # Adding Actions to Edit menu
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSelectAll)
        
        # Adding menus to the menu bar
        self.menu_bar.addAction(self.menuFile.menuAction())
        self.menu_bar.addAction(self.menuEdit.menuAction())
        self.menu_bar.addAction(self.menuView.menuAction())
        
    def init_config_signals(self):
        self.md_editor.textChanged.connect(self.markdown_update)
        
        self.actionNew.triggered.connect(self.new_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionSave_As.triggered.connect(self.save_as_file)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionOpenFolder.triggered.connect(self.open_folder)
        
        self.actionUndo.triggered.connect(self.md_editor.undo)
        self.actionRedo.triggered.connect(self.md_editor.redo)
        self.actionCut.triggered.connect(self.md_editor.cut)
        self.actionCopy.triggered.connect(self.md_editor.copy)
        self.actionPaste.triggered.connect(self.md_editor.paste)
        
        self.actionSelectAll.triggered.connect(self.md_editor.selectAll)
        
        self.actionEditor_Only.triggered.connect(self.show_editor_only)
        self.actionViewer_Only.triggered.connect(self.show_viewer_only)
        self.actionSplit_View.triggered.connect(self.show_split_view)
        self.toggle_explorer_action.triggered.connect(self.toggle_file_explorer)
        self.actionToggleLayout.triggered.connect(self.toggle_layout)
        
        self.file_explorer.doubleClicked.connect(self.open_file_from_explorer)

    def toggle_layout(self):
        if self.editor_viewer_splitter.orientation() == QtCore.Qt.Orientation.Horizontal:
            self.editor_viewer_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)  # Switch to vertical layout
            self.actionToggleLayout.setText("Switch to Horizontal Split")  # Update menu text
        else:
            self.editor_viewer_splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)  # Switch back to horizontal
            self.actionToggleLayout.setText("Switch to Vertical Split")  # Update menu text

        self.editor_viewer_splitter.setSizes([500, 500])  # Adjust sizes for balance (optional)
        
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", os.path.dirname(__file__))
        if folder_path:
            self.file_model.setRootPath(folder_path)
            self.file_explorer.setRootIndex(self.file_model.index(folder_path))
        
    def toggle_file_explorer(self):
        if self.file_explorer.isVisible():
            self.file_explorer.hide()
        else:
            self.file_explorer.show()
    
    def markdown_update(self):
        self.md_viewer.setMarkdown(self.md_editor.toPlainText())
        
    def new_file(self):
        # Clear the editor and viewer
        self.md_editor.clear()
        self.md_viewer.clear()
        
        # Reset the file path and window title
        self.current_file_path = None
        self.setWindowTitle("Untitled - ThoughtForge")
        
    def save_file(self):
        if self.current_file_path:
            try:
                with open(self.current_file_path, "w", encoding="utf-8") as file:
                    file.write(self.md_editor.toPlainText())
                self.statusbar.showMessage(f"File saved: {self.current_file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
        else:
            self.save_as_file()
        
    def save_as_file(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if fileName:
            if not fileName.endswith(".md"):
                fileName += ".md"
            
            try:
                with open(fileName, "w", encoding="utf-8") as file:
                    file.write(self.md_editor.toPlainText())
                
                self.current_file_path = fileName
                self.setWindowTitle(f"{fileName} - ThoughtForge")
                self.statusbar.showMessage(f"File saved successfully: {fileName}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
        
    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if fileName:
            self.load_file(fileName)
                
    def open_file_from_explorer(self, index):
        file_path = self.file_model.filePath(index)
        if file_path.endswith(".md"):
            self.load_file(file_path)
        
    def load_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            self.md_editor.setPlainText(content)
            self.current_file_path = file_path
            self.setWindowTitle(f"{file_path} - ThoughtForge")
            self.statusbar.showMessage(f"File opened: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
                
    def show_editor_only(self):
        self.md_editor.show()
        self.md_viewer.hide()
        
    def show_viewer_only(self):
        self.md_editor.hide()
        self.md_viewer.show()
        
    def show_split_view(self):
        self.md_editor.show()
        self.md_viewer.show()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
                        QWidget {
                            font-size: 14px;
                        }
                      """)
    win = MarkdownEditor()
    win.show()
    sys.exit(app.exec())
    
if hasattr(sys, "frozen"):
    sys.version_info = __version__