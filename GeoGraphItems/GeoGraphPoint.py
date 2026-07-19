'''GeoGrapher点图元
'''

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .GeoGraphItem import GeoGraphPathItem

from PyQt5.QtWidgets import QStyle, QApplication, QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF

from .GeoGraphItem import GeoGraphItem
from .GeoGraphPointLabel import GeoGraphPointLabel
from .Core import (
    DecFloat, GeoPoint, GeoSegment, GeoIntersection, PointPos, footPoint)

__all__ = ['GeoGraphPoint']


class GeoGraphPoint(QGraphicsEllipseItem, GeoGraphItem):
    '''点图元类，也是其它点图元类的基类。
    '''
    ATTRIBUTES_INFO = {
        **GeoGraphItem.ATTRIBUTES_INFO,
        'pointSize': {
            'type': float, 'title': 'Size',
            'min': 1, 'max': 36, 'step': 1,
            'getter': lambda self: self.pointSize(),
            'setter': lambda self, value: self.setPointSize(value),
        },
        'pointBorderColor': {
            'type': 'color', 'title': 'Border Color',
            'getter': lambda self: self.drawColor(),
            'setter': lambda self, value: self.setDrawColor(value),
        },
        'pointFillColor': {
            'type': 'color', 'title': 'Fill Color',
            'getter': lambda self: self.fillColor(),
            'setter': lambda self, value: self.setFillColor(value),
        },
        'pointLabelText': {
            'group': 'Label', 'type': str, 'title': 'Text',
            'getter': lambda self: self._label.toPlainText(),
            'setter': lambda self, value: self._label.setLabel(value),
        },
        'pointLabelAngle': {
            'group': 'Label', 'type': 'angle', 'title': 'Angle',
            'getter': lambda self: self._label.labelAngle(),
            'setter': lambda self, value: self._label.setLabelAngle(value),
        },
        'pointLabelDistance': {
            'group': 'Label', 'type': float, 'title': 'Distance',
            'min': 5, 'max': 100, 'step': 2,
            'getter': lambda self: self._label.labelDistance(),
            'setter': lambda self, value: self._label.setLabelDistance(value),
        },
    }

    def __init__(self):
        '''初始化点图元。
        '''
        super().__init__()
        self._penFinal = QPen(QColor('#000000'), 2.)
        self._penSelected = QPen(QColor('#808080'), 2.)
        self._pens = [self._penFinal, self._penSelected]
        self._pointSize = 12.
        self._drawColor = QColor('#000000')
        self._fillColor = QColor('#e6e6e6')
        self.setPointSize(self._pointSize)
        self.setPen(self._penFinal)
        self.setFillColor(self._fillColor)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.isUpdatable: bool = True
        self.isFree: bool = True                     # 是否为自由点
        self.onPath: GeoGraphPathItem | None = None  # 所在路径
        self.isIntersec: bool = False                # 是否为交点
        self.instance = GeoPoint(self.x, self.y)     # 基础图元
        self.ancestors = set()
        self.typePatterns = {(GeoGraphPoint,)}
        self._label = GeoGraphPointLabel(self)  # 点标签

    def __str__(self):
        '''返回点图元的标识字符串。
        '''
        return f'Point {self._label.toPlainText()}'

    def shortIdentifier(self):
        '''返回点图元的简短标识字符串。
        '''
        return self._label.toPlainText()

    def _addFirstMaster(self, master: GeoGraphItem):
        '''为本图元添加第一个父图元。
        '''
        if isinstance(master, GeoGraphPoint):
            self._copyPointToSelf(master)
            self.updateSelfPosition()
        else:  # 路径上的点
            self.onPath = master
            master.addChild(self)
            self._masters.append(master)
            self.instance.addMaster(master.instance)
            self.isFree = False
            self.setPos(self._newPosition(master._mousePos()))
        self._mastersHaveNotUpdated = set(self._masters)

    def _copyPointToSelf(self, point: GeoGraphPoint):
        '''将给定点图元复制到自己。仅在初始化时调用。

        :param point: 给定的点图元。
        '''
        self.setPos(point.pos())
        point.removeChild(self)
        point.scene().removeItem(point)
        self.ancestors = point.ancestors.copy()
        self.onPath = point.onPath
        self.isFree = point.isFree
        self._masters = []
        if point.isIntersec:  # 是交点
            self.setFlag(self.ItemIsMovable, False)
            self.setFlag(self.ItemSendsGeometryChanges, False)
            self.isUpdatable = False
            self.isIntersec = True
            self.instance = GeoIntersection()
            for master in point.masters():
                self.addMaster(master)
        elif point.onPath is not None:  # 是路径上的点
            self.instance = GeoPoint(self.x, self.y)
            self.addMaster(point.onPath)
        else:  # 是自由点
            self.ancestors = set()

    def paint(self, painter, option, widget=None):
        '''绘制点图元。自动对点的选中状态进行处理。
        '''
        # 根据选中状态设置画笔
        if option.state & QStyle.State_Selected:
            option.state = QStyle.State_None
            self.setPen(self._penSelected)
        else:
            self.setPen(self._penFinal)
        super().paint(painter, option, widget)

    def _newPosition(self, pos: QPointF) -> QPointF:
        '''根据鼠标移动计算点图元的实际位置。
        若点在路径上，则返回鼠标位置在路径上的投影坐标；
        若点为自由点，则返回网格吸附后的坐标。
        仅被`self.itemChange()`调用。

        :param pos: 鼠标位置。
        :returns: 返回的点位置。
        '''
        if not self.isFree:  # 路径上
            ins = self.onPath.instance
            poss = PointPos(DecFloat(pos.x()), DecFloat(pos.y()))
            fpos = footPoint(poss, ins.abc()) \
                if isinstance(ins, GeoSegment) \
                else footPoint(poss, ins.o().cpos(), ins.r())
            return QPointF(float(fpos.x), float(fpos.y))
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
        super().updateSelfPosition()
        if not self.isFree:  # 仅交点需更新
            x, y = self.instance.pos()
            if not x.is_nan() and not y.is_nan():
                self.setUndefined(False)  # 设为已定义
                self.setPos(float(x), float(y))
            else:
                self.setUndefined(True)   # 设为未定义

    def onAddingSelfToScene(self):
        '''在场景中添加的同时初始化标签。子类可覆盖此方法。
        '''
        self._label.setLabel()  # 初始化标签

    def onRemovingSelfFromScene(self):
        '''在场景中删除时，同时在管理器中删除点图元标签。子类可覆盖此方法。
        '''
        self._label.pointLabelsManager.removeLabel(
            self._label.toPlainText())

    def itemChange(self, change, value):
        '''移动点时调用。参见`self._newPosition()`。
        '''
        if self.scene() \
                and QApplication.mouseButtons() == Qt.LeftButton \
                and change == self.ItemPositionChange:
            return self._newPosition(value)
        return super().itemChange(change, value)

    def pointSize(self) -> float:
        '''返回点的大小。
        '''
        return self._pointSize

    def setPointSize(self, size: float):
        '''设置点的大小。仅在初始化时调用。
        '''
        self._pointSize = size
        self.setRect(-size / 2, -size / 2, size, size)

    def drawColor(self) -> QColor:
        '''返回点的描边颜色。
        '''
        return self._drawColor

    def setDrawColor(self, color: QColor):
        '''设置点的描边颜色。
        '''
        self._drawColor = color
        self._penFinal.setColor(color)
        self.update()  # 更新图元以应用新的画笔颜色

    def fillColor(self) -> QColor:
        '''返回点的填充颜色。
        '''
        return self._fillColor

    def setFillColor(self, color: QColor):
        '''设置点的填充颜色。
        '''
        self._fillColor = color
        self.setBrush(QBrush(color))
