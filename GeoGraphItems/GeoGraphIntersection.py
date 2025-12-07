'''GeoGrapher交点图元
'''

from .GeoGraphPoint import GeoGraphPoint
from .GeoGraphSegment import GeoGraphSegment
from .GeoGraphCircle import GeoGraphCircle
from .Core import GeoIntersection

__all__ = ['GeoGraphIntersection']


class GeoGraphIntersection(GeoGraphPoint):
    '''交点图元类。
    '''

    def __init__(self):
        '''初始化交点图元。
        '''
        super().__init__()
        self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemSendsGeometryChanges, False)
        self.isUpdatable = False
        self.isFree = False     # 非自由点
        self.isIntersec = True  # 是交点
        self.instance = GeoIntersection()
        self.typePatterns = {
            (GeoGraphSegment, GeoGraphSegment),
            (GeoGraphCircle, GeoGraphSegment),
            (GeoGraphSegment, GeoGraphCircle),
            (GeoGraphCircle, GeoGraphCircle),}

    def _addFirstMaster(self, master):
        '''为本图元添加第一个父图元。子类可在此处作一些特殊处理。
        '''
        self.addMaster(master)
