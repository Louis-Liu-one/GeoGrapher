'''GeoGrapher点图元
'''

from PyQt5.QtWidgets import QStyle, QApplication
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF

from .GeoGraphItem import GeoGraphItem
from .GeoGraphPointLabel import GeoGraphPointLabel
from .GeoItems import GeoPoint, GeoIntersection

__all__ = ['GeoGraphPoint']


class GeoGraphPoint(QGraphicsEllipseItem, GeoGraphItem):
    '''点图元类，也是其它点图元类的基类。
    '''

    def __init__(self):
        '''初始化点图元。
        '''
        super().__init__()
        self._penFinal = QPen(QColor(0, 0, 0), 2.)
        self._penSelected = QPen(QColor(128, 128, 128), 2.)
        self._pens = [self._penFinal, self._penSelected]
        self.setRect(-5., -5., 10., 10.)
        self.setPen(self._penFinal)
        self.setBrush(QBrush(QColor(230, 230, 230)))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.isFree = True       # 是否为自由点
        self.onPath = None       # 所在路径
        self.isIntersec = False  # 是否为交点
        self.instance = GeoPoint(self.x, self.y)  # 基础图元
        self.ancestors = [self]
        self.typePatterns = [[GeoGraphPoint],]
        self.label = GeoGraphPointLabel(self)  # 点标签
        self._labelZoomScaleFirstChange = True  # 点标签是否未与场景缩放比例同步

    def _addFirstMaster(self, master):
        '''为本图元添加第一个父图元。
        '''
        if isinstance(master, GeoGraphPoint):
            self._copyPointToSelf(master)
        else:
            self.onPath = master
            self.instance.addMaster(master.instance)
            self.isFree = False
            self.setPos(self._newPosition(master._mousePos()))
        self._mastersHaveNotUpdated = self._masters.copy()

    def _copyPointToSelf(self, point):
        '''将给定点图元复制到自己。仅在初始化时调用。

        :param point: 给定的点图元。
        :type point: GeoGrapher.GeoItems.GeoGraphPoint.GeoGraphPoint
        '''
        point.updateSelfPosition()
        self.setPos(point.pos())
        point.scene().removeItem(point)
        self.ancestors = point.ancestors.copy()
        self.onPath = point.onPath
        self.isFree = point.isFree
        self._masters = []
        point.removeChild(self)
        if point.isIntersec:  # 是交点
            self.setFlag(self.ItemIsMovable, False)
            self.setFlag(self.ItemSendsGeometryChanges, False)
            self.isIntersec = True
            self.instance = GeoIntersection()
            for master in point.masters():
                self.addMaster(master)
        elif point.onPath is not None:  # 是路径上的点
            self.instance = GeoPoint(self.x, self.y)
            self.addMaster(point.onPath)
        else:  # 是自由点
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
        仅被`self.itemChange()`调用。

        :param pos: 鼠标位置。
        :type pos: PyQt5.QtCore.QPointF
        :returns: 返回的点位置。
        :rtype: PyQt5.QtCore.QPointF
        '''
        if not self.isFree:  # 路径上
            tempPoint = GeoPoint(pos.x, pos.y)
            tempPoint.addMaster(self.onPath.instance)
            self.onPath.instance.removeChild(tempPoint)
            x, y = tempPoint.pos()
            return QPointF(float(x), float(y))
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
        '''移动点时调用。参见`self._newPosition()`。
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
        rect.setHeight(self.rect().height() / zoomChange)  # 更新大小
        rect.moveCenter(QPointF(0., 0.))                   # 更新位置
        self.setRect(rect)
        if self._labelZoomScaleFirstChange:  # 当初次调用时将标签缩放比例与场景同步
            self._labelZoomScaleFirstChange = False
            self.label.zoomScaleChanged(zoomChange)
