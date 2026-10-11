import sys
from PySide6.QtWidgets import QApplication

from grafikon.state import GrafikonState, LayerTree, Model
from grafikon.gui import MainGUI

model = Model({}, LayerTree())
appState = GrafikonState({}, model, {})
app = QApplication(sys.argv)
appGui = MainGUI(appState)
sys.exit(app.exec())