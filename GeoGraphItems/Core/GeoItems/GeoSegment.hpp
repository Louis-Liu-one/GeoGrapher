/* GeoSegment.hpp - 线段图元
 */
#ifndef GeoSegment_HPP
#define GeoSegment_HPP

#include "GeoCalc.hpp"
#include "GeoPoint.hpp"

class GeoSegment : public GeoPathItem
{
    /* 线段图元类。直线用ax + by + c = 0定义。
     */
public:
    GeoSegment();
    PointPos footPointFrom(PointPos p); // 点在直线上的投影
    LineArgs abc(); // 一次性返回直线方程的a（x项系数）、b（y项系数）、c（常数项）。
};

GeoSegment::GeoSegment() : GeoPathItem() {}

PointPos GeoSegment::footPointFrom(PointPos p)
{
    return footPoint(p, abc());
}

LineArgs GeoSegment::abc()
{
    if (_masters.size() != 2) return nanline;
    PointPos p1 = ((GeoPoint *)_masters[0])->pos(),
        p2 = ((GeoPoint *)_masters[1])->pos();
    auto [x1, y1] = p1;
    auto [x2, y2] = p2;
    return LineArgs(y2 - y1, x1 - x2, x2 * y1 - x1 * y2);
}

#endif
