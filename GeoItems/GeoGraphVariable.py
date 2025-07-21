'''GeoGrapher变量图元
'''

from .GeoGraphItem import GeoGraphItem
from .GeoBasicItems import GeoVariable

__all__ = ['GeoGraphVariable']


class GeoGraphVariable(GeoGraphItem):
    '''变量图元类。变量图元是虚图元，不显示于场景中。
    '''

    def __init__(self):
        '''初始化变量图元。
        '''
        super().__init__()
        self.instance = GeoVariable()

    def get(self):
        '''获取变量图元的值。
        '''
        return self.instance.get()

    def set(self, val):
        '''设置变量图元的值。
        '''
        self.instance.set(val)
