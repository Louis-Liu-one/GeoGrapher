'''一些基础图元
'''

from decimal import Decimal

__all__ = ['GeoItem', 'GeoSegment', 'GeoCircle']


class GeoItem:
    '''所有基础图元类的基类。
    '''

    def __init__(self):
        '''初始化基础图元。
        '''
        self._children = []
        self._masters = []
        self._noMasters = True

    def addMaster(self, master):
        '''添加父图元，并将自身添加为父图元的子图元。
        '''
        if self._noMasters:
            self._noMasters = False
            self._addFirstMaster(master)
        else:
            self._masters.append(master)
            master.addChild(self)

    def _addFirstMaster(self, master):
        '''添加第一个父图元。子类可在此处作一些特殊处理。
        '''
        self.addMaster(master)

    def addChild(self, child):
        '''添加子图元。
        '''
        if child not in self._children:
            self._children.append(child)

    def removeChild(self, child):
        '''删除子图元。
        '''
        if child in self._children:
            self._children.remove(child)

    def masters(self):
        '''父图元。
        '''
        return self._masters

    def children(self):
        '''子图元。
        '''
        return self._children

    def remove(self):
        '''从所有的父图元删除自身。
        '''
        for master in self._masters:
            master.removeChild(self)


class GeoSegment(GeoItem):
    '''基础线段图元类。线段图元由两端点定义。
    两端点为(x1, y1)、(x2, y2)，直线表达式为ax + by + c = 0。
    '''

    def abc(self):
        '''同时返回直线表达式中的x项系数、y项系数、常数项。
        '''
        if len(self._masters) == 2:
            x1, y1 = self._masters[0].pos()
            x2, y2 = self._masters[1].pos()
            return y2 - y1, x1 - x2, x2 * y1 - x1 * y2
        return Decimal('NaN'), Decimal('NaN'), Decimal('NaN')


class GeoCircle(GeoItem):
    '''基础圆图元类。圆图元由圆心与圆上一点定义。
    '''

    def o(self):
        '''圆心。
        '''
        if len(self._masters):
            return self._masters[0]

    def r(self):
        '''半径。
        '''
        if len(self._masters) == 2:
            return self.o().distanceTo(self._masters[1])
