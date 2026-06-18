'''GeoGrapher交点图元
'''

from .GeoGraphPoint import GeoGraphPoint
from .GeoGraphSegment import GeoGraphSegment
from .GeoGraphCircle import GeoGraphCircle
from .GeoGraphVariable import GeoGraphIsecNoVar
from .Interfaces.IsecNoAsker import IsecNoAskerDialog
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
            (GeoGraphCircle, GeoGraphCircle)}

    def _addFirstMaster(self, master):
        '''为本图元添加第一个父图元。子类可在此处作一些特殊处理。
        '''
        self.addMaster(master)

    def whenFinishingCreating(self, view, typePatterns):
        '''完成创建时，询问交点编号。

        :param view: 图元所在视图。
        :type view: GeoGrapher.GeoGraphView.GeoGraphView
        :param typePatterns: 图元进行此次创建选用的类型模式。
        :type typePatterns: set[tuple[type]]
        :returns: 返回`True`，当此次创建的是两直线交点，或交点编号询问完成；
            反之，当交点编号询问失败，图元创建失败。
        :rtype: bool
        '''
        if (GeoGraphSegment, GeoGraphSegment) in typePatterns:
            return True  # 两直线仅一个交点，无需询问编号
        dialog = IsecNoAskerDialog(view, 'Choose Intersection Number')
        if dialog.exec():  # 正确选择并点击OK，交点图元创建成功
            var = GeoGraphIsecNoVar()
            var.set(dialog.result())
            self.addMaster(var)
            return True
        return False  # 点击Cancel或关闭了对话框，交点图元创建失败
