
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QPushButton

from .GeoGraphView import GeoGraphView
from .GeoGraphScene import GeoGraphScene
from .Constants import *


class GeoGridGraph(QWidget):

    def __init__(
            self, parent=None, xAxis=(-10000, 10000), yAxis=(-10000, 10000)):
        super().__init__(parent)
        self._xAxis, self._yAxis = xAxis, yAxis
        self._xLen, self._yLen = xAxis[1] - xAxis[0], yAxis[1] - yAxis[0]
        self._zoomScale = 1.
        self._initWidgets()

    def _initWidgets(self):
        self._scene = GeoGraphScene(self)
        self._scene.setSceneRect(
            self._xAxis[0], self._yAxis[0], self._xLen, self._yLen)
        self._view = GeoGraphView(self._scene, self)
        zoomInButton = QPushButton('放大', self)     #
        zoomOutButton = QPushButton('缩小', self)    #
        zoomInButton.clicked.connect(self.zoomIn)   #
        zoomOutButton.clicked.connect(self.zoomOut) #
        selectModeButton = QPushButton('Select', self)
        pointModeButton = QPushButton('Point', self)
        segmentModeButton = QPushButton('Segment', self)
        circleModeButton = QPushButton('Circle', self)
        isecModeButton = QPushButton('Intersection', self)
        selectModeButton.clicked.connect(self._mainModeChanged)
        pointModeButton.clicked.connect(self._secondaryModeChanged)
        segmentModeButton.clicked.connect(self._secondaryModeChanged)
        circleModeButton.clicked.connect(self._secondaryModeChanged)
        isecModeButton.clicked.connect(self._secondaryModeChanged)
        zoomLayout = QHBoxLayout()
        zoomLayout.addWidget(zoomInButton)
        zoomLayout.addWidget(zoomOutButton)
        modeLayout = QHBoxLayout()
        modeLayout.addWidget(selectModeButton)
        modeLayout.addWidget(pointModeButton)
        modeLayout.addWidget(segmentModeButton)
        modeLayout.addWidget(circleModeButton)
        modeLayout.addWidget(isecModeButton)
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self._view)
        mainLayout.addLayout(zoomLayout)
        mainLayout.addLayout(modeLayout)
        self.setLayout(mainLayout)

    def zoomIn(self):
        if self._zoomScale <= 10.:
            self._zoomScaleChanged(1.25)

    def zoomOut(self):
        if self._zoomScale >= .1:
            self._zoomScaleChanged(.8)

    def _zoomScaleChanged(self, zoomChange):
        self._view.scale(zoomChange, zoomChange)
        self._zoomScale *= zoomChange
        self._scene.zoomScaleChanged(zoomChange)

    def _mainModeChanged(self):
        self._view.mainMode = mainModes[self.sender().text()]

    def _secondaryModeChanged(self):
        self._view.mainMode = GeoMainMode.DRAW
        self._view.secondaryMode = drawModes[self.sender().text()]
