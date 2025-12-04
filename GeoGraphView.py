'''GeoGrapher绘制视图
'''

from PyQt5.QtWidgets import QApplication, QMenu, QAction
from PyQt5.QtWidgets import QGraphicsView, QGraphicsTextItem
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

from .GeoGraphItems.GeoGraphItem import GeoGraphPathItem
from .GeoGraphItems.GeoGraphPoint import GeoGraphPoint
from .GeoGraphItems.GeoGraphIntersection import GeoGraphIntersection
from .GeoGraphItems.GeoGraphCircle import GeoGraphCircle
from .GeoGraphItems.GeoGraphVariable import GeoGraphIsecNoVar
from .GeoGraphItems.Core import *
from .Constants import *

__all__ = ['GeoGraphView']


def _isAllInstance(items, class_):
    '''判断序列中是否全部是某类型的对象。
    '''
    return all([isinstance(item, class_) for item in items])


def _createdItemsFilter(items):
    '''筛选图元序列中已创建的图元。
    '''
    return [item for item in items if item.isCreated]


class GeoGraphView(QGraphicsView):
    '''GeoGrapher绘制视图。结合`GeoGrapher.GeoGridGraphScene`使用。
    使用方法与`PyQt5.QtWidgets.QGraphicsView`相同。
    '''

    def __init__(self, scene, parent=None):
        '''创建视图。参数与`PyQt5.QGraphicsView`相同。
        '''
        super().__init__(scene, parent)
        self.setDragMode(self.RubberBandDrag)
        self.setRenderHints(QPainter.HighQualityAntialiasing)
        self.setMouseTracking(True)
        self.mainMode = GeoMainMode.SELECT  # 主模式，默认为选择模式
        self.secondaryMode = None           # 次模式
        # 下列属性在绘制模式创建图元时使用
        self._drawModeSelectedItems = []  # 当前选择过的图元
        self._typePatterns = []           # 根据次模式决定图元的类型匹配
        self._creatingItem = None         # 当前正在创建的图元

    def mousePressEvent(self, event):
        '''按下鼠标时，若主模式为绘制模式，则创建图元或添加父图元。
        '''
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton \
                and self.mainMode == GeoMainMode.DRAW:
            self._drawModeMousePress(event.pos())

    def _drawModeMousePress(self, pos):
        '''当在绘制模式按下鼠标时，创建图元或添加父图元。

        :param pos: 鼠标点击的位置，在视图坐标系下。
        :type pos: PyQt5.QtCore.QPoint
        '''
        selectedItem = self.itemAt(pos)  # 选中的图元
        scenePos = self.mapToScene(pos)  # 转换为场景坐标系
        # 从未选择过图元，表明此次点击是第一次，要创建新图元
        if not self._drawModeSelectedItems:
            # 创建图元
            self._creatingItem = self.secondaryMode.value()
            self.scene().addItem(self._creatingItem)
            # 初始化图元的类型匹配
            self._typePatterns = self._creatingItem.typePatterns.copy()
        rawTypePatterns = self._typePatterns.copy()
        # 根据选中的图元类型筛选匹配的类型模式
        self._typePatterns = \
            self._creatingItem.typePatternsFilter(
                len(self._drawModeSelectedItems), type(selectedItem))
        createPointFlag = not self._typePatterns  # 是否需要创建新点
        # 若无匹配的类型模式
        if createPointFlag:
            # 此时需要创建一个点，筛选匹配点的类型模式
            self._typePatterns = \
                self._creatingItem.typePatternsFilter(
                    len(self._drawModeSelectedItems), GeoGraphPoint)
        if self._typePatterns:  # 匹配成功
            self._drawModeAddItem(                     # 添加
                self._createPointAt(scenePos)          # 创建的新点
                if createPointFlag else selectedItem)  # 或选中的图元为父图元
            # 若此次图元创建完成
            if len(self._typePatterns[0]) == len(self._drawModeSelectedItems):
                self._creatingItem.isCreated = True
                self._creatingItem.updateSelfPosition()
                # 初始化，以为下次创建作准备
                self._drawModeSelectedItems = []
                self._creatingItem = None
        else:  # 匹配失败，此次图元创建失败，重新初始化
            if self._creatingItem is not None:
                self.scene().removeItem(self._creatingItem)
                self._creatingItem = None
            self._drawModeSelectedItems = []

    def _drawModeAddItem(self, master):
        '''为当前在创建的图元添加父图元。

        :param master: 要添加的父图元。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        # 为在创建的图元添加父图元
        self._creatingItem.addMaster(master)
        # 添加至选择过的图元列表
        self._drawModeSelectedItems.append(master)

    def _createPointAt(self, scenePos):
        '''在指定坐标处创建一个点。
        自动判断该点是否为自由点、一路径上的点或两路径的交点。

        :param scenePos: 创建点的坐标，在场景坐标系下。
        :type scenePos: PyQt5.QtCore.QPointF
        :returns: 创建好的点。
        :rtype: GeoGrapher.GeoItems.GeoGraphPoint.GeoGraphPoint
        '''
        # 在指定坐标附近的图元
        items = _createdItemsFilter(self.items(self.mapFromScene(scenePos)))
        if len(items) and _isAllInstance(items, GeoGraphPathItem):
            # 若附近有两个及以上的路径图元
            if len(items) > 1 and _isAllInstance(items, GeoGraphPathItem):
                # 则创建前两个路径图元的交点
                point = self._createIntersecWithItems(scenePos, items)
            # 若附近仅一个路径图元
            elif isinstance(items[0], GeoGraphPathItem):
                # 则创建路径上的点
                point = GeoGraphPoint()
                point.addMaster(items[0])
        else:  # 否则创建自由点
            point = GeoGraphPoint()
            point.setPos(scenePos)
        point.isCreated = True
        self.scene().addItem(point)
        point.updateSelfPosition()  # 更新点坐标
        return point

    def _createIntersecWithItems(self, scenePos, items):
        '''以指定图元为路径在指定坐标处创建一个交点。
        自动判断该点的交点编号，使得该点距离指定坐标较近。

        :param scenePos: 创建交点的坐标，在场景坐标系下。
        :type scenePos: PyQt5.QtCore.QPointF
        :param items: 取前两个为交点的路径。
        :type items: list[GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem]
        :returns: 创建好的交点。
        :rtype: GeoGrapher.GeoItems.GeoGraphIntersection.GeoGraphIntersection
        '''
        point = GeoGraphIntersection()
        point.addMaster(items[0])
        point.addMaster(items[1])
        if isinstance(items[0], GeoGraphCircle) \
                or isinstance(items[1], GeoGraphCircle):
            seg, circ = items[0].instance, items[1].instance
            if isinstance(items[0], GeoGraphCircle):
                seg, circ = circ, seg
            pos1, pos2 = intersec(seg.abc(), circ.o().cpos(), circ.r())
            if not isLeftPoint(pos1, pos2):
                pos1, pos2 = pos2, pos1
            poss = PointPos(DecFloat(scenePos.x()), DecFloat(scenePos.y()))
            l1, l2 = distanceTo(poss, pos1), distanceTo(poss, pos2)
            var = GeoGraphIsecNoVar()
            var.set(1 if float(l1) < float(l2) else 2)  # 自动判断交点编号
            point.addMaster(var)
        return point

    def mouseReleaseEvent(self, event):
        '''松开鼠标时，更新图元。
        '''
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            # 若当前选中了可操作图元
            for item in self.scene().selectedItems():
                if item.isUpdatable and not item.isUndefined:
                    item.activelyUpdatePosition()  # 则递归更新图元

    def keyPressEvent(self, event):
        '''按下删除键时，删除选中图元。
        '''
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Backspace \
                and self.mainMode == GeoMainMode.SELECT \
                and not isinstance(
                    self.scene().focusItem(), QGraphicsTextItem):
            for item in self.scene().selectedItems():
                if not isinstance(item, QGraphicsTextItem):
                    self.scene().removeItem(item)
