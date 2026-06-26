'''GeoGrapher绘制视图
'''

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import QPoint, QPointF
    from .Constants import GeoSecondaryMode
    from .GeoGraphScene import GeoGraphScene
    from .GeoGraphItems.GeoGraphItem import GeoGraphItem

import collections

from PyQt5.QtWidgets import QGraphicsView, QGraphicsTextItem
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

from .GeoGraphItems.GeoGraphItem import GeoGraphPathItem
from .GeoGraphItems.GeoGraphPoint import GeoGraphPoint
from .GeoGraphItems.GeoGraphIntersection import GeoGraphIntersection
from .GeoGraphItems.GeoGraphCircle import GeoGraphCircle
from .GeoGraphItems.GeoGraphVariable import GeoGraphVariable, GeoGraphIsecNoVar
from .GeoGraphItems.Interfaces.ItemAttributesSetter import \
    ItemAttributesSetterDialog
from .GeoGraphItems.Core import DecFloat, PointPos, intersec, distanceTo
from .Constants import GeoMainMode

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
    '''GeoGrapher绘制视图。结合`GeoGrapher.GeoGraphScene`使用。
    使用方法与`PyQt5.QtWidgets.QGraphicsView`相同。
    '''

    def __init__(self, scene: GeoGraphScene, parent: QWidget | None = None):
        '''创建视图。参数与`PyQt5.QGraphicsView`相同。
        '''
        super().__init__(scene, parent)
        self.setDragMode(self.RubberBandDrag)
        self.setRenderHints(QPainter.HighQualityAntialiasing)
        self.setMouseTracking(True)
        self.mainMode: GeoMainMode = GeoMainMode.SELECT  # 主模式，默认为选择模式
        self.secondaryMode: GeoSecondaryMode = None      # 次模式
        # 下列属性在绘制模式创建图元时使用
        self._drawModeSelectedItems: list[GeoGraphItem] = []  # 当前选择过的图元
        self._typePatterns: list[tuple[type]] = []            # 根据次模式决定图元的类型匹配
        self._creatingItem: GeoGraphItem = None               # 当前正在创建的图元
        self._itemWithCurrentAttributesDialog: \
            GeoGraphItem = None                # 当前正在设置属性的图元
        self._itemAttributesSetterDialog: \
            ItemAttributesSetterDialog = None  # 当前的图元属性设置对话框

    def mousePressEvent(self, event):
        '''按下鼠标时，若主模式为绘制模式，则创建图元或添加父图元。
        '''
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton \
                and self.mainMode == GeoMainMode.DRAW:
            self._drawModeMousePress(event.pos())

    def _drawModeMousePress(self, pos: QPoint):
        '''当在绘制模式按下鼠标时，创建图元或添加父图元。具体实现如下：
        1. 若当前尚未创建图元，则创建；
        2. 根据选中的图元类型筛选匹配的类型模式，类型模式存储在
           `GeoGrapher.GeoGraphItems.GeoGraphItem.typePatterns`中；
        3. 若未选中图元，则创建新点，筛选允许创建点的类型模式；
           创建的点作为当前选中的图元进入后续操作；
        4. 若类型模式匹配成功，则将当前选中的图元作为待创建图元的父图元；
        5. 重复判断当前正在创建的图元是否需要输入变量值，不断匹配类型模式，
           直到不再需要输入变量值或输入失败；
        6. 若类型模式匹配成功且当前选中图元是该类型模式的最后一个图元，
           则当前图元创建完成，做收尾工作，为下次创建作准备；
        7. 若类型模式全部匹配失败，此次图元创建失败，做收尾工作，为下次创建作准备。
        图元的类型模式可以有多个，但是任一模式的全部类型不能与另一模式的开始数个类型相同，
        以避免产生歧义。

        :param pos: 鼠标点击的位置，在视图坐标系下。
        :type pos: PyQt5.QtCore.QPoint
        '''
        selectedItem = self.itemAt(pos)  # 选中的图元
        scenePos = self.mapToScene(pos)  # 转换为场景坐标系
        # 从未选择过图元，表明此次点击是第一次，要创建新图元
        if not self._drawModeSelectedItems:
            # 创建图元
            self._creatingItem: GeoGraphItem = self.secondaryMode.value()
            self.scene().addItem(self._creatingItem)
            # 初始化图元的类型匹配
            self._typePatterns = self._creatingItem.typePatterns.copy()
        rawTypePatterns = self._typePatterns.copy()
        # 根据选中的图元类型筛选匹配的类型模式
        self._typePatterns = \
            self._creatingItem.typePatternsFilter(
                rawTypePatterns,
                len(self._drawModeSelectedItems), type(selectedItem))
        createPointFlag = not self._typePatterns  # 是否需要创建新点
        # 若无匹配的类型模式
        if createPointFlag:
            # 此时需要创建一个点，筛选匹配点的类型模式
            self._typePatterns = \
                self._creatingItem.typePatternsFilter(
                    rawTypePatterns,
                    len(self._drawModeSelectedItems), GeoGraphPoint)
        if self._typePatterns:  # 匹配成功
            self._drawModeAddItem(                     # 添加
                self._createPointAt(scenePos)          # 创建的新点
                if createPointFlag else selectedItem)  # 或选中的图元为父图元
            # 重复检查变量输入要求，直到不再需要输入变量值或输入失败
            if not self._repeatCheckingVarInputRequirement():
                self._afterCreatingItem()
                return
            # 若此次图元创建完成
            if len(list(self._typePatterns)[0]) \
                    == len(self._drawModeSelectedItems):
                self._creatingItem.isCreated = True
                self._creatingItem.updateSelfPosition()
                # 初始化，以为下次创建作准备
                self._creatingItem = None
                self._afterCreatingItem()
        else:  # 匹配失败，此次图元创建失败，重新初始化
            self._afterCreatingItem()

    def _repeatCheckingVarInputRequirement(self) -> bool:
        '''重复检查变量输入要求。用于在一次创建过程中需要输入多个变量值的情况。
        '''
        while True:
            status, continueChecking = self._checkVarInputRequirement()
            if not status:  # 变量输入失败，创建失败，做收尾工作
                return False
            if not continueChecking:  # 不需要继续检查，结束
                return True

    def _checkVarInputRequirement(self) -> tuple[bool, bool]:
        '''检查当前正在创建的图元是否需要输入变量值。
        '''
        if len(list(self._typePatterns)[0]) \
                == len(self._drawModeSelectedItems):
            return True, False
        rawTypePatterns = self._typePatterns.copy()
        varTypePatterns = self._creatingItem.typePatternsFilter(
            rawTypePatterns, len(self._drawModeSelectedItems),
            GeoGraphVariable, loose=True)
        if varTypePatterns:
            varType = next(iter(varTypePatterns))[
                len(self._drawModeSelectedItems)]
            self._typePatterns = self._creatingItem.typePatternsFilter(
                varTypePatterns, len(self._drawModeSelectedItems), varType)
            varObject = varType()
            status = varObject.askValueFromUser(self)
            if status:
                self._drawModeAddItem(varObject)  # 添加变量图元
                return True, True
            else:
                return False, None
        return True, False  # 不需要输入变量值

    def _afterCreatingItem(self):
        '''完成创建后进行的收尾工作。包括：删除未完成创建的图元，清空选择过的图元列表。
        '''
        if self._creatingItem is not None:
            self.scene().removeItem(self._creatingItem)
            self._creatingItem = None
        self._drawModeSelectedItems = []

    def _drawModeAddItem(self, master: GeoGraphItem):
        '''为当前在创建的图元添加父图元。

        :param master: 要添加的父图元。
        :type master: GeoGrapher.GeoGraphItems.GeoGraphItem.GeoGraphItem
        '''
        # 为在创建的图元添加父图元
        self._creatingItem.addMaster(master)
        # 添加至选择过的图元列表
        self._drawModeSelectedItems.append(master)

    def _createPointAt(self, scenePos: QPointF) -> GeoGraphPoint:
        '''在指定坐标处创建一个点。
        自动判断该点是否为自由点、一路径上的点或两路径的交点。

        :param scenePos: 创建点的坐标，在场景坐标系下。
        :type scenePos: PyQt5.QtCore.QPointF
        :returns: 创建好的点。
        :rtype: GeoGrapher.GeoGraphItems.GeoGraphPoint.GeoGraphPoint
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

    def _createIntersecWithItems(
            self, scenePos: QPointF,
            items: list[GeoGraphItem]) -> GeoGraphIntersection:
        '''以指定图元为路径在指定坐标处创建一个交点。
        自动判断该点的交点编号，使得该点距离指定坐标较近。

        :param scenePos: 创建交点的坐标，在场景坐标系下。
        :type scenePos: PyQt5.QtCore.QPointF
        :param items: 取前两个为交点的路径。
        :type items: list[GeoGrapher.GeoGraphItems.GeoGraphItem.GeoGraphItem]
        :returns: 创建好的交点。
        :rtype:
            GeoGrapher.GeoGraphItems\
