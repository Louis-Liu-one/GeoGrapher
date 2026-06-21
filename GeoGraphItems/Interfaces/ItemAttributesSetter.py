'''图元属性设置对话框
'''

from PyQt5.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QFormLayout
from PyQt5.QtWidgets import (
    QLineEdit, QSpinBox, QDoubleSpinBox, QDialogButtonBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QPointF

from .FormUtils import IntValueSliderSelector, ColorSelector

__all__ = ['ItemAttributesSetterDialog']


class ItemAttributesSetterDialog(QDialog):
    '''图元属性设置对话框。
    '''

    def __init__(self, parent=None, item=None, title='Set Item Attributes'):
        '''初始化对话框。
        '''
        super().__init__(parent)
        self._item = item
        self._initUi()
        self._adjustPosition()
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowTitle(title.capitalize())

    def _initUi(self):
        '''初始化界面。
        '''
        formLayout = QFormLayout()
        # 在此添加界面元素
        self._valueGetters = {}    # 存储属性值获取函数的字典，便于后续获取当前属性值
        for attr, value in self._item.itemAttributes.items():
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
                continue  # 不支持的属性类型，跳过
            formLayout.addRow(attrInfo['title'] + ':', attributeBox)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.adjustSize()

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
                            attr)["title"]}" is invalid. Skipping.',
                    QMessageBox.Ok)
        super().accept()
