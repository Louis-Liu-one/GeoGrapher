'''基础变量图元
'''

from .GeoBasicItems import GeoItem

__all__ = ['GeoVariable']


class GeoVariable(GeoItem):
    '''基础变量图元类。
    '''

    def __init__(self, master=None):
        '''初始化基础变量图元。

        :param master: 第一个父图元，可为None。
        :type master: GeoGrapher.GeoItems.GeoBasicItems.GeoItem
        '''
        super().__init__(master)
        self._var = 0  # 图元值

    def get(self):
        '''获取变量图元的值。
        '''
        return self._var

    def set(self, val):
        '''设置变量图元的值。
        '''
        self._var = val
