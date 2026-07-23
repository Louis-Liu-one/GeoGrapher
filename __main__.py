'''主程序，运行GeoGrapher。
'''

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from .GrapherCentralWidget import GrapherCentralWidget


def _main():
    '''运行GeoGrapher。
    '''
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = QMainWindow()
    window.setWindowTitle('GeoGrapher')
    grapher = GrapherCentralWidget(parent=window)
    window.setCentralWidget(grapher)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    _main()
