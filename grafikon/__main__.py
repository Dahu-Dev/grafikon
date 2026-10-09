import sys
from PySide6.QtWidgets import QApplication

from grafikon.state import GrafikonState 
from grafikon.gui import MainGUI

appState = GrafikonState()
app = QApplication(sys.argv)
appGui = MainGUI(appState)
sys.exit(app.exec())