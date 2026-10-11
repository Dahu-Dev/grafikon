from pathlib import Path

import numpy as np

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QFileDialog, QTreeWidget, QVBoxLayout, QTreeWidgetItem, QCheckBox
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *

class MainGUI(QMainWindow):
    def __init__(self, appState):
            super().__init__()
            self.appState = appState
            self.load_ui()
            
            self.appState.set_ui_callback("MODEL", "layer_tree", self.update_layer_tree_ui)

            self.appState.sync()
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

    def update_layer_tree_ui(self, nestedLayers: list):
        self.ui.Tree_Layers.clear()

        def populateNode(parentContainer, nodes):
            for node in nodes:
                if isinstance(node, list) and len(node) >= 3:
                    label = str(node[1])
                    children = node[2]
                    item = QTreeWidgetItem([label])

                    if isinstance(parentContainer, QTreeWidget):
                        parentContainer.addTopLevelItem(item)
                    else:
                        parentContainer.addChild(item)

                    if children:
                        populateNode(item, children)

        if isinstance(nestedLayers, list) and len(nestedLayers) >= 3 and not (nestedLayers[0] and isinstance(nestedLayers[0], list)):
            root_item = QTreeWidgetItem([str(nestedLayers[1])])
            self.ui.Tree_Layers.addTopLevelItem(root_item)
            if nestedLayers[2]:
                populateNode(root_item, nestedLayers[2])
        else:
            populateNode(self.ui.Tree_Layers, nestedLayers)

    def show(self):
         self.ui.show()