'''一些常数
'''

import enum

from .GeoGraphItems.GeoGraphPoint import GeoGraphPoint
from .GeoGraphItems.GeoGraphSegment import GeoGraphSegment
from .GeoGraphItems.GeoGraphCircle import GeoGraphCircle
from .GeoGraphItems.GeoGraphIntersection import GeoGraphIntersection

__all__ = [
    'GeoMainMode', 'GeoSecondaryMode',
    'mainModes', 'drawModes',
]


class GeoMainMode(enum.Enum):
    '''主模式。
    '''

    SELECT = 0  # 选择
    DRAW = 1    # 绘制


class GeoSecondaryMode(enum.Enum):
    '''次模式。
    '''

    POINT = GeoGraphPoint      # 点
    SEGMENT = GeoGraphSegment  # 线段
    CIRCLE = GeoGraphCircle    # 圆
    INTERSECTION = GeoGraphIntersection  # 交点


mainModes = {
    'Select': GeoMainMode.SELECT,
}  # 字符串所对主模式
drawModes = {
    'Point': GeoSecondaryMode.POINT,
    'Segment': GeoSecondaryMode.SEGMENT,
    'Circle': GeoSecondaryMode.CIRCLE,
    'Intersection': GeoSecondaryMode.INTERSECTION,
}  # 字符串所对绘制次模式
