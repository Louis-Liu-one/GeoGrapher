'''GeoGrapher绘制场景
'''

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QPainter
    from PySide6.QtCore import QPointF, QRect, QRectF
    from .GeoGraphView import GeoGraphView

import collections

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import QLine

from .GeoGraphItems.GeoGraphItem import GeoGraphItem, GeoGraphPathItem
from .GeoGraphItems.GeoGraphPoint import GeoGraphPoint
from .GeoGraphItems.GeoGraphCircle import GeoGraphCircle
from .GeoGraphItems.GeoGraphIntersection import GeoGraphIntersection
from .GeoGraphItems.GeoGraphVariable import GeoGraphIsecNoVar
from .GeoGraphItems.GeoPointLabelsManager import GeoPointLabelsManager
from .GeoGraphItems.Core import (
    DecFloat, PointPos, intersec, distanceTo, GeoItemsManager)


__all__ = ['GeoGraphScene']


class GeoGraphScene(QGraphicsScene):
    '''GeoGrapher绘制场景。使用方法与`QGraphicsScene`基本相同。
    '''

    def __init__(
            self, parent=None,
            darkGridSize=128, darkPenColor='#c0c0c0', darkPenWidth=1.2,
            lightGridSize=32, lightPenColor='#d0d0d0', lightPenWidth=.5,
            backgroundColor='#f1f1f1'):
        '''初始化场景。

        :param parent: 父控件。
        :param darkGridSize: 深色网格大小。
        :param darkPenColor: 深色网格颜色。
        :param darkPenWidth: 深色网格粗细。
        :param lightGridSize: 浅色网格大小。
        :param lightPenColor: 浅色网格颜色。
        :param lightPenWidth: 浅色网格粗细。
        :param backgroundColor: 背景颜色。
        '''
        super().__init__(parent)
        self.lightGridSize, self.darkGridSize = lightGridSize, darkGridSize
        self.zoomScale = 1.        # 当前放缩比例
        self.tempScale = 1.        # 缓存放缩比例，用于管理网格宽度
        self.itemsManager = GeoItemsManager()  # 统一管理基础图元
        self.pointLabelsManager = GeoPointLabelsManager()  # 点图元标签
        self._penDark = QPen(QColor(darkPenColor), darkPenWidth)     # 深色画笔
        self._penLight = QPen(QColor(lightPenColor), lightPenWidth)  # 浅色画笔
        self.setBackgroundBrush(QColor(backgroundColor))

    def views(self) -> list[GeoGraphView]:
        '''获取场景所在的所有视图。
        '''
        return super().views()

    def drawBackground(self, painter: QPainter, rect: QRect | QRectF):
        '''绘制背景网格。
        '''
        super().drawBackground(painter, rect)
        left = int(rect.left()) - int(rect.left()) % self.lightGridSize
        top = int(rect.top()) - int(rect.top()) % self.lightGridSize
        right, bottom = int(rect.right()), int(rect.bottom())
        linesDark, linesLight = [], []
        for i in range(top, bottom, self.lightGridSize):
            (linesLight if i % self.darkGridSize
                else linesDark).append(QLine(left, i, right, i))
        for i in range(left, right, self.lightGridSize):
            (linesLight if i % self.darkGridSize
                else linesDark).append(QLine(i, bottom, i, top))
        painter.setPen(self._penLight)
        if linesLight:
            painter.drawLines(linesLight)
        painter.setPen(self._penDark)
        if linesDark:
            painter.drawLines(linesDark)

    def zoomScaleChanged(self, zoomChange: float):
        '''放缩比例变化。

        :param zoomChange: 新放缩比例与原放缩比例的比值。
        '''
        # 更新网格画笔宽度
        self._penDark.setWidthF(
            self._penDark.widthF() / zoomChange)
        self._penLight.setWidthF(
            self._penLight.widthF() / zoomChange)
        self.zoomScale *= zoomChange
        self.tempScale *= zoomChange
        # 更新网格宽度
        while self.tempScale >= 2 and self.lightGridSize % 2 == 0:
            self.tempScale /= 2
            self.lightGridSize //= 2
            self.darkGridSize //= 2
        while self.tempScale <= .5:
            self.tempScale *= 2
            self.lightGridSize *= 2
            self.darkGridSize *= 2
        for item in self.items():
            if isinstance(item, GeoGraphItem):
                item.zoomScaleChanged(zoomChange)

    def createPointAt(self, scenePos: QPointF) -> GeoGraphPoint:
        '''在指定坐标处创建一个点。
        自动判断该点是否为自由点、一路径上的点或两路径的交点。

        :param scenePos: 创建点的坐标，在场景坐标系下。
        :returns: 创建好的点。
        '''
        # 在指定坐标附近的图元
        items: list[GeoGraphItem] = [
            item for item in self.items(scenePos)
            if isinstance(item, GeoGraphItem) and item.isCreated]
        if len(items) and all(
                isinstance(item, GeoGraphPathItem) for item in items):
            # 若附近有两个及以上的路径图元
            if len(items) > 1:
                # 则创建前两个路径图元的交点
                point = self.createIntersecWithItems(scenePos, items)
            # 若附近仅一个路径图元
            else:
                # 则创建路径上的点
                point = GeoGraphPoint()
                point.addMaster(items[0])
        else:  # 否则创建自由点
            point = GeoGraphPoint()
            point.setPos(scenePos)
        point.isCreated = True
        self.addItem(point)
        point.updateSelfPosition()  # 更新点坐标
        return point

    def createIntersecWithItems(
            self, scenePos: QPointF,
            items: list[GeoGraphItem]) -> GeoGraphIntersection:
        '''以指定图元为路径在指定坐标处创建一个交点。
        自动判断该点的交点编号，使得该点距离指定坐标较近。

        :param scenePos: 用户点击处的坐标，在场景坐标系下。在该坐标附近创建交点。
        :param items: 取前两个元素为路径创建交点。
        :returns: 创建好的交点。
        '''
        if len(items) < 2:
            return
        point = GeoGraphIntersection()
        point.addMaster(items[0])
        point.addMaster(items[1])
        if isinstance(items[0], GeoGraphCircle) \
                or isinstance(items[1], GeoGraphCircle):
            poss = PointPos(DecFloat(scenePos.x()), DecFloat(scenePos.y()))
            if isinstance(items[0], GeoGraphCircle) \
                    and isinstance(items[1], GeoGraphCircle):
                circ1, circ2 = items[0].instance, items[1].instance
                pos1, pos2 = intersec(
                    circ1.o().cpos(), circ1.r(), circ2.o().cpos(), circ2.r())
            else:
                seg, circ = items[0].instance, items[1].instance
                if isinstance(items[0], GeoGraphCircle):
                    seg, circ = circ, seg
                pos1, pos2 = intersec(
                    seg.abc(), circ.o().cpos(), circ.r(),
                    seg.point1().cpos(), seg.point2().cpos())
            l1, l2 = distanceTo(poss, pos1), distanceTo(poss, pos2)
            var = GeoGraphIsecNoVar()
            var.set(1 if float(l1) < float(l2) else 2)  # 按照到两交点到距离自动判断交点编号
            point.addMaster(var)
        return point

    def addItem(self, item: GeoGraphItem):
        '''添加图元。
        '''
        super().addItem(item)
        item.zoomScaleChanged(self.zoomScale)     # 让图元适应当前缩放倍数
        item.onAddingSelfToScene()                # 调用图元的添加回调函数
        self.itemsManager.addItem(item.instance)  # 添加基础图元

    def removeItem(self, item: GeoGraphItem):
        '''删除图元，并递归删除其子图元。
        '''
        if item.instance is None:
            return  # 图元已经被删除
        super().removeItem(item)
        item.onRemovingSelfFromScene()
        item.isAvailable = False
        for master in item.masters():
            master.removeChild(item)  # 从所有父图元中删除图元
        self.itemsManager.removeItem(item.instance)  # 删除基础图元
        item.instance = None
        for child in item.children():
            self.removeItem(child)  # 递归删除子图元

    def updateItems(self, items: set[GeoGraphItem]):
        '''从给定的图元集合开始递归更新图元，保证每个图元实际上最多只会被计算一次。
        先将相关图元还原为更新前的准备状态，再更新图元。
        '''
        q = collections.deque()
        ancestors: set[GeoGraphItem] = set()
        for item in items:
            if item.isUpdatable and not item.isUndefined:
                q.append(item)
                ancestors.add(item)
        while q:  # 将相关图元全部还原为更新前的准备状态
            master: GeoGraphItem = q.popleft()
            for child in master.children():
                q.append(child)  # 广度优先遍历
            master.updateFromMasters()
            master.instance.update()
        for ancestor in ancestors:
            for child in ancestor.children():
                child.updatePosition(ancestor, ancestors)
