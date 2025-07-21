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

    SELECT = 0  # 选择
    DRAW = 1    # 绘制


class GeoSecondaryMode(enum.Enum):
    '''次模式。
    '''

    POINT = GeoGraphPoint      # 点
    SEGMENT = GeoGraphSegment  # 线段
    CIRCLE = GeoGraphCircle    # 圆


mainModes = {
    'Select': GeoMainMode.SELECT,
}  # 字符串所对主模式
drawModes = {
    'Point': GeoSecondaryMode.POINT,
    'Segment': GeoSecondaryMode.SEGMENT,
    'Circle': GeoSecondaryMode.CIRCLE,
}  # 字符串所对绘制次模式
