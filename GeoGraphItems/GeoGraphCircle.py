'''GeoGrapher圆图元
'''

from PyQt5.QtGui import QPainterPath
from PyQt5.QtCore import QPointF, QLineF

from .GeoGraphItem import GeoGraphPathItem
from .GeoGraphPoint import GeoGraphPoint
from .GeoItems import GeoCircle

__all__ = ['GeoGraphCircle']


class GeoGraphCircle(GeoGraphPathItem):
    '''圆图元类。圆图元由圆心与圆上一点定义。
    '''

    def __init__(self):
        '''初始化圆图元。
        '''
        super().__init__()
        self.instance = GeoCircle()
        self.typePatterns = [[GeoGraphPoint, GeoGraphPoint],]

    def rawShape(self):
        '''原始路径形状，不具有选中范围。
        圆图元的路径形状仅包含圆周附近，而不包含圆内。
        '''
        firstPosX = self._masters[0].x()
        firstPosY = self._masters[0].y()
        secondPos = self._mousePos() \
            if len(self._masters) == 1 else self._masters[1].pos()
        radius = QLineF(self._masters[0].pos(), secondPos).length()
        path = QPainterPath(QPointF(firstPosX + radius, firstPosY))
        # 画两次弧，以保证圆图元不包含圆内部分
        path.arcTo(
            firstPosX - radius, firstPosY - radius,
            radius * 2, radius * 2, 0, 360)
        path.moveTo(firstPosX + radius, firstPosY)
        path.arcTo(
            firstPosX - radius, firstPosY - radius,
            radius * 2, radius * 2, 0, 360)
        return path
