'''GeoGrapher点图元的标签
'''

from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

from .GeoGraphItem import GeoGraphItem
from .Core import GeoItem

__all__ = ['GeoGraphPointLabel']


class GeoGraphPointLabel(QGraphicsTextItem, GeoGraphItem):
    '''点图元标签类，是点图元旁的标签。
    '''

    def __init__(self, parent):
        '''初始化点图元标签。

        :param parent: 待标记的点图元。
        :type parent: GeoGrapher.GeoItems.GeoGraphPoint.GeoGraphPoint
        :param label: 标签内容。
        :type label: str
        '''
        super().__init__()
        self.instance = GeoItem()
        self.setParentItem(parent)
        self.pointLabelsManager = self._label = None
        self._realx = 0.   # 实际中心横坐标
        self._realy = 18.  # 实际中心纵坐标
        self.setTextInteractionFlags(Qt.TextEditorInteraction)  # 可编辑的标签
        self.setDefaultTextColor(QColor(0, 0, 0))  # 字体颜色
        self.setCursor(Qt.IBeamCursor)             # 鼠标样式
        self.setFlag(self.ItemStacksBehindParent)  # 标签位于点图元下方
        font = QFont()
        font.setPointSizeF(18.)  # 初始字号
        self.setFont(font)

    def zoomScaleChanged(self, zoomChange):
        '''当视图放缩比例改变时更新字体大小和与点图元的相对位置。
        '''
        super().zoomScaleChanged(zoomChange)
        font = self.font()
        font.setPointSizeF(font.pointSizeF() / zoomChange)
        self.setFont(font)
        self._realx /= zoomChange
        self._realy /= zoomChange
        self._updatePos()

    def setLabel(self, label=None):
        '''设置标签。
        '''
        if label is None:  # 在`.GeoGraphPoint`中初次设置时保存标签管理器
            self.pointLabelsManager = self.scene().pointLabelsManager
            self._label = next(self.pointLabelsManager)
            self.pointLabelsManager.addLabel(self._label)
            self.setPlainText(self._label)
            return True
        if self.pointLabelsManager.setLabel(self.toPlainText(), label):
            self.setPlainText(label)
            return True
        return False

    def _updatePos(self):
        '''以文字中心坐标为原点修改位置。
        '''
        self.setPos(
            self._realx - self.boundingRect().width() / 2,
            self._realy - self.boundingRect().height() / 2)

    def setPlainText(self, text):
        '''设置文字，并以文字中心坐标为原点修改位置。
        '''
        super().setPlainText(text)
        self._updatePos()  # 使标签以文字中心坐标为原点

    def focusInEvent(self, event):
        '''聚焦时，缓存当前标签。
        '''
        super().focusInEvent(event)
        self._label = self.toPlainText()

    def focusOutEvent(self, event):
        '''取消聚焦时，判断修改的标签是否合法。
        若不合法，则将修改的标签重新改为缓存的原标签（`self._label`）。
        '''
        super().focusOutEvent(event)
        if not self.pointLabelsManager.setLabel(
                self._label, self.toPlainText()):
            self.setPlainText(self._label)  # 改回原标签
        else:
            self._updatePos()  # 文字更新后，使标签以文字中心坐标为原点
