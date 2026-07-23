'''一些程序使用的常量
'''

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .GeoGraphItems.GeoGraphItem import GeoGraphItem

import enum

from .GeoGraphItems.GeoGraphPoint import GeoGraphPoint
from .GeoGraphItems.GeoGraphSegment import GeoGraphSegment
from .GeoGraphItems.GeoGraphCircle import GeoGraphCircle
from .GeoGraphItems.GeoGraphIntersection import GeoGraphIntersection

__all__ = ['GeoMainMode', 'GeoSecondaryMode', 'secondaryModeClasses']


class GeoMainMode(enum.Enum):
    '''主模式。
    '''

    SELECT = 0  # 选择
    DRAW = 1    # 绘制


class GeoSecondaryMode(enum.Enum):
    '''次模式。
    '''

    POINT = 0         # 点
    SEGMENT = 1       # 线段
    CIRCLE = 2        # 圆
    INTERSECTION = 3  # 交点


# 各个次模式对应的图元类
secondaryModeClasses: dict[GeoSecondaryMode, type[GeoGraphItem]] = {
    GeoSecondaryMode.POINT: GeoGraphPoint,
    GeoSecondaryMode.SEGMENT: GeoGraphSegment,
    GeoSecondaryMode.CIRCLE: GeoGraphCircle,
    GeoSecondaryMode.INTERSECTION: GeoGraphIntersection,
}
