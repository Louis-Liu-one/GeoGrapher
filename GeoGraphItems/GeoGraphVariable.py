'''GeoGrapher变量图元
'''

import math
import functools

from .GeoGraphItem import GeoGraphItem
from .Core import GeoIntVar

__all__ = [
    'GeoGraphVariable', 'GeoGraphVarClass',
    'GeoGraphIntVar', 'GeoGraphIsecNoVar',
    'judgeFuncForReal', 'GeoIntVar']


class GeoGraphVariable(GeoGraphItem):
    '''变量图元类。变量图元是虚图元，不显示于场景中。
    '''

    def __init__(self, insType, default, judgeFunc=None):
        '''创建变量图元。

        :param insType: 基础图元的类型。在`.Core`中定义。
        :type insType: GeoGrapher.GeoGraphItems.Core.GeoItem
        :param default: 变量初始值。将作为参数传入`insType.__init__()`。
        :type default: object
        :param judgeFunc: 传入一个参数`val`、返回布尔值的函数，
                          判断`val`可否设置为变量图元的值。若为`None`，则无限制。
        :type judgeFunc: typing.Callable[[object], bool]
        '''
        super().__init__()
        self.instance = insType(default)
        self._judgeFunc = judgeFunc

    def get(self):
        '''获取变量图元的值。
        '''
        return self.instance.get()

    def set(self, val):
        '''设置变量图元的值。
        '''
        if self._judgeFunc is None or self._judgeFunc(val):
            self.instance.set(val)
            return True
        return False


def GeoGraphVarClass(insType, default, judgeFunc=None):
    '''创建变量图元类。参数参见`.GeoGraphVariable.GeoGraphVariable.__init__()`。
    '''
    return functools.partial(GeoGraphVariable, insType, default, judgeFunc)


def judgeFuncForReal(
        vtype=float, vmin=-math.inf, vmax=math.inf, imin=True, imax=True):
    '''为`.GeoGraphVariable.GeoGraphVariable.__init__()`提供`judgeFunc`参数。
    仅支持整数图元或浮点数图元。

    :param vtype: 图元类型。`int`、`float`及它们的子类。
    :type vtype: type
    :param vmin: 变量最小值。
    :type vmin: int | float
    :param vmax: 变量最大值。
    :type vmax: int | float
    :param imin: 变量可否与最小值相同。
    :type imin: bool
    :param imax: 变量可否与最大值相同。
    :type imax: bool
    :returns: `judgeFunc`函数。
    :rtype: typing.Callable[[object], bool]
    '''
    def judgeFunc(val):
        return isinstance(val, vtype) \
            and (vmin <= val if imin else vmin < val) \
            and (vmax >= val if imax else vmax > val)
    return judgeFunc


GeoGraphIntVar = GeoGraphVarClass(GeoIntVar, 0)  # 整数变量图元
GeoGraphIsecNoVar = GeoGraphVarClass(            # 交点编号变量图元
    GeoIntVar, 1, judgeFuncForReal(int, 1, 2))
