'''GeoGrapher线段图元
'''

from PyQt5.QtGui import QPainterPath

from .GeoGraphItem import GeoGraphPathItem
from .GeoGraphPoint import GeoGraphPoint
from .GeoItems import GeoSegment

__all__ = ['GeoGraphSegment']


class GeoGraphSegment(GeoGraphPathItem):
    '''线段图元类。线段图元由两端点定义。
    '''

    def __init__(self):
        '''初始化线段图元。
        '''
        super().__init__()
        self.instance = GeoSegment()
        self.typePatterns = [[GeoGraphPoint, GeoGraphPoint],]

    def rawShape(self):
        '''原始路径形状，不具有选中范围。
        '''
        path = QPainterPath(self._masters[0].pos())
        path.lineTo(
            self._mousePos() if len(self._masters) == 1
            else self._masters[1].pos())
        return path
