'''一些常数
'''

import enum

from .GeoItems.GeoGraphPoint import GeoGraphPoint
from .GeoItems.GeoGraphSegment import GeoGraphSegment
from .GeoItems.GeoGraphCircle import GeoGraphCircle

__all__ = [
    'GeoMainMode', 'GeoSecondaryMode',
    'mainModes', 'drawModes', 'drawModeTypes',
]


class GeoMainMode(enum.Enum):
    '''主模式。
    '''

    Select = 0  # 选择
    Draw = 1    # 绘制
    #


class GeoSecondaryMode(enum.Enum):
    '''次模式。
    '''

    Point = 0    # 点
    Segment = 1  # 线段
    Circle = 2   # 圆
    #


mainModes = {
    'Select': GeoMainMode.Select,
}  # 字符串所对主模式
drawModes = {
    'Point': GeoSecondaryMode.Point,
    'Segment': GeoSecondaryMode.Segment,
    'Circle': GeoSecondaryMode.Circle,
}  # 字符串所对绘制次模式
drawModeTypes = {
    GeoSecondaryMode.Point: GeoGraphPoint,
    GeoSecondaryMode.Segment: GeoGraphSegment,
    GeoSecondaryMode.Circle: GeoGraphCircle,
}  # 绘制次模式所对图元类型
