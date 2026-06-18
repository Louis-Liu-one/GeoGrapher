
from PyQt5.QtWidgets import QVBoxLayout, QFormLayout
from PyQt5.QtWidgets import QLineEdit, QDialogButtonBox
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import Qt, QPointF

__all__ = ['ItemAttributesSetterDialog']


class ItemAttributesSetterDialog(QDialog):
    '''图元属性设置对话框。
    '''

    def __init__(self, parent=None, item=None, title='设置图元属性'):
        '''初始化对话框。
        '''
        super().__init__(parent)
        self._item = item
        self._initUi()
        self._adjustPosition()
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowTitle(title)

    def _initUi(self):
        '''初始化界面。
        '''
        formLayout = QFormLayout()
        # 在此添加界面元素
        self._attributeBoxes = {}  # 存储属性输入框的字典，便于后续获取输入值
        for attr, value in self._item.itemAttributes.items():
            attrInfo = self._item.itemAttributes.getAttributesInfo(attr)
            attributeBox = QLineEdit(str(value))
            formLayout.addRow(attrInfo['title'] + ':', attributeBox)
            self._attributeBoxes[attr] = attributeBox

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Cancel)
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

    def result(self):
        '''获取设置的属性值。'''
        return {attr: box.text() for attr, box in self._attributeBoxes.items()}

    def accept(self):
        '''确认设置，更新图元属性。'''
        for attr, box in self._attributeBoxes.items():
            try:
                self._item.itemAttributes[attr] = box.text()  # 更新图元属性
            except ValueError:
                QMessageBox.warning(
                    self, '输入错误', f'属性“{attr}”的值无效，默认跳过。', QMessageBox.Ok)
        super().accept()