.GeoGraphIntersection.GeoGraphIntersection
        '''
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
            var.set(1 if float(l1) < float(l2) else 2)  # 自动判断交点编号
            point.addMaster(var)
        return point

    def mouseReleaseEvent(self, event):
        '''松开鼠标时，更新图元。以当前选中的可操作图元为顶层，开始更新。
        '''
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            # 若当前选中了可操作图元
            q = collections.deque()
            ancestors = set()
            for item in self.scene().selectedItems():
                if item.isUpdatable and not item.isUndefined:
                    q.append(item)
                    ancestors.add(item)
            while q:  # 将相关图元全部还原为更新前的准备状态
                master = q.popleft()
                for child in master.children():
                    q.append(child)  # 广度优先遍历
                master.updateFromMasters()
                master.instance.update()
            for ancestor in ancestors:
                for child in ancestor.children():
                    child.updatePosition(ancestor, ancestors)

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
        elif event.key() == Qt.Key_V \
                and self.mainMode == GeoMainMode.SELECT \
                and not isinstance(
                    self.scene().focusItem(), QGraphicsTextItem):
            # Only for tests
            for item in self.scene().selectedItems():
                if not isinstance(item, QGraphicsTextItem):
                    item.setVisible(not item.isVisible())

    def openItemAttributesDialog(self, item: GeoGraphItem):
        '''打开图元属性设置对话框。

        :param item: 待设置属性的图元。
        :type item: GeoGrapher.GeoGraphItems.GeoGraphItem.GeoGraphItem
        '''
        self.closeItemAttributesDialog()
        self._itemWithCurrentAttributesDialog = item
        title = f'Set Attributes for {item}'  # 对话框标题
        self._itemAttributesSetterDialog = ItemAttributesSetterDialog(
            self.scene().views()[0], item, title=title)
        self._itemAttributesSetterDialog.show()

    def closeItemAttributesDialog(self, item: GeoGraphItem | None = None):
        '''关闭图元属性设置对话框。

        :param item: 待关闭属性设置对话框的图元。默认为`None`，即关闭当前正在设置属性的图元的属性设置对话框。
        :type item: GeoGrapher.GeoGraphItems.GeoGraphItem.GeoGraphItem | None
        '''
        if item is None or item == self._itemWithCurrentAttributesDialog:
            if self._itemWithCurrentAttributesDialog:
                self._itemWithCurrentAttributesDialog = None
            if self._itemAttributesSetterDialog:
                self._itemAttributesSetterDialog.close()
                self._itemAttributesSetterDialog = None
