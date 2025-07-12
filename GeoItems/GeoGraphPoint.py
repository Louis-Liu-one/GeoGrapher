'''GeoGrapher点图元
'''

from PyQt5.QtWidgets import QStyle, QApplication
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF

from .GeoGraphItem import GeoGraphItem
from .GeoBasicItems import GeoPoint, GeoIntersection

__all__ = ['GeoGraphPoint']


class GeoGraphPoint(QGraphicsEllipseItem, GeoGraphItem):
    '''点图元类，与其它点图元类的基类。
    '''

    def __init__(self, master=None):
        '''初始化点图元。

        :param master: 点图元的第一个父图元。若不提供，则图元为自由点。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        QGraphicsEllipseItem.__init__(self)
        GeoGraphItem.__init__(self, master)
        self._initStates()  # 初始化状态
        if isinstance(master, GeoGraphPoint):
            self._copyPointToSelf(master)
        elif master is not None:
            self.onPath = master
            self.instance = GeoPoint(master.instance, self.x, self.y)
            tempPoint = GeoPoint(
                master.instance,
                master._mousePos().x, master._mousePos().y)
            x, y = tempPoint.pos()
            self.setPos(float(x), float(y))
            self.isFree = False
        else:
            self._masters = []
            self.ancestors = [self]
        self._mastersHaveNotUpdated = self._masters.copy()

    def _initStates(self):
        '''初始化图元状态，设置画笔。
        '''
        self._penFinal = QPen(QColor('#000000'), 2.)
        self._penSelected = QPen(QColor('#808080'), 2.)
        self._pens = [self._penFinal, self._penSelected]
        self.setRect(-5., -5., 10., 10.)
        self.setPen(self._penFinal)
        self.setBrush(QBrush(QColor('#e6e6e6')))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.isFree = True       # 是否为自由点
        self.onPath = None       # 所在路径
        self.isIntersec = False  # 是否为交点
        self.instance = GeoPoint(x=self.x, y=self.y)  # 基础图元

    def _copyPointToSelf(self, point):
        '''将给定点图元复制到自己。仅在初始化时调用。

        :param point: 给定的点图元。
        :type point: GeoGrapher.GeoItems.GeoGraphPoint.GeoGraphPoint
        '''
        self.setPos(point.pos())
        point.scene().removeItem(point)
        self.ancestors = point.ancestors.copy()
        self.onPath = point.onPath
        self.isFree = point.isFree
        point.removeChild(self)
        if point.isIntersec:  # 是交点
            self.setFlag(self.ItemIsMovable, False)
            self.setFlag(self.ItemSendsGeometryChanges, False)
            self.isIntersec = True
            self.instance = GeoIntersection(point.instance)
            self._masters = point.masters().copy()
            for item in self._masters:
                item.addChild(self)
        elif point.onPath is not None:  # 是路径上的点
            self._masters = [point.onPath]
            point.onPath.addChild(self)
            self.instance = GeoPoint(
                self.onPath.instance, x=self.x, y=self.y)
        else:  # 是自由点
            self._masters = []
            self.ancestors = [self]

    def paint(self, painter, option, widget=None):
        '''绘制点图元。自动对点的选中状态进行处理。
        '''
        # 根据选中状态设置画笔
        if option.state & QStyle.State_Selected:
            option.state = QStyle.State_None
            self.setPen(self._penSelected)
        else:
            self.setPen(self._penFinal)
        self._checkAvailable()
        super().paint(painter, option, widget)

    def _newPosition(self, pos):
        '''根据鼠标移动返回点位置。
        若点在路径上，则返回鼠标位置在路径上的投影坐标；
        若点为自由点，则返回网格吸附后的坐标。
        仅被``self.itemChange()``调用。

        :param pos: 鼠标位置。
        '''
        if not self.isFree:  # 路径上
            tempPoint = GeoPoint(self.onPath.instance, x=pos.x, y=pos.y)
            return QPointF(float(tempPoint.x()), float(tempPoint.y()))
        # 自由点，开启网格吸附
        gridSize = self.scene().lightGridSize
        xGrid, yGrid = pos.x(), pos.y()
        # 若点到网格距离小于1/6的网格大小，则吸附到网格上
        if abs(gridSize / 2 - pos.x() % gridSize) > gridSize / 3:
            xGrid = round(pos.x() / gridSize) * gridSize
        if abs(gridSize / 2 - pos.y() % gridSize) > gridSize / 3:
            yGrid = round(pos.y() / gridSize) * gridSize
        return QPointF(xGrid, yGrid)

    def updateSelfPosition(self):
        '''更新自身位置。
        '''
        if not self.isFree:
            x, y = self.instance.pos()
            if not x.is_nan() and not y.is_nan():
                self.setPos(float(x), float(y))

    def itemChange(self, change, value):
        '''移动点时调用。参见``self._newPosition()``。
        '''
        if self.scene() \
                and QApplication.mouseButtons() == Qt.LeftButton \
                and change == self.ItemPositionChange:
            return self._newPosition(value)
        return super().itemChange(change, value)

    def zoomScaleChanged(self, zoomChange):
        '''视图放缩比例改变时更新点的大小以适应放缩比例。

        :param zoomChange: 放缩比例的变化比例，即新放缩比例比原放缩比例。
        :type zoomChange: float
        '''
        super().zoomScaleChanged(zoomChange)
        rect = self.rect()
        rect.setWidth(self.rect().width() / zoomChange)
        rect.setHeight(self.rect().height() / zoomChange)
        rect.moveCenter(QPointF(0., 0.))
        self.setRect(rect)


GeoGraphPoint.typePatterns = [[GeoGraphPoint],]
