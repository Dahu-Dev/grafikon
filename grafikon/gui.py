from pathlib import Path

import numpy as np

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QFileDialog, QVBoxLayout, QTreeWidgetItem, QCheckBox
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *

class MainGUI(QMainWindow):
    def __init__(self, appState):
            super().__init__()
            self.programState = appState
            self.load_ui()
            self.show()
    
    def load_ui(self, relPath: Path = Path("main.ui")):
            """Load the pyside6-designer output .ui file for the main window"""
            uiFileName = Path(__file__).resolve().parent / relPath
            uiFile = QFile(uiFileName)
            if not uiFile.open(QIODevice.ReadOnly):
                raise FileNotFoundError(f"Cannot open {uiFileName}: {uiFile.errorString()}")
            loader = QUiLoader()
            self.ui = loader.load(uiFile, self)
            uiFile.close()
            if not self.ui:
                raise FileNotFoundError(loader.errorString())

    def show(self):
         self.ui.show()