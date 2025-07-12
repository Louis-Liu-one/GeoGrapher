'''基础图元
'''

from .GeoBasicItems import GeoSegment, GeoCircle
from .GeoPoint import GeoPoint, GeoIntersection
from .GeoVariable import GeoVariable

__all__ = [
    'GeoItems', 'GeoSegment', 'GeoCircle',
    'GeoPoint', 'GeoIntersection',
    'GeoVariable',
]


class GeoItems:
    '''基础图元管理类。
    '''

    def __init__(self):
        '''初始化基础图元管理。
        '''
        self._items = []

    def addItem(self, item):
        '''添加基础图元。

        :param item: 待添加的图元。
        :type item: GeoGrapher.GeoItems.GeoBasicItems.GeoItem
        '''
        self._items.append(item)

    def removeItem(self, item):
        '''删除基础图元。

        :param item: 待删除的图元。
        :type item: GeoGrapher.GeoItems.GeoBasicItems.GeoItem
        '''
        if item in self._items:
            self._items.remove(item)
            item.remove()
            # 删除图元的子图元
            for child in item.children():
                self.removeItem(child)
