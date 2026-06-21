'''GeoGrapher变量图元
'''

import math

from .GeoGraphItem import GeoGraphItem
from .Interfaces.IsecNoAsker import IsecNoAskerDialog
from .Core import GeoIntVar

__all__ = ['GeoGraphVariable', 'GeoGraphIntVar', 'GeoGraphIsecNoVar']


def judgeFuncForReal(
        vtype=float, vmin=-math.inf, vmax=math.inf, imin=True, imax=True):
    '''为`.GeoGraphVariable.GeoGraphVariable.__init__()`提供`judgeFunc`参数。
    仅支持整数或浮点数的判断。

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

    def askValueFromUser(self, view):
        '''询问用户输入，并将其设置为变量图元的值。子类可在此处实现一些特殊的询问方式。

        :returns: 是否成功设置了变量图元的值。默认不询问，直接返回成功。
        :rtype: bool
        '''
        return True  # 默认不询问，直接返回成功


class GeoGraphIntVar(GeoGraphVariable):
    '''整数变量图元类。
    '''

    def __init__(self, default=0, judgeFunc=None):
        '''创建整数变量图元。

        :param default: 变量初始值。默认为`0`。
        :type default: int
        :param judgeFunc: 传入一个参数`val`、返回布尔值的函数，
                          判断`val`可否设置为变量图元的值。若为`None`，则无限制。
        :type judgeFunc: typing.Callable[[object], bool]
        '''
        super().__init__(GeoIntVar, default, judgeFunc)


class GeoGraphIsecNoVar(GeoGraphIntVar):
    '''交点编号变量图元类。交点编号变量图元的值仅能为`1`或`2`。
    '''
    def __init__(self, default=1):
        '''创建交点编号变量图元。

        :param default: 变量初始值。默认为`1`。
        :type default: int
        '''
        super().__init__(default, judgeFuncForReal(int, 1, 2))

    def askValueFromUser(self, view):
        '''询问用户输入交点编号，并将其设置为变量图元的值。

        :returns: 是否成功设置了变量图元的值。
        :rtype: bool
        '''
        dialog = IsecNoAskerDialog(view, 'Choose Intersection Number')
        if dialog.exec():  # 正确选择并点击OK，交点图元创建成功
            self.set(dialog.result())
            return True
        return False  # 点击Cancel或关闭了对话框，交点图元创建失败
