from pathlib import Path

import numpy as np

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QFileDialog, QTreeWidget, QVBoxLayout, QTreeWidgetItem, QCheckBox
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from OpenGL.GL import *

from .primitives import Entity, Polyline

class ModelSpaceWidget(QOpenGLWidget):
    """
    The Grafikon model space widget. A subclass of QOpenGLWidget.

    Attributes
    ----------
    self.npLines : numpy.ndarray of floats, shape of (num of lines, 2, 2).
        The array that contains the lines being drawn in OpenGL.
    """

    def __init__(self):
        super().__init__()
        self.npLines = np.array(
            [[[-0.1, 0], [0.1, 0]], [[0, -0.1], [0, 0.1]]]
        )  # Set initial non-empty line set to show displays is working

    def initializeGL(self):
        """
        Set initial OpenGL settings.

        Re-implemented from base class. Called when widget created.
        """
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Set background color to black
        glColor3f(1.0, 1.0, 1.0)  # Set default drawing color to white

    def resizeGL(self, w=None, h=None):
        """
        Resize the widget.

        Re-implemented from base class. Called when resized or parent widgets resize.

        Paramters
        ---------
        w : int
            New width for the model space. Measured in Pixels.
        h : int
            New height for the model space. Measured in Pixels.
        """
        if w is None or h is None:
            w = self.width()
            h = self.height()
        glViewport(0, 0, w, h)  # Update the viewport to the new widget size

        # Set up an orthographic projection with the origin at the center
        # and overall dimentions to fit the minimum and maximum drawn values
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        allPoints = np.vstack(self.npLines)
        minX = np.min(allPoints[:, 0]) - 0.5
        maxX = np.max(allPoints[:, 0]) + 0.5
        minY = np.min(allPoints[:, 1]) - 0.5
        maxY = np.max(allPoints[:, 1]) + 0.5

        dw = float(maxX) - float(minX)

        # glOrtho(500, 600, 500, 600, -1, 1)
        glOrtho(float(minX), float(maxX), float(minY), float(maxY), -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """
        Draw to the model space widget.

        Re-implemented from base class. Called whenever the drawn content changes.
        """
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Draw a numpy.ndarray of floats, shape of (num of lines, 2, 2).
            glEnableClientState(GL_VERTEX_ARRAY)
            for line in self.npLines:
                glVertexPointer(2, GL_FLOAT, 0, line)
                glDrawArrays(GL_LINE_STRIP, 0, len(line))
            glDisableClientState(GL_VERTEX_ARRAY)
        except Exception as e:
            print("GL error: ", e)

    def update_drawing(self, entities: list[Polyline]):
            # print(entities)

            lines = [[[point.coordinate.x, point.coordinate.y] for point in polyline.points] for polyline in entities]
            # print(lines)
                 
                
            self.npLines = np.asarray(lines)
            # Make sure we have the OpenGL context
            self.makeCurrent()
    
            # Update the projection based on new data
            self.resizeGL()
            # Schedule a repaint
            self.update()
            # Release the context
            self.doneCurrent()


class MainGUI(QMainWindow):
    def __init__(self, appState):
            super().__init__()
            self.appState = appState
            self.load_ui()
            
            self.appState.set_ui_callback("MODEL", "layer_tree", self.update_layer_tree_ui)


            self.glWidget = ModelSpaceWidget()
            layout = QVBoxLayout()
            layout.addWidget(self.glWidget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.ui.Placeholder_Model.setLayout(layout)
    
            self.appState.set_ui_callback("MODEL", "visual_space_draw", self.glWidget.update_drawing)

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

    def update_layer_tree_ui(self, nestedLayers: list): #this will probably need to be exectuted in different ways, and also is currently only a tree heirarchy update not updating other aspects.
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

