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
    GeoPoint *point1();
    GeoPoint *point2();
private:
    GeoPoint *_point1 = nullptr, *_point2 = nullptr;
    LineArgs _cachedabc = nanline;
};

GeoSegment::GeoSegment() : GeoPathItem() {}

PointPos GeoSegment::footPointFrom(PointPos p)
{
    return footPoint(p, abc());
}

GeoPoint *GeoSegment::point1()
{
    if (not _point1) _point1 = dynamic_cast<GeoPoint *>(_masters[0]);
    return _point1 ? _point1 : &nanpoint;
}

GeoPoint *GeoSegment::point2()
{
    if (not _point2) _point2 = dynamic_cast<GeoPoint *>(_masters[1]);
    return _point2 ? _point2 : &nanpoint;
}

LineArgs GeoSegment::abc()
{
    if (_masters.size() != 2) return nanline;
    if (_updated) return _cachedabc;
    _updated = true;
    auto [x1, y1] = point1()->pos();
    auto [x2, y2] = point2()->pos();
    return _cachedabc = LineArgs(
        y2 - y1, x1 - x2, fma(x2, y1, -x1 * y2));
}

#endif
