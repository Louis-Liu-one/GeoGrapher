'''GeoGrapher点图元的标签
'''

from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtGui import QFont, QColor, QPainterPath
from PyQt5.QtCore import Qt, QRectF

from .GeoGraphItem import GeoGraphItem
from .Core import GeoItem


class GeoGraphPointLabel(QGraphicsTextItem, GeoGraphItem):
    '''点图元标签类，是点图元旁的标签。
    '''

    def __init__(self, parent, label='A'):
        '''初始化点图元标签。

        :param parent: 待标记的点图元。
        :type parent: GeoGrapher.GeoItems.GeoGraphPoint.GeoGraphPoint
        :param label: 标签内容。
        :type label: str
        '''
        super().__init__()
        self.instance = GeoItem()
        self.setParentItem(parent)
        self.setPos(3, 3)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)  # 可编辑的标签
        self.setDefaultTextColor(QColor(0, 0, 0))
        self.setPlainText(label)
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
        dist = self.pos().x() / zoomChange
        self.setPos(dist, dist)
