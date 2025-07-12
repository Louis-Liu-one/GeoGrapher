
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from .GeoGridGraph import GeoGridGraph


def _main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    gridGraph = GeoGridGraph(window)   #
    window.setCentralWidget(gridGraph)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    _main()
