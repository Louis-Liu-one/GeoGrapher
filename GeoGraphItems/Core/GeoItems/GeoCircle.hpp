/* GeoCircle.hpp - 圆图元
 */
#ifndef GeoCircle_HPP
#define GeoCircle_HPP

#include "GeoCalc.hpp"
#include "GeoPoint.hpp"

class GeoCircle : public GeoPathItem
{
    /* 圆图元类。
     */
public:
    PointPos footPointFrom(PointPos p);    // 点在圆上的投影
    GeoPoint *o();   // 圆心
    GeoPoint *onc(); // 圆上一点
    DecFloat r();    // 半径
    std::pair<PointPos, DecFloat> oandr(); // 一次返回圆心坐标与半径
    bp::tuple oandrPy();                   // oandr()的Python形式
};

GeoPoint *GeoCircle::o()
{
    if (_masters.size() != 2) return &nanpoint;
    GeoPoint *p = dynamic_cast<GeoPoint *>(_masters[0]);
    return p ? p : &nanpoint;
}

GeoPoint *GeoCircle::onc()
{
    if (_masters.size() != 2) return &nanpoint;
    GeoPoint *p = dynamic_cast<GeoPoint *>(_masters[1]);
    return p ? p : &nanpoint;
}

DecFloat GeoCircle::r()
{
    if (_masters.size() != 2) return nandf;
    GeoPoint *p1 = dynamic_cast<GeoPoint *>(_masters[0]),
        *p2 = dynamic_cast<GeoPoint *>(_masters[1]);
    return p1 and p2 ? distanceTo(p1->pos(), p2->pos()) : nandf;
}

std::pair<PointPos, DecFloat> GeoCircle::oandr()
{
    if (_masters.size() != 2)
        return std::make_pair(nanpos, nandf);
    GeoPoint *p1 = dynamic_cast<GeoPoint *>(_masters[0]),
        *p2 = dynamic_cast<GeoPoint *>(_masters[1]);
    PointPos p1pos = p1->pos();
    return p1 and p2 ? std::make_pair(
            p1pos, distanceTo(p1pos, p2->pos()))
        : std::make_pair(nanpos, nandf); 
}

bp::tuple GeoCircle::oandrPy()
{
    auto [o, r] = oandr();
    return bp::make_tuple(o, r);
}

PointPos GeoCircle::footPointFrom(PointPos p)
{
    auto [o, r] = oandr();
    return footPoint(p, o, r);
}

#endif
