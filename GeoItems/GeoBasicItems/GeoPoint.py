'''基础点图元及相关图元
'''

from decimal import Decimal
from PyQt5.QtCore import QPointF
from .GeoBasicItems import GeoItem, GeoSegment, GeoCircle

__all__ = ['GeoPoint', 'GeoIntersection']


class GeoPoint(GeoItem):
    '''基础点图元类。
    '''

    def __init__(self, master=None, x=None, y=None):
        '''初始化基础点图元。

        :param master: 第一个父图元，可为None。
        :type master: GeoGrapher.GeoItems.GeoBasicItems.GeoItem
        :param x: 动态返回点的横坐标的函数。
        :type x: typing.Callable[[], float]
        :param y: 动态返回点的纵坐标的函数。
        :type y: typing.Callable[[], float]
        '''
        super().__init__(master)
        self._x, self._y = x, y

    def _xRaw(self):
        '''图元的原始横坐标。
        '''
        return Decimal(self._x())

    def _yRaw(self):
        '''图元的原始纵坐标。
        '''
        return Decimal(self._y())

    def _pointRaw(self):
        '''图元的原始点。
        '''
        return GeoPoint(x=self._xRaw, y=self._yRaw)

    def pos(self):
        '''图元的坐标。若在路径上，则为原始坐标在路径上的投影，否则为原始坐标。

        :returns: 图元坐标。
        :rtype: tuple[decimal.Decimal, decimal.Decimal]
        '''
        if self._masters:
            return self._footPointRaw(self._masters[0])
        return self._xRaw(), self._yRaw()

    def distanceTo(self, item):
        '''点到指定图元的距离。
        对于点，距离为两点欧氏距离；
        对于直线和圆，距离为点到直线或圆上一点的最短距离。
        '''
        if isinstance(item, GeoPoint):      # 点
            return self.distanceToXY(*item.pos())
        elif isinstance(item, GeoSegment):  # 直线
            return self.distanceToLabc(*item.abc())
        elif isinstance(item, GeoCircle):   # 圆
            return abs(self.distanceTo(item.o()) - item.r())

    def distanceToXY(self, x, y, sx=None, sy=None):
        '''点(sx, sy)到(x, y)的距离。
        若sx、sy未指定，则为自身坐标。
        '''
        if sx is None or sy is None:
            sx, sy = self.pos()
        return ((x - sx) ** 2 + (y - sy) ** 2).sqrt()

    def distanceToLabc(self, a, b, c, sx=None, sy=None):
        '''点(sx, sy)到直线的距离。直线由ax + by + c = 0定义。
        若sx、sy未指定，则为自身坐标。
        '''
        if sx is None or sy is None:
            sx, sy = self.pos()
        k = (a ** 2 + b ** 2).sqrt()
        return Decimal('NaN') if k == 0 else abs(a * sx + b * sy + c) / k

    def footPointLabc(self, a, b, c, sx=None, sy=None):
        '''点(sx, sy)在直线ax + by + c = 0上的垂足坐标。
        若sx、sy未指定，则为自身坐标。
        '''
        if sx is None or sy is None:
            sx, sy = self.pos()
        aSquare, bSquare = a ** 2, b ** 2
        k = aSquare + bSquare
        if k == 0:
            return Decimal('NaN'), Decimal('NaN')
        x = bSquare * sx - a * b * sy - a * c
        y = aSquare * sy - a * b * sx - b * c
        return x / k, y / k

    def _footPointRawL(self, line):
        '''原始点在直线上的垂足坐标。

        :param line: 给定直线。
        :type line: GeoGrapher.GeoItems.GeoBasicItems.GeoSegment
        :returns: 垂足坐标。
        :rtype: tuple[decimal.Decimal, decimal.Decimal]
        '''
        a, b, c = line.abc()
        return self.footPointLabc(a, b, c, self._xRaw(), self._yRaw())

    def _footPointRawC(self, circle):
        '''原始点在圆上的垂足坐标，定义为圆周上一点，使得该点到原始点距离最短。

        :param circle: 给定圆。
        :type line: GeoGrapher.GeoItems.GeoBasicItems.GeoCircle
        :returns: 垂足坐标。
        :rtype: tuple[decimal.Decimal, decimal.Decimal]
        '''
        d = self._pointRaw().distanceTo(circle.o())
        if d == 0:
            return Decimal('NaN'), Decimal('NaN')
        ox, oy = circle.o().pos()
        dx, dy = self._xRaw() - ox, self._yRaw() - oy
        return circle.r() / d * dx + ox, circle.r() / d * dy + oy

    def _footPointRaw(self, item):
        '''原始点在路径上的垂足坐标。
        参见``GeoGrapher.GeoItems.GeoBasicItems.GeoPoint._footPointL()``
        与``GeoGrapher.GeoItems.GeoBasicItems.GeoPoint._footPointC()``。
        '''
        if isinstance(item, GeoSegment):
            return self._footPointRawL(item)
        elif isinstance(item, GeoCircle):
            return self._footPointRawC(item)
        return Decimal('NaN'), Decimal('NaN')

    def _leftPointFirst(self, x1, y1, x2, y2):
        '''将两点排序，使得两点中横坐标较小的点优先。
        若横坐标相同，则纵坐标较大的点优先。
        优先的点称为两点中的左点，另一点称为两点中的右点。

        :returns: 排序后的点。
        :rtype: tuple[
            decimal.Decimal, decimal.Decimal,
            decimal.Decimal, decimal.Decimal]
        '''
        if x1 < x2:
            return x1, y1, x2, y2
        if x1 > x2:
            return x2, y2, x1, y1
        if y1 > y2:
            return x1, y1, x2, y2
        return x2, y2, x1, y1

    def toQPointF(self):
        '''将本图元转换为PyQt5.QtCore.QPointF。
        '''
        x, y = self.pos()
        return QPointF(float(x), float(y))


