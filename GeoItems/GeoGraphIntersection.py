'''GeoGrapher交点图元
'''

from .GeoGraphPoint import GeoGraphPoint
from .GeoBasicItems import GeoIntersection

__all__ = ['GeoGraphIntersection']


class GeoGraphIntersection(GeoGraphPoint):
    '''交点图元类。
    '''

    def __init__(self, master):
        '''初始化交点图元。

        :param master: 交点图元的第一个父图元，可为None。
        :type master: GeoGrapher.GeoItems.GeoGraphItem.GeoGraphItem
        '''
        super().__init__(master)
        self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemSendsGeometryChanges, False)
        self.isFree = False     # 非自由点
        self.isIntersec = True  # 是交点
        self.instance = GeoIntersection(master.instance)
