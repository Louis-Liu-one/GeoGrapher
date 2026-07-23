'''GeoGrapher线段图元
'''

from PySide6.QtGui import QPainterPath

from .GeoGraphItem import GeoGraphPathItem
from .GeoGraphPoint import GeoGraphPoint
from .Core import GeoSegment

__all__ = ['GeoGraphSegment']


class GeoGraphSegment(GeoGraphPathItem):
    '''线段图元类。线段图元由两端点定义。
    '''

    def __init__(self):
        '''初始化线段图元。
        '''
        super().__init__()
        self.instance = GeoSegment()
        self.typePatterns = {(GeoGraphPoint, GeoGraphPoint)}

    def __str__(self):
        '''返回线段图元的标识字符串。
        '''
        return f'Segment {self.shortIdentifier()}'

    def shortIdentifier(self):
        '''返回线段图元的简短标识字符串。
        '''
        return f'{self._masters[0].shortIdentifier()
                  }-{self._masters[1].shortIdentifier()}'

    def rawShape(self):
        '''原始路径形状，不具有选中范围。
        '''
        firstPointPos = self.mapFromScene(self._masters[0].pos())
        secondPointPos = self.mapFromScene(
            self._mousePos() if len(self._masters) == 1
            else self._masters[1].pos())
        path = QPainterPath()
        path.moveTo(firstPointPos)
        path.lineTo(secondPointPos)
        return path
