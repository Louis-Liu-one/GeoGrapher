'''一些表单组件的工具类
'''

from PySide6.QtWidgets import QWidget, QColorDialog, QVBoxLayout
from PySide6.QtWidgets import QSlider, QSpinBox, QFrame
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

__all__ = ['IntValueSliderSelector', 'ColorSelector']


class IntValueSliderSelector(QWidget):
    '''整数值滑动选择器，包含一个水平滑动条和一个数值框，二者联动。
    '''

    def __init__(self, parent=None):
        '''初始化选择器。
        '''
        super().__init__(parent)
        self._slider: QSlider = QSlider(Qt.Orientation.Horizontal)
        self._spin: QSpinBox = QSpinBox()

        layout = QVBoxLayout(self)
        layout.addWidget(self._slider)
        layout.addWidget(self._spin)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._slider.valueChanged.connect(self._onSliderValueChanged)
        self._spin.valueChanged.connect(self._onSpinValueChanged)

        self.setStyleSheet('QSlider::handle { background: transparent; }')

    def setValue(self, value: int):
        '''设置选择器的当前值。
        '''
        self._spin.setValue(int(value))

    def value(self) -> int:
        '''返回选择器的当前值。
        '''
        return self._spin.value()

    def setRange(self, minVal: int, maxVal: int):
        '''设置选择器的取值范围。
        '''
        self._slider.setRange(int(minVal), int(maxVal))
        self._spin.setRange(int(minVal), int(maxVal))

    def setMinimum(self, minVal: int):
        '''设置选择器的最小值。
        '''
        self._slider.setMinimum(int(minVal))
        self._spin.setMinimum(int(minVal))

    def setMaximum(self, maxVal: int):
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


class ColorSelector(QFrame):
    '''颜色选择器，包含一个颜色显示框，点击展示框时弹出颜色选择对话框。
    '''

    def __init__(self, parent=None, dialogTitle: str = 'Choose Color'):
        '''初始化选择器。
        '''
        super().__init__(parent)
        self._color: QColor = QColor('#ffffff')  # 默认白色
        self._dialogTitle: str = dialogTitle
        self._initUi()

    def _initUi(self):
        '''初始化界面。
        '''
        # 颜色预览色块
        self.setFixedHeight(24)
        self.setFrameShape(QFrame.Shape.Box)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._updateBackground()

    def mousePressEvent(self, event):
        '''鼠标点击事件，弹出颜色选择对话框。
        '''
        if event.button() == Qt.MouseButton.LeftButton:
            self._openColorPickerDialog()
        super().mousePressEvent(event)

    def _updateBackground(self):
        '''刷新预览色块的背景。
        '''
        self.setStyleSheet(
            f'background-color: {self._color.name()}; border: 1px solid #999;'
        )

    def _openColorPickerDialog(self):
        '''弹出颜色选择窗口。
        '''
        new_color = QColorDialog.getColor(self._color, self, self._dialogTitle)
        if new_color.isValid():
            self._color = new_color
            self._updateBackground()

    def value(self) -> QColor:
        '''返回当前选择的颜色。
        '''
        return self._color

    def setValue(self, color: QColor):
        '''设置选择器颜色。
        '''
        if isinstance(color, QColor) and color.isValid():
            self._color = color
            self._updateBackground()
