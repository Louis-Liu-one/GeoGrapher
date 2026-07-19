'''图元属性设置对话框
'''

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QWidget
    from ..GeoGraphItem import GeoGraphItem

from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QSizePolicy
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtWidgets import (
    QLineEdit, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QCheckBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QPointF

from .FormUtils import IntValueSliderSelector, ColorSelector

__all__ = ['ItemAttributesSetterDialog']


class ItemAttributesSetterDialog(QDialog):
    '''图元属性设置对话框。
    '''

    def __init__(
            self, parent: QWidget | None = None,
            item: GeoGraphItem = None, title: str = 'Set Item Attributes',
            defaultGroupName: str = 'Basic'):
        '''初始化对话框。

        :param parent: 父窗口。
        :param item: 需要设置属性的图元。
        :param title: 对话框标题。
        :param defaultGroupName: 未设置`group`字段的属性的默认组名。
        '''
        super().__init__(parent)
        self._item = item
        self._defaultGroupName = str(defaultGroupName)
        self._initUi()
        self._adjustPosition()
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowTitle(title)

    def _initUi(self):
        '''初始化界面。
        '''
        tree = QTreeWidget()
        tree.setMinimumHeight(300)
        tree.setMaximumHeight(500)
        tree.setIndentation(15)
        tree.setColumnCount(2)
        tree.setHeaderLabels(['Attribute', 'Value'])
        # 第一列自适应内容宽度，不截断文字
        tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        groups = {}
        # 在此添加界面元素
        self._valueGetters = {}    # 存储属性值获取函数的字典，便于后续获取当前属性值
        for attr, value in self._item.itemAttributes.items():
            attrInfo = self._item.itemAttributes.getAttributesInfo(attr)
            attributeBox = self._createAttributeBox(attr, value)
            if attributeBox is None:
                continue  # 不支持的属性类型，跳过
            attributeBox.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Preferred)
            groupName = attrInfo.get('group', self._defaultGroupName)
            if groupName not in groups:
                groups[groupName] = QTreeWidgetItem(tree, [groupName])
                groups[groupName].setExpanded(True)
            treeWidget = QTreeWidgetItem(
                groups[groupName], [attrInfo['title']])
            treeWidget.setTextAlignment(0, Qt.AlignRight | Qt.AlignVCenter)
            tree.setItemWidget(treeWidget, 1, attributeBox)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(tree)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.adjustSize()

    def _createAttributeBox(self, attr: str, value: Any) -> QWidget | None:
        '''根据属性类型创建对应的界面元素。

        :param attr: 属性名。
        :param value: 属性值。
        :returns: 对应的界面元素，若属性类型不支持则返回`None`。
        '''
        attrInfo = self._item.itemAttributes.getAttributesInfo(attr)
        attrType = attrInfo['type']
        if attrType == 'angle':
            attributeBox = IntValueSliderSelector()
            attributeBox.setRange(-180, 180)
            attributeBox.setValue(value)
            self._valueGetters[attr] = attributeBox.value
        elif attrType == 'color':
            attributeBox = ColorSelector(
                dialogTitle=f'Select {attrInfo['title']}')
            attributeBox.setValue(QColor(value))
            self._valueGetters[attr] = attributeBox.value
        elif issubclass(attrType, bool):
            attributeBox = QCheckBox()
            attributeBox.setChecked(value)
            self._valueGetters[attr] = attributeBox.isChecked
        elif issubclass(attrType, (int, float)):
            attributeBox = QDoubleSpinBox() \
                if issubclass(attrType, float) else QSpinBox()
            if attrInfo.get('min') is not None:
                attributeBox.setMinimum(attrInfo['min'])
            if attrInfo.get('max') is not None:
                attributeBox.setMaximum(attrInfo['max'])
            attributeBox.setSingleStep(attrInfo.get(
                'step', .05 if issubclass(attrType, float) else 1))
            if issubclass(attrType, float) \
                    and attrInfo.get('decimals') is not None:
                attributeBox.setDecimals(attrInfo['decimals'])
            attributeBox.setValue(value)
            self._valueGetters[attr] = attributeBox.value
        elif issubclass(attrType, str):
            attributeBox = QLineEdit(str(value))
            self._valueGetters[attr] = attributeBox.text
        else:
            return None  # 不支持的属性类型，返回None
        return attributeBox

    def _adjustPosition(self):
        '''调整对话框位置，使其出现在图元的右上方。
        '''
        if self._item and self._item.scene() and self._item.scene().views():
            view_top_left = self._item.scene().views()[0].mapToGlobal(
                QPointF(0, 0).toPoint())
            dlg_x = view_top_left.x() - self.width() - 15  # 调整对话框横坐标，使其出现在视图左侧
            dlg_y = view_top_left.y()
            self.move(dlg_x, dlg_y)

    def accept(self):
        '''确认设置，更新图元属性。'''
        for attr, getter in self._valueGetters.items():
            try:
                self._item.itemAttributes[attr] = getter()  # 更新图元属性
            except ValueError:
                QMessageBox.warning(
                    self, 'Input Error',
                    f'The value for attribute "{
                        self._item.itemAttributes.getAttributesInfo(
                            attr)['title']}" is invalid. Skipping.',
                    QMessageBox.Ok)
        super().accept()
