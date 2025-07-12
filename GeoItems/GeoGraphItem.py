'''GeoGrapher图元基类
'''

from PyQt5.QtWidgets import QStyle, QGraphicsItem, QGraphicsPathItem
from PyQt5.QtGui import QCursor, QPen, QColor, QPainterPathStroker
from PyQt5.QtCore import Qt

from .GeoBasicItems import GeoPoint

__all__ = ['GeoGraphItem', 'GeoGraphPathItem']


class GeoGraphItem(QGraphicsItem):
    '''所有图元类的基类。此类不应创建实例。
    '''

    def __init__(self, master):
        '''初始化图元。

        :param master: 图元的第一个父图元。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        super().__init__()
        self._masters = [] if master is None else [master]  # 父图元
        self._children = []                                 # 子图元
        # 祖先
        self.ancestors = [] if master is None else master.ancestors.copy()
        # 在一轮更新中尚未调用``self.updatePosition()``的父图元
        self._mastersHaveNotUpdated = self._masters.copy()
        self.isCreated = False   # 是否已创建
        self.isAvailable = True  # 是否可用，即是否未删除
        self.setFlag(self.ItemIsSelectable)
        if master is not None:
            master.addChild(self)

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

    def activelyUpdatePosition(self):
        '''主动更新。只更新子图元而不更新自身。
        '''
        self.updateChildrenPosition(self)

    def updatePosition(self, master, ancestor):
        '''被动更新。为避免反复更新子图元，仅当一轮更新中最后一次调用时更新。

        :param master: 调用该函数的父图元。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        :param ancestor: 本轮更新中主动更新的图元。
        :type ancestor: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        if master in self._mastersHaveNotUpdated:
            self._mastersHaveNotUpdated.remove(master)
        for i in range(len(self._mastersHaveNotUpdated) - 1, -1, -1):
            # 若仍有相关父图元未调用该函数
            if ancestor in self._mastersHaveNotUpdated[i].ancestors:
                # 则不更新子图元
                return
            self._mastersHaveNotUpdated.pop(i)  # 删除无关的父图元
        # 本轮更新完毕，重新初始化并更新
        self._mastersHaveNotUpdated = self._masters.copy()
        self.updateSelfPosition()              # 更新自身
        self.updateChildrenPosition(ancestor)  # 更新子图元

    def updateSelfPosition(self):
        '''更新自身。此方法应被子类覆盖。
        '''
        pass

    def updateChildrenPosition(self, ancestor):
        '''更新子图元。

        :param ancestor: 本轮更新中主动更新的图元。
        :type ancestor: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        for child in self._children:
            child.updatePosition(self, ancestor)

    @staticmethod
    def typePatternsFilter(selfType, idx, itemType):
        '''筛选可用的类型匹配。参见
        ``GeoGrapher.GeoGridGraphView.GeoGridGraphView._drawModeMousePress``。

        :param selfType: 图元自身的类型。
        :type selfType: type
        :param idx: 当前匹配位置。
        :type idx: int
        :param itemType: 待匹配的类型。
        :type itemType: type
        :returns: 筛选后可用的类型匹配。
        :rtype: list[list[type]]
        '''
        return [
            typePattern for typePattern in selfType.typePatterns
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
        self._masters.append(master)
        self._mastersHaveNotUpdated.append(master)
        master.addChild(self)
        # 更新祖先
        for ancestor in master.ancestors:
            if ancestor not in self.ancestors:
                self.ancestors.append(ancestor)
        self.instance.addMaster(master.instance)

    def addChild(self, child):
        '''为本图元添加子图元。
        '''
        self._children.append(child)

    def removeChild(self, child):
        '''删除本图元的子图元。
        '''
        if child in self._children:
            self._children.remove(child)

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

    def __init__(self, master):
        '''初始化路径图元。

        :param master: 图元的第一个父图元。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        QGraphicsPathItem.__init__(self)
        GeoGraphItem.__init__(self, master)
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
        return pathStroker.createStroke(self.rawShape())

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
