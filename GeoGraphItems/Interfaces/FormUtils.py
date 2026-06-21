'''一些表单组件的工具类
'''

from PyQt5.QtWidgets import QWidget, QColorDialog, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QSlider, QSpinBox, QPushButton, QFrame
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

__all__ = ['IntValueSliderSelector', 'ColorSelector']


class IntValueSliderSelector(QWidget):
    '''整数值滑动选择器，包含一个水平滑动条和一个数值框，二者联动。
    '''

    def __init__(self, parent=None):
        '''初始化选择器。
        '''
        super().__init__(parent)
        self._slider = QSlider(Qt.Horizontal)
        self._spin = QSpinBox()
        self.setValue = self._spin.setValue
        self.value = self._spin.value

        lay = QVBoxLayout(self)
        lay.addWidget(self._slider)
        lay.addWidget(self._spin)
        self._slider.valueChanged.connect(self._onSliderValueChanged)
        self._spin.valueChanged.connect(self._onSpinValueChanged)

    def setRange(self, minVal, maxVal):
        '''设置选择器的取值范围。
        '''
        self._slider.setRange(int(minVal), int(maxVal))
        self._spin.setRange(int(minVal), int(maxVal))

    def setMinimum(self, minVal):
        '''设置选择器的最小值。
        '''
        self._slider.setMinimum(int(minVal))
        self._spin.setMinimum(int(minVal))

    def setMaximum(self, maxVal):
        '''设置选择器的最大值。
        '''
        self._slider.setMaximum(int(maxVal))
        self._spin.setMaximum(int(maxVal))

    def _onSpinValueChanged(self, value):
        '''当数值框的值改变时更新滑动条的值。
        '''
        if self._slider.value() != value:
            self._slider.setValue(value)

    def _onSliderValueChanged(self, value):
        '''当滑动条的值改变时更新数值框的值。
        '''
        if self._spin.value() != value:
            self._spin.setValue(value)


class ColorSelector(QWidget):
    '''颜色选择器，包含一个颜色显示框和一个按钮，点击按钮弹出颜色选择对话框。
    '''

    def __init__(
            self, parent=None,
            buttonText='Choose Color', dialogTitle='Choose Color'):
        '''初始化选择器。
        '''
        super().__init__(parent)
        self._color = QColor('#ffffff')  # 默认白色
        self._dialogTitle = dialogTitle
        self._initUi(buttonText=buttonText)

    def _initUi(self, buttonText='Choose Color'):
        '''初始化界面。
        '''
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # 颜色预览色块
        self._colorDisplayFrame = QFrame()
        self._colorDisplayFrame.setFixedSize(32, 24)
        self._colorDisplayFrame.setFrameShape(QFrame.Box)
        self._updateFrameBackground()

        # 打开颜色选择器按钮
        self._colorPickerButton = QPushButton(buttonText.capitalize())
        self._colorPickerButton.clicked.connect(self._openColorPickerDialog)

        layout.addWidget(self._colorDisplayFrame)
        layout.addWidget(self._colorPickerButton)

    def _updateFrameBackground(self):
        '''刷新预览色块的背景。
        '''
        self._colorDisplayFrame.setStyleSheet(
            f'background-color: {self._color.name()}; border: 1px solid #999;'
        )

    def _openColorPickerDialog(self):
        '''弹出颜色选择窗口。
        '''
        new_color = QColorDialog.getColor(self._color, self, self._dialogTitle)
        if new_color.isValid():
            self._color = new_color
            self._updateFrameBackground()

    def value(self):
        '''返回当前选择的颜色。

        :returns: 当前选择的颜色。
        :rtype: PyQt5.QtGui.QColor
        '''
        return self._color

    def setValue(self, color):
        '''设置颜色。

        :param color: 要设置的颜色。
        :type color: PyQt5.QtGui.QColor
        '''
        if isinstance(color, QColor) and color.isValid():
            self._color = color
            self._updateFrameBackground()
