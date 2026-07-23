'''GeoGrapher图元基类
'''

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from PySide6.QtGui import QPainter
    from PySide6.QtCore import QPointF
    from ..GeoGraphScene import GeoGraphScene
    from .Interfaces.ItemAttributesSetter import ItemAttributesSetterDialog

from collections.abc import MutableMapping

from PySide6.QtWidgets import QStyle, QGraphicsItem
from PySide6.QtGui import QCursor, QPen, QColor
from PySide6.QtGui import QPainterPath, QPainterPathStroker
from PySide6.QtCore import Qt

__all__ = ['GeoGraphItem', 'GeoGraphPathItem', 'GeoGraphItemAttributes']


class GeoGraphItem(QGraphicsItem):
    '''所有图元类的基类。此类不应被创建实例。
    '''
    # 图元默认属性，子类可在此基础上添加以设置默认属性
    ATTRIBUTES_INFO = {
        'visible': {
            'default': True,
            'getter': lambda self: self.isVisible(),
            'setter': lambda self, value: self.setVisible(value)
        },
        'opacity': {
            'default': 1.0, 'min': 0.0, 'max': 1.0, 'decimals': 2,
            'getter': lambda self: self.opacity(),
            'setter': lambda self, value: self.setOpacity(value)
        },
    }

    def __init__(self):
        '''初始化图元。
        '''
        super().__init__()
        self._masters: list[GeoGraphItem] = []      # 父图元
        self._children: set[GeoGraphItem] = set()  # 子图元
        self.ancestors: set[GeoGraphItem] = set()  # 祖先
        # 在一轮更新中尚未调用`self.updatePosition()`的父图元
        self._mastersHaveNotUpdated: set[GeoGraphItem] = set()
        self._pens: list[QPen] = []  # 图元所有的画笔，用于缩放比例时更新
        self.isCreated: bool = False    # 是否已创建
        self.isUndefined: bool = False  # 是否未定义
        self.isAvailable: bool = True   # 是否可用，即是否未删除
        self.isUpdatable: bool = False  # 是否可作为顶层结点更新
        self._noMasters: bool = True    # 是否无祖先
        self.itemAttributes: GeoGraphItemAttributes \
            = GeoGraphItemAttributes(self, self.ATTRIBUTES_INFO)  # 图元属性
        self.itemAttributesSetterDialog: \
            ItemAttributesSetterDialog | None = None  # 图元属性设置对话框
        self.typePatterns: set[tuple[type[GeoGraphItem]]] = set()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def scene(self) -> GeoGraphScene:
        '''获取图元所在的场景。
        '''
        return super().scene()

    def shortIdentifier(self) -> str:
        '''返回图元的简短标识字符串。子类可覆盖此方法以提供更具体的标识字符串。
        '''
        return f'Item {id(self)}'

    def setUndefined(self, state: bool):
        '''设置图元的未定义状态，并递归更新其子图元状态。

        :param state: 图元是否未定义。
        '''
        if self.isUndefined != state:
            self.isUndefined = state
            self.setVisible(not self.isUndefined)
            for child in self._children:
                child.setUndefined(state)

    def updateFromMasters(
            self, master: GeoGraphItem | None = None,
            ancestors: set[GeoGraphItem] | None = None) -> bool:
        '''若没有传入`master`，则初始化`self._mastersHaveNotUpdated`。
        若传入`master`，则从`self._mastersHaveNotUpdated`中删除之；
        若本轮更新中该图元所有相关父图元均已更新，即`self._mastersHaveNotUpdated`
        已空，则该图元可以更新，返回`True`，反之返回`False`。

        :param master: 调用该函数的父图元。
        :param ancestors: 本轮更新中的顶层图元。
        :returns: 是否可以更新。
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

    def updatePosition(
            self, master: GeoGraphItem, ancestors: set[GeoGraphItem]):
        '''被动更新。为避免反复更新同一图元，仅当一轮更新中最后一次调用时更新。

        :param master: 调用该函数的父图元。
        :param ancestors: 本轮更新中的顶层图元。
        '''
        if self.updateFromMasters(master, ancestors):
            self.updateSelfPosition()     # 更新自身
            for child in self._children:  # 更新子图元
                child.updatePosition(self, ancestors)

    def updateSelfPosition(self):
        '''更新自身位置。子类可覆盖此方法。
        '''
        pass

    def typePatternsFilter(
            self, patterns: set[tuple[type[GeoGraphItem]]],
            idx: int, itemType: type[GeoGraphItem], loose: bool = False) \
            -> set[tuple[type[GeoGraphItem]]]:
        '''筛选可用的类型匹配。参见`GeoGraphView._clickInDrawMode()`。

        :param patterns: 可用的所有类型匹配。
        :param idx: 当前匹配位置。
        :param itemType: 待匹配的类型。
        :param loose: 是否宽松匹配，即待匹配类型是否可为类型匹配中对应位置的子类。
        :returns: 筛选后可用的类型匹配。
        '''
        return {
            typePattern for typePattern
            in self.typePatterns.intersection(patterns)
            if len(typePattern) > idx
            and (issubclass(typePattern[idx], itemType)
                 if loose else issubclass(itemType, typePattern[idx]))}

    def masters(self) -> list[GeoGraphItem]:
        '''本图元的父图元。
        '''
        return self._masters

    def addMaster(self, master: GeoGraphItem):
        '''为本图元添加父图元。仅在初始化图元时调用。
        '''
        if self._noMasters:
            self._noMasters = False  # 必须使用标志变量，否则会造成无限循环递归
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

    def _addFirstMaster(self, master: GeoGraphItem):
        '''为本图元添加第一个父图元。子类可在此处作一些特殊处理。
        '''
        self.addMaster(master)

    def children(self) -> set[GeoGraphItem]:
        '''本图元的子图元。
        '''
        return self._children

    def addChild(self, child: GeoGraphItem):
        '''为本图元添加子图元。
        '''
        self._children.add(child)

    def removeChild(self, child: GeoGraphItem):
        '''删除本图元的子图元。
        '''
        if self.isAvailable and child in self._children:
            self._children.remove(child)
            self.instance.removeChild(child.instance)

    def onAddingSelfToScene(self):
        '''在场景中添加时调用。子类可覆盖此方法。
        '''
        pass

    def onRemovingSelfFromScene(self):
        '''在场景中删除时调用。子类可覆盖此方法。
        '''
        pass

    def zoomScaleChanged(self, zoomChange: float):
        '''当视图放缩比例改变时调用。子类可覆盖此方法。

        :param zoomChange: 放缩比例的变化比例，即新放缩比例比原放缩比例。
        '''
        pass

    def itemChange(self, change, value):
        '''图元状态改变时调用。子类可覆盖此方法以处理特定状态改变。
        '''
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange \
                and self.isCreated:
            if value:  # 选中
                self.openItemAttributesDialog()
            else:      # 取消选中
                self.closeItemAttributesDialog()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSceneChange:
            if value is None:
                self.closeItemAttributesDialog()  # 删除图元属性设置对话框实例
        return super().itemChange(change, value)

    def openItemAttributesDialog(self):
        '''打开属性设置弹窗。
        '''
        self.scene().views()[0].openItemAttributesDialog(self)

    def closeItemAttributesDialog(self):
        '''关闭属性设置弹窗。
        '''
        self.scene().views()[0].closeItemAttributesDialog(self)

    def _mousePos(self) -> QPointF:
        '''鼠标位置。

        :returns: 当前鼠标位置，在场景坐标系下。
        '''
        view = self.scene().views()[0]
        return view.mapToScene(view.mapFromGlobal(QCursor.pos()))


class GeoGraphPathItem(GeoGraphItem):
    '''所有路径图元类的基类。此类不应被创建实例。
    '''

    def __init__(self):
        '''初始化路径图元。
        '''
        super().__init__()
        self._penDrag = QPen(
            QColor('#000000'), 1., Qt.PenStyle.DashLine)  # 创建时的画笔
        self._penFinal = QPen(QColor('#000000'))     # 创建完成后未选中时的画笔
        self._penSelected = QPen(QColor('#808080'))  # 创建完成后选中时的画笔
        self._selectWidth = 10.      # 选中范围的宽度
        # 所有画笔
        self._pens = [self._penDrag, self._penFinal, self._penSelected]
        self.setZValue(-1)  # 路径图元位于所有图元的下方

    def updateSelfPosition(self):
        '''路径图元不更新位置，仅调用`prepareGeometryChange()`方法触发重绘。
        '''
        super().updateSelfPosition()
        self.prepareGeometryChange()

    def rawShape(self) -> QPainterPath:
        '''原始的路径形状，不具有选中范围。此方法应被子类覆盖。
        '''
        pass

    def shape(self) -> QPainterPath:
        '''路径形状。

        :returns: 路径的形状，具有带宽度的选中范围。
        '''
        pathStroker = QPainterPathStroker()
        pathStroker.setWidth(self._selectWidth)
        return pathStroker.createStroke(
            QPainterPath() if not self._masters else self.rawShape())

    def boundingRect(self):
        '''使用自身路径的矩形作为图元的矩形。
        '''
        return self.shape().boundingRect()

    def paint(self, painter: QPainter, option, widget=None):
        '''绘制路径。根据图元情况选择画笔。
        '''
        if not self.isCreated:
            self.prepareGeometryChange()  # 只有正在创建时才需要不断重绘
        if option.state & QStyle.StateFlag.State_Selected:
            painter.setPen(self._penSelected)
        else:
            painter.setPen(
                self._penFinal if self.isCreated else self._penDrag)
        painter.drawPath(self.rawShape())

    def zoomScaleChanged(self, zoomChange: float):
        '''当视图放缩比例改变时更新选中宽度。

        :param zoomChange: 放缩比例的变化比例，即新放缩比例比原放缩比例。
        '''
        super().zoomScaleChanged(zoomChange)
        self._selectWidth /= zoomChange


class GeoGraphItemAttributes(MutableMapping):
    '''图元属性类。以字典形式存储图元属性。

    使用`GeoGraphItemAttributes(item, attributesInfo)`创建图元属性实例。
    `attributesInfo`是一个字典，键是图元的各个属性名称，值是该属性的描述。
    每个属性的描述是一个字典，键是各个字段，值是该字段对应的值。支持的字段有：

    - `title`：属性的自然语言描述。若不提供，则以字段名的首字母大写形式为描述。
    - `group`：属性所在的分组。可以用此字段为属性分组，也可以不提供。
    - `default`：属性的默认值。若不提供，则以`getter`字段的返回值为默认值。
    - `min, max, step`：属性的最小值、最大值与步长。仅限整数或浮点数属性。
    - `decimals`：属性的浮点有效位数。仅限浮点数属性。
    - `type`：属性的类型。若不提供，则以默认值的类型为属性的类型。
    - `getter: Callable[[] -> Any]`：一个无参函数，返回属性的值。
        未提供默认值时以此为默认值，但不会在初始化时直接设置，而是懒惰求值。
    - `setter: Callable[[Any] -> None]`：一个函数，设置属性的值。
        当调用`GeoGraphItemAttributes.__setitem__()`时会调用此函数。

    `GeoGraphItemAttributes.__setitem__()`会对参数进行校验，
    但仅检查`type`、`min`、`max`字段，其余字段供`ItemAttributesSetterDialog`使用。
    '''
    SPECIAL_ATTRTYPES = {'angle': int, 'color': QColor}  # 特殊属性类型，需特殊处理

    def __init__(
            self, item: GeoGraphItem,
            attributesInfo: dict[str, dict[str, Any]] | None = None):
        '''初始化图元属性。

        :param item: 图元实例，用于获取图元属性。
        :param attributesInfo: 图元属性信息字典。
        '''
        super().__init__()
        self._item = item
        self._attributes = {}     # 存储图元属性值的字典
        self.attributesInfo = {}  # 存储图元属性信息的字典，便于后续获取属性信息
        if attributesInfo is not None:
            for name, info in attributesInfo.items():
                self._attributes[name] = (
                    info['default'] if 'default' in info else None)
                self.attributesInfo[name] = info.copy()
                if 'type' not in self.attributesInfo[name]:
                    self.attributesInfo[name]['type'] \
                        = type(self._attributes[name])
                if 'title' not in self.attributesInfo[name]:
                    self.attributesInfo[name]['title'] = name.capitalize()
                if self.attributesInfo[name]['type'] in self.SPECIAL_ATTRTYPES:
                    self.attributesInfo[name]['pythonType'] \
                        = self.SPECIAL_ATTRTYPES[
                            self.attributesInfo[name]['type']]

    def __len__(self):
        '''图元属性数量。
        '''
        return len(self._attributes)

    def __getitem__(self, key: str) -> Any:
        '''获取图元属性值。

        :param key: 属性名称。
        :returns: 图元属性值。
        '''
        if key not in self.attributesInfo:
            raise KeyError(f"Attribute '{key}' not found")
        value = self._attributes[key]
        if value is None and 'getter' in self.attributesInfo[key]:
            value = self.attributesInfo[key]['getter'](self._item)
            self._attributes[key] = value
        return value

    def __setitem__(self, key: str, value: Any):
        '''设置图元属性值。

        :param key: 属性名称。
        :param value: 属性值。
        '''
        if key in self.attributesInfo:
            attrInfo = self.attributesInfo[key]
            attrType = attrInfo.get('pythonType', attrInfo['type'])
            try:
                value = attrType(value)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid value for attribute '{key}': {value}")
            if isinstance(value, int | float):
                if 'min' in attrInfo and value < attrInfo['min']:
                    raise ValueError(
                        f"Value for attribute '{key}' cannot be "
                        f"less than {attrInfo['min']}")
                if 'max' in attrInfo and value > attrInfo['max']:
                    raise ValueError(
                        f"Value for attribute '{key}' cannot be "
                        f"greater than {attrInfo['max']}")
            if 'setter' in attrInfo:
                attrInfo['setter'](self._item, value)
        self._attributes[key] = value

    def __delitem__(self, key: str):
        '''删除图元属性。
        '''
        if key in self._attributes:
            del self._attributes[key]
        if key in self.attributesInfo:
            del self.attributesInfo[key]

    def __iter__(self) -> Iterator[str]:
        '''迭代图元属性名称。
        '''
        return iter(self._attributes)

    def getAttributesInfo(self, attr: str) -> dict[str, Any]:
        '''获取图元属性信息。

        :param attr: 属性名称。
        :returns: 图元属性信息。
        '''
        return self.attributesInfo[attr]
