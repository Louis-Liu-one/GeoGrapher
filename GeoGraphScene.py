'''GeoGrapher绘制场景
'''

from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import QLine

from .GeoGraphItems.Core import GeoItemsManager

__all__ = ['GeoGraphScene']


class GeoGraphScene(QGraphicsScene):
    '''GeoGrapher绘制场景。
    使用方法与`PyQt5.QtWidgets.QGraphicsScene`基本相同。
    '''

    def __init__(
            self, parent=None,
            darkGridSize=128, darkPenColor='#c0c0c0', darkPenWidth=1.2,
            lightGridSize=32, lightPenColor='#d0d0d0', lightPenWidth=.5,
            backgroundColor='#f1f1f1'):
        '''初始化场景。

        :param parent: 父控件。
        :type parent: PyQt5.QtWidgets.QWidget
        :param darkGridSize: 深色网格大小。
        :type darkGridSize: int
        :param darkPenColor: 深色网格颜色。
        :type darkPenColor: str
        :param darkPenWidth: 深色网格粗细。
        :type darkPenWidth: float
        :param lightGridSize: 浅色网格大小。
        :type lightGridSize: int
        :param lightPenColor: 浅色网格颜色。
        :type lightPenColor: str
        :param lightPenWidth: 浅色网格粗细。
        :type lightPenWidth: float
        :param backgroundColor: 背景颜色。
        :type backgroundColor: str
        '''
        super().__init__(parent)
        self.lightGridSize, self.darkGridSize = lightGridSize, darkGridSize
        self.zoomScale = 1.        # 当前放缩比例
        self.tempScale = 1.        # 缓存放缩比例，用于管理网格宽度
        self.itemsManager = GeoItemsManager()  # 统一管理基础图元
        self._penDark = QPen(QColor(darkPenColor), darkPenWidth)     # 深色画笔
        self._penLight = QPen(QColor(lightPenColor), lightPenWidth)  # 浅色画笔
        self.setBackgroundBrush(QColor(backgroundColor))

    def drawBackground(self, painter, rect):
        '''绘制背景网格。
        '''
        super().drawBackground(painter, rect)
        left = int(rect.left()) - int(rect.left()) % self.lightGridSize
        top = int(rect.top()) - int(rect.top()) % self.lightGridSize
        right, bottom = int(rect.right()), int(rect.bottom())
        linesDark, linesLight = [], []
        for i in range(top, bottom, self.lightGridSize):
            (linesLight if i % self.darkGridSize
                else linesDark).append(QLine(left, i, right, i))
        for i in range(left, right, self.lightGridSize):
            (linesLight if i % self.darkGridSize
                else linesDark).append(QLine(i, bottom, i, top))
        painter.setPen(self._penLight)
        if linesLight:
            painter.drawLines(*linesLight)
        painter.setPen(self._penDark)
        if linesDark:
            painter.drawLines(*linesDark)

    def zoomScaleChanged(self, zoomChange):
        '''放缩比例变化。

        :param zoomChange: 新放缩比例与原放缩比例的比值。
        :type zoomChange: float
        '''
        # 更新网格画笔宽度
        self._penDark.setWidthF(
            self._penDark.widthF() / zoomChange)
        self._penLight.setWidthF(
            self._penLight.widthF() / zoomChange)
        self.zoomScale *= zoomChange
        self.tempScale *= zoomChange
        # 更新网格宽度
        while self.tempScale >= 2 and self.lightGridSize % 2 == 0:
            self.tempScale /= 2
            self.lightGridSize //= 2
            self.darkGridSize //= 2
        while self.tempScale <= .5:
            self.tempScale *= 2
            self.lightGridSize *= 2
            self.darkGridSize *= 2
        for item in self.items():
            item.zoomScaleChanged(zoomChange)

    def addItem(self, item):
        '''添加图元。

        :param item: 待添加的图元。
        :type item: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        super().addItem(item)
        item.zoomScaleChanged(self.zoomScale)
        self.itemsManager.addItem(item.instance)  # 添加基础图元

    def removeItem(self, item):
        '''删除图元。

        :param item: 待删除的图元。
        :type item: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        super().removeItem(item)
        item.isAvailable = False
        for master in item.masters():
            master.removeChild(item)  # 从所有父图元中删除图元
        self.itemsManager.removeItem(item.instance)  # 删除基础图元
        item.instance = None
