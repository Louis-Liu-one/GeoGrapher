'''GeoGrapher绘制视图
'''

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QPoint
    from .Constants import GeoSecondaryMode
    from .GeoGraphScene import GeoGraphScene

from PySide6.QtWidgets import QGraphicsView, QGraphicsTextItem
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt

from .GeoGraphItems.GeoGraphItem import GeoGraphItem
from .GeoGraphItems.GeoGraphPoint import GeoGraphPoint
from .GeoGraphItems.GeoGraphVariable import GeoGraphVariable
from .GeoGraphItems.Interfaces.ItemAttributesSetter import \
    ItemAttributesSetterDialog
from .Constants import GeoMainMode, secondaryModeClasses

__all__ = ['GeoGraphView']


class GeoGraphView(QGraphicsView):
    '''GeoGrapher绘制视图。结合`GeoGraphScene`使用。使用方法与`QGraphicsView`相同。
    '''

    def __init__(self, scene: GeoGraphScene, parent=None):
        '''创建视图。参数与`QGraphicsView`相同。
        '''
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        self._mainMode: GeoMainMode = GeoMainMode.SELECT     # 主模式，默认为选择模式
        self._secondaryMode: GeoSecondaryMode | None = None  # 次模式
        # 下列属性在绘制模式创建图元时使用
        self._drawModeSelectedItems: list[GeoGraphItem] = []  # 当前选择过的图元
        # 满足用户操作的当前正在创建的图元的类型匹配
        self._typePatterns: list[tuple[type[GeoGraphItem]]] = []
        self._creatingItem: GeoGraphItem | None = None        # 当前正在创建的图元
        self._itemWithCurrentAttributesDialog: \
            GeoGraphItem | None = None                        # 当前正在设置属性的图元
        self._itemAttributesSetterDialog: \
            ItemAttributesSetterDialog | None = None          # 当前的图元属性设置对话框
        self._zoomScale = 1.                                      # 缩放倍数
        self._minimumZoomScale, self._maximumZoomScale = .1, 10.  # 最小、最大缩放倍数

    def scene(self) -> GeoGraphScene:
        '''获取视图对应的场景对象。
        '''
        return super().scene()

    def toggleMainMode(self, mode: GeoMainMode):
        '''设置主模式。
        '''
        self._mainMode = mode

    def toggleSecondaryMode(self, mode: GeoSecondaryMode):
        '''设置次模式，并将主模式设为绘制模式。
        '''
        self._mainMode = GeoMainMode.DRAW
        self._secondaryMode = mode

    def mousePressEvent(self, event):
        '''按下鼠标时，若主模式为绘制模式，则创建图元或添加父图元。
        '''
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton \
                and self._mainMode == GeoMainMode.DRAW:
            self._clickInDrawMode(event.pos())

    def _clickInDrawMode(self, pos: QPoint):
        '''当在绘制模式按下鼠标时，创建图元或添加父图元。具体实现如下：
        1. 若当前尚未创建图元，则创建；
        2. 根据选中的图元类型筛选匹配的类型模式，类型模式存储在
           图元的`typePatterns`属性中；
        3. 若未选中图元，则创建新点，筛选允许创建点的类型模式；
           创建的点作为当前选中的图元进入后续操作；
        4. 若类型模式匹配成功，则将当前选中的图元作为待创建图元的父图元；
        5. 重复判断当前正在创建的图元是否需要输入变量值，不断匹配类型模式，
           直到不再需要输入变量值或输入失败；
        6. 若类型模式匹配成功且当前选中图元是该类型模式的最后一个图元，
           则当前图元创建完成，做收尾工作，为下次创建作准备；
        7. 若类型模式全部匹配失败，此次图元创建失败，做收尾工作，为下次创建作准备。
        图元的类型模式可以有多个，但是任一模式不能是另一模式的前缀，以避免产生歧义。

        :param pos: 鼠标点击的位置，在视图坐标系下。
        '''
        selectedItem = self.itemAt(pos)  # 选中的图元
        scenePos = self.mapToScene(pos)  # 转换为场景坐标系
        # 从未选择过图元，表明此次点击是第一次，要创建新图元
        if not self._drawModeSelectedItems:
            # 创建图元
            self._creatingItem = \
                secondaryModeClasses[self._secondaryMode]()
            self.scene().addItem(self._creatingItem)
            # 初始化图元的类型匹配
            self._typePatterns = self._creatingItem.typePatterns.copy()
        rawTypePatterns = self._typePatterns.copy()
        # 根据选中的图元类型筛选匹配的类型模式
        self._typePatterns = self._creatingItem.typePatternsFilter(
            rawTypePatterns,
            len(self._drawModeSelectedItems), type(selectedItem))
        createPointFlag = not self._typePatterns  # 是否需要创建新点
        # 若无匹配的类型模式
        if createPointFlag:
            # 此时需要创建一个点，筛选匹配点的类型模式
            self._typePatterns = self._creatingItem.typePatternsFilter(
                rawTypePatterns,
                len(self._drawModeSelectedItems), GeoGraphPoint)
        if self._typePatterns:  # 匹配成功
            self._addMasterForCreatingItem(                     # 添加
                self.scene().createPointAt(scenePos)   # 创建的新点
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

        :returns: 变量是否全部输入完成，创建成功。
        '''
        while True:
            status, continueChecking = self._checkVarInputRequirement()
            if not status:  # 变量输入失败，创建失败，做收尾工作
                return False
            if not continueChecking:  # 不需要继续检查，结束
                return True

    def _checkVarInputRequirement(self) -> tuple[bool, bool]:
        '''检查当前正在创建的图元是否需要输入变量值。

        :returns: 返回一个元组，由两个`bool`组成。
            第一个表示此次变量创建是否没有出现问题，第二个表示此次是否创建了变量。
            只有存在需要创建变量的类型模式时才会创建变量图元。
        '''
        if len(list(self._typePatterns)[0]) \
                == len(self._drawModeSelectedItems):
            return True, False
        rawTypePatterns = self._typePatterns.copy()
        varTypePatterns = self._creatingItem.typePatternsFilter(
            rawTypePatterns, len(self._drawModeSelectedItems),
            GeoGraphVariable, loose=True)  # 查找下一个图元类型是变量的类型模式
        if varTypePatterns:  # 如果存在这种类型模式
            varType = next(iter(varTypePatterns))[
                len(self._drawModeSelectedItems)]
            self._typePatterns = self._creatingItem.typePatternsFilter(
                varTypePatterns, len(self._drawModeSelectedItems), varType)
            varObject: GeoGraphVariable = varType()
            status = varObject.askValueFromUser(self)
            if status:
                self._addMasterForCreatingItem(varObject)  # 添加变量图元
                return True, True
            else:
                return False, None
        return True, False  # 不需要输入变量值

    def _afterCreatingItem(self):
        '''完成创建后进行的收尾工作。包括：删除未完成创建的图元，清空选择过的图元列表。
        '''
        if self._creatingItem is not None:  # 若当前正在创建的图元未完成创建便退出，则删除该图元
            self.scene().removeItem(self._creatingItem)
            self._creatingItem = None
        self._drawModeSelectedItems = []

    def _addMasterForCreatingItem(self, master: GeoGraphItem):
        '''为当前在创建的图元添加父图元。

        :param master: 要添加的父图元。
        '''
        # 为在创建的图元添加父图元
        self._creatingItem.addMaster(master)
        # 添加至选择过的图元列表
        self._drawModeSelectedItems.append(master)

    def keyPressEvent(self, event):
        '''按下删除键时，删除选中图元。
        '''
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_Backspace \
                and self._mainMode == GeoMainMode.SELECT \
                and not isinstance(
                    self.scene().focusItem(), QGraphicsTextItem):  # 正在输入时不删除
            for item in self.scene().selectedItems():
                if isinstance(item, GeoGraphItem):
                    self.scene().removeItem(item)

    def openItemAttributesDialog(self, item: GeoGraphItem):
        '''打开给定图元的属性设置对话框。
        '''
        self.closeItemAttributesDialog()
        self._itemWithCurrentAttributesDialog = item
        title = f'Set Attributes for {item}'  # 对话框标题
        self._itemAttributesSetterDialog = ItemAttributesSetterDialog(
            self, item, title=title)
        self._itemAttributesSetterDialog.show()

    def closeItemAttributesDialog(self, item: GeoGraphItem | None = None):
        '''关闭图元属性设置对话框。

        :param item: 待关闭属性设置对话框的图元。默认为`None`，即关闭当前正在设置属性的图元的属性设置对话框。
        '''
        if item is None or item == self._itemWithCurrentAttributesDialog:
            if self._itemWithCurrentAttributesDialog:
                self._itemWithCurrentAttributesDialog = None
            if self._itemAttributesSetterDialog:
                self._itemAttributesSetterDialog.close()
                self._itemAttributesSetterDialog = None

    def zoomScaleChanged(self, zoomChange: float):
        '''缩放时调用。控制缩放比例于一定范围内，并将信号传递给场景。
        '''
        newZoomScale = self._zoomScale * zoomChange
        if self._minimumZoomScale <= newZoomScale <= self._maximumZoomScale:
            self._zoomScale = newZoomScale
            self.scale(zoomChange, zoomChange)
            self.scene().zoomScaleChanged(zoomChange)
