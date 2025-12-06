'''GeoGrapher图元基类
'''

import collections

from PyQt5.QtWidgets import QStyle, QGraphicsItem, QGraphicsPathItem
from PyQt5.QtGui import QCursor, QPen, QColor
from PyQt5.QtGui import QPainterPath, QPainterPathStroker
from PyQt5.QtCore import Qt

from .Core import GeoPoint

__all__ = ['GeoGraphItem', 'GeoGraphPathItem']


class GeoGraphItem(QGraphicsItem):
    '''所有图元类的基类。此类不应创建实例。
    '''

    def __init__(self):
        '''初始化图元。
        '''
        super().__init__()
        self._masters = []      # 父图元
        self._children = set()  # 子图元
        self.ancestors = set()  # 祖先
        # 在一轮更新中尚未调用`self.updatePosition()`的父图元
        self._mastersHaveNotUpdated = set()
        self._pens = []  # 图元所有的画笔，用于缩放比例时更新
        self.isCreated = False    # 是否已创建
        self.isUndefined = False  # 是否未定义
        self.isAvailable = True   # 是否可用，即是否未删除
        self.isUpdatable = False  # 是否可作为顶层结点更新
        self._noMasters = True    # 是否无祖先
        self.setFlag(self.ItemIsSelectable)

    def update(self):
        '''视图调用时检查是否可用。
        '''
        super().update()
        self._checkAvailable()

    def _checkAvailable(self):
        '''检查图元是否可用。若图元的父图元之一不可用，则该图元不可用，删除图元。
        '''
        if self.isAvailable:
            for item in self._masters:
                if not item.isAvailable:
                    self.scene().removeItem(self)
                    break

    def setUndefined(self, state):
        '''设置图元的未定义状态，并递归更新其子图元状态。

        :param state: 图元是否未定义。
        :type state: bool
        '''
        if self.isUndefined != state:
            self.isUndefined = state
            self.setVisible(not self.isUndefined)
            for child in self._children:
                child.setUndefined(state)

    def updateFromMasters(self, master=None, ancestors=None):
        '''若没有传入`master`，则初始化`self._mastersHaveNotUpdated`。
        若传入`master`，则从`self._mastersHaveNotUpdated`中删除之；
        若本轮更新中该图元所有相关父图元均已更新，即`self._mastersHaveNotUpdated`
        已空，则该图元可以更新，返回`True`，反之返回`False`。

        :param master: 调用该函数的父图元。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        :param ancestors: 本轮更新中的顶层图元。
        :type ancestors: set[GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem]
        '''
        if master is not None:
            ancestors = set(ancestors)
            if master in self._mastersHaveNotUpdated:
                self._mastersHaveNotUpdated.remove(master)
            while self._mastersHaveNotUpdated:
                item = self._mastersHaveNotUpdated.pop()
                if not item.ancestors.isdisjoint(ancestors):
                    self._mastersHaveNotUpdated.add(item)
                    return False
        self._mastersHaveNotUpdated = set(self._masters)
        return True

    def updatePosition(self, master, ancestors):
        '''被动更新。为避免反复更新同一图元，仅当一轮更新中最后一次调用时更新。

        :param master: 调用该函数的父图元。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        :param ancestor: 本轮更新中的顶层图元。
        :type ancestors: set[GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem]
        '''
        if self.updateFromMasters(master, ancestors):
            self.updateSelfPosition()     # 更新自身
            for child in self._children:  # 更新子图元
                child.updatePosition(self, ancestors)

    def updateSelfPosition(self):
        '''更新自身。子类可覆盖此方法。
        '''
        pass

    def typePatternsFilter(self, idx, itemType):
        '''筛选可用的类型匹配。参见
        `GeoGrapher.GeoGridGraphView.GeoGridGraphView._drawModeMousePress()`。

        :param idx: 当前匹配位置。
        :type idx: int
        :param itemType: 待匹配的类型。
        :type itemType: type
        :returns: 筛选后可用的类型匹配。
        :rtype: list[list[type]]
        '''
        return [
            typePattern for typePattern in self.typePatterns
            if len(typePattern) >= idx
            and issubclass(itemType, typePattern[idx])]

    def masters(self):
        '''本图元的父图元。
        '''
        return self._masters

    def addMaster(self, master):
        '''为本图元添加父图元。仅在初始化图元时调用。

        :param master: 待添加的父图元。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        if self._noMasters:
            self._noMasters = False
            self._addFirstMaster(master)
        else:
            self._masters.append(master)
            self._mastersHaveNotUpdated.add(master)
            master.addChild(self)
            # 更新祖先
            for ancestor in master.ancestors:
                if ancestor not in self.ancestors:
                    self.ancestors.add(ancestor)
            self.instance.addMaster(master.instance)

    def _addFirstMaster(self, master):
        '''为本图元添加第一个父图元。子类可在此处作一些特殊处理。
        '''
        self.addMaster(master)

    def children(self):
        '''本图元的子图元。
        '''
        return self._children

    def addChild(self, child):
        '''为本图元添加子图元。
        '''
        self._children.add(child)

    def removeChild(self, child):
        '''删除本图元的子图元。
        '''
        if self.isAvailable and child in self._children:
            self._children.remove(child)
            self.instance.removeChild(child.instance)

    def removeSelf(self):
        '''删除自身，而不在场景中删除。
        '''
        self.removeSelfFromScene()
        self.isAvailable = False
        for master in self._masters:
            master.removeChild(self)  # 从所有父图元中删除自身

    def removeSelfFromScene(self):
        '''在场景中删除时调用。子类可覆盖此方法。
        '''
        pass

    def zoomScaleChanged(self, zoomChange):
        '''当视图放缩比例改变时设置画笔宽度以适应放缩比例。

        :param zoomChange: 放缩比例的变化比例，即新放缩比例比原放缩比例。
        :type zoomChange: float
        '''
        for pen in self._pens:
            pen.setWidthF(pen.widthF() / zoomChange)

    def _mousePos(self):
        '''鼠标位置。

        :returns: 当前鼠标位置，在场景坐标系下。
        :rtype: PyQt5.QtCore.QPointF
        '''
        view = self.scene().views()[0]
        return view.mapToScene(view.mapFromGlobal(QCursor.pos()))


class GeoGraphPathItem(QGraphicsPathItem, GeoGraphItem):
    '''所有路径图元类的基类。此类不应创建实例。
    '''

    def __init__(self):
        '''初始化路径图元。

        :param master: 图元的第一个父图元。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        super().__init__()
        self._penDrag = QPen(QColor('#000000'), 1., Qt.DashLine)  # 创建时的画笔
        self._penFinal = QPen(QColor('#000000'))     # 创建完成后未选中时的画笔
        self._penSelected = QPen(QColor('#808080'))  # 创建完成后选中时的画笔
        self._selectWidth = 10.  # 选中范围的宽度
        # 所有画笔
        self._pens = [self._penDrag, self._penFinal, self._penSelected]
        self.setPen(self._penFinal)
        self.setZValue(-1)  # 路径图元位于所有图元的下方

    def rawShape(self):
        '''原始的路径形状，不具有选中范围。此方法应被子类覆盖。
        '''
        pass

    def shape(self):
        '''路径形状。

        :returns: 路径的形状，具有带宽度的选中范围。
        :rtype: PyQt5.QtGui.QPainterPath
        '''
        pathStroker = QPainterPathStroker()
        pathStroker.setWidth(self._selectWidth)
        rawShape = QPainterPath if not self._masters else self.rawShape
        return pathStroker.createStroke(rawShape())

    def paint(self, painter, option, widget=None):
        '''绘制路径。根据图元情况选择画笔。
        '''
        self.update()
        self.setPath(self.shape())
        if option.state & QStyle.State_Selected:
            option.state = QStyle.State_None
            painter.setPen(self._penSelected)
        else:
            painter.setPen(
                self._penFinal if self.isCreated else self._penDrag)
        painter.drawPath(self.rawShape())

    def zoomScaleChanged(self, zoomChange):
        '''当视图放缩比例改变时更新画笔宽度和选中宽度。

        :param zoomChange: 放缩比例的变化比例，即新放缩比例比原放缩比例。
        :type zoomChange: float
        '''
        super().zoomScaleChanged(zoomChange)
        self._selectWidth /= zoomChange
