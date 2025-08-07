'''基础变量图元
'''

from .GeoBasicItems import GeoItem

__all__ = ['GeoVariable']


class GeoVariable(GeoItem):
    '''基础变量图元类。
    '''

    def __init__(self):
        '''初始化基础变量图元。
        '''
        super().__init__()
        self._var = 0  # 图元值

    def get(self):
        '''获取变量图元的值。
        '''
        return self._var

    def set(self, val):
        '''设置变量图元的值。
        '''
        self._var = val
