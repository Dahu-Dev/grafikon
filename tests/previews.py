import sys
from PySide6.QtWidgets import QApplication

from grafikon.state import GrafikonState, LayerTree, Model
from grafikon.gui import MainGUI
from grafikon.primitives import Coordinate, Point, Polyline

def manual_pre_draw_polyline_on_root():
    model = Model({}, LayerTree())
    appState = GrafikonState({}, model, {})

    model.draw_polyline((
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
    ), "active")
    
    app = QApplication(sys.argv)
    appGui = MainGUI(appState)
    sys.exit(app.exec())

manual_pre_draw_polyline_on_root()