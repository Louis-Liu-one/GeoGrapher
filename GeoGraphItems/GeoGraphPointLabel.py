'''GeoGrapher点图元的标签
'''

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .GeoPointLabelsManager import GeoPointLabelsManager

import math

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
        :type parent: GeoGrapher.GeoGraphItems.GeoGraphPoint.GeoGraphPoint
        :param label: 标签内容。
        :type label: str
        '''
        super().__init__()
        self.instance = GeoItem()
        self.setParentItem(parent)
        self.pointLabelsManager: GeoPointLabelsManager = None
        self._label: str = None
        self._labelDistance = 10.  # 标签与点图元的距离
        self._labelAngle = -45     # 标签相对于点图元的角度
        self.setLabelDistance(self._labelDistance)  # 根据距离和角度设置标签位置
        self.setTextInteractionFlags(Qt.TextEditorInteraction)  # 可编辑的标签
        self.setDefaultTextColor(QColor('#000000'))  # 字体颜色
        self.setCursor(Qt.IBeamCursor)             # 鼠标样式
        self.setFlag(self.ItemStacksBehindParent)  # 标签位于点图元下方
        font = QFont()
        font.setPointSizeF(18.)  # 初始字号
        self.setFont(font)

    def setLabel(self, label: str | None = None) -> bool:
        '''设置标签。
        '''
        if label is None:  # 在`.GeoGraphPoint`中初次设置时保存标签管理器
            self.pointLabelsManager = self.scene().pointLabelsManager
            self._label = next(self.pointLabelsManager)
            self.pointLabelsManager.addLabel(self._label)
            self.setPlainText(self._label)
            return True
        # 向标签管理器请求修改标签，若成功则修改标签内容，否则保持原标签不变
        if self.pointLabelsManager.setLabel(self.toPlainText(), label):
            self.setPlainText(label)
            return True
        return False

    def labelDistance(self) -> float:
        '''获取标签与点图元的距离。
        '''
        return self._labelDistance

    def setLabelDistance(self, distance: float):
        '''设置标签与点图元的距离。
        '''
        self._labelDistance = distance
        angle = math.radians(self._labelAngle)
        self._realx = distance * math.cos(angle)
        self._realy = -distance * math.sin(angle)
        self._updatePos()

    def labelAngle(self) -> float:
        '''获取标签相对于点图元的角度。
        '''
        return self._labelAngle

    def setLabelAngle(self, angle: float):
        '''设置标签相对于点图元的角度。
        '''
        self._labelAngle = int(angle)
        angle = math.radians(angle)
        self._realx = self._labelDistance * math.cos(angle)
        self._realy = -self._labelDistance * math.sin(angle)
        self._updatePos()

    def _updatePos(self):
        '''以文字中心坐标为原点修改位置。
        '''
        angle = self.labelAngle() % 360
        labelWidth = self.boundingRect().width()
        labelHeight = self.boundingRect().height()
        halfWidth, halfHeight = labelWidth / 2, labelHeight / 2

        if 337.5 < angle or angle <= 22.5:  # 右侧附近
            dx, dy = 0, halfHeight
        elif 22.5 < angle <= 67.5:          # 右上附近
            dx, dy = 0, labelHeight
        elif 67.5 < angle <= 112.5:         # 上方附近
            dx, dy = halfWidth, labelHeight
        elif 112.5 < angle <= 157.5:        # 左上附近
            dx, dy = labelWidth, labelHeight
        elif 157.5 < angle <= 202.5:        # 左侧附近
            dx, dy = labelWidth, halfHeight
        elif 202.5 < angle <= 247.5:        # 左下附近
            dx, dy = labelWidth, 0
        elif 247.5 < angle <= 292.5:        # 下方附近
            dx, dy = halfWidth, 0
        else:                               # 右下附近
            dx, dy = 0, 0
        self.setPos(self._realx - dx, self._realy - dy)  # 以文字中心坐标为原点修改位置

    def setPlainText(self, text: str):
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
