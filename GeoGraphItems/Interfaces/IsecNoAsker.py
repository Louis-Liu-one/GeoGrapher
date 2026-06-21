'''交点编号询问对话框
'''

from PyQt5.QtWidgets import QVBoxLayout, QFormLayout
from PyQt5.QtWidgets import QDialog, QSpinBox, QDialogButtonBox
from PyQt5.QtCore import Qt

__all__ = ['IsecNoAskerDialog']


class IsecNoAskerDialog(QDialog):
    '''用于询问交点编号的应用程序模态对话框。
    '''

    def __init__(self, parent=None, title=''):
        '''初始化对话框。
        '''
        super().__init__(parent)
        self._initUi()
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)

    def _initUi(self):
        '''初始化界面。
        '''
        formLayout = QFormLayout()
        self._resultBox = QSpinBox()
        self._resultBox.setRange(1, 2)
        formLayout.addRow('Intersection Number:', self._resultBox)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def result(self):
        '''获取交点编号的值。
        '''
        return self._resultBox.value()