class GeoIntersection(GeoPoint):
    '''基础交点图元类。
    '''

    def __init__(self, master):
        '''初始化基础交点图元。

        :param master: 第一个父图元。若与自身类型相同，则复制到自身。
        :type master: GeoGrapher.GeoItems.GeoBasicItems.GeoItem
        '''
        if isinstance(master, GeoIntersection):  # 复制到自身
            self._masters = master.masters()
            self._children = master.children()
            for item in self._masters:
                item.addChild(self)
        else:
            super().__init__(master)

    def _posLL(self):
        '''两直线交点坐标。
        '''
        if len(self._masters) != 2:
            return Decimal('NaN'), Decimal('NaN')
        a1, b1, c1 = self._masters[0].abc()
        a2, b2, c2 = self._masters[1].abc()
        k = a1 * b2 - a2 * b1
        if k != 0:
            return (b1 * c2 - b2 * c1) / k, (a2 * c1 - a1 * c2) / k
        return Decimal('NaN'), Decimal('NaN')

    def posCAll(self):
        '''直线与圆两交点坐标，或两圆交点坐标。未定义返回两NaN。

        :returns: 两交点。
        :rtype: tuple[
            tuple[decimal.Decimal, decimal.Decimal],
            tuple[decimal.Decimal, decimal.Decimal]]
        '''
        if isinstance(self._masters[0], GeoCircle):
            self._masters.reverse()
        a, b, c = self._masters[0].abc()
        o, r = self._masters[1].o(), self._masters[1].r()
        ox, oy = o.pos()
        hx, hy = o.footPointLabc(a, b, c, ox, oy)
        h = o.distanceToLabc(a, b, c, ox, oy)
        d = r ** 2 - h ** 2
        absq = a ** 2 + b ** 2
        if d < 0 or absq == 0:
            return Decimal('NaN'), Decimal('NaN')
        sq = (d / absq).sqrt()
        dx, dy = -b * sq, a * sq
        i1x, i1y, i2x, i2y = hx + dx, hy + dy, hx - dx, hy - dy
        if hy >= oy:
            x1, y1, x2, y2 = self._leftPointFirst(i1x, i1y, i2x, i2y)
        else:
            x2, y2, x1, y1 = self._leftPointFirst(i1x, i1y, i2x, i2y)
        return (x1, y1), (x2, y2)

    def _posLC(self):
        '''直线与圆其中一个交点的坐标，由第3个父图元的值决定。
        若圆心在直线上的投影的纵坐标大于或等于圆心纵坐标，则返回两交点中的左点；
        反之，则返回两交点中的右点。
        左点与右点参见``self._leftPointFirst()``。
        '''
        if len(self._masters) != 3:
            return Decimal('NaN'), Decimal('NaN')
        return self.posCAll()[self._masters[2].get() - 1]

    def pos(self):
        '''交点坐标。

        :returns: 交点的坐标。未定义返回两NaN。
        :rtype: tuple[decimal.Decimal, decimal.Decimal]
        '''
        if isinstance(self._masters[0], GeoSegment) \
                and isinstance(self._masters[1], GeoSegment):
            return self._posLL()  # 两直线
        elif isinstance(self._masters[0], GeoSegment) \
                and isinstance(self._masters[1], GeoCircle) \
                or isinstance(self._masters[0], GeoCircle) \
                and isinstance(self._masters[1], GeoSegment):
            return self._posLC()  # 直线与圆
        return Decimal('NaN'), Decimal('NaN')
