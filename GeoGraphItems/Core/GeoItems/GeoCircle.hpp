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
    GeoCircle();
    PointPos footPointFrom(PointPos p);    // 点在圆上的投影
    GeoPoint *o();   // 圆心
    GeoPoint *onc(); // 圆上一点
    DecFloat r();    // 半径
    std::pair<PointPos, DecFloat> oandr(); // 一次返回圆心坐标与半径
    bp::tuple oandrPy();                   // oandr()的Python形式
private:
    GeoPoint *_o = nullptr, *_onc = nullptr;
    DecFloat _cachedr = nandf;
};

GeoCircle::GeoCircle() : GeoPathItem() {}

GeoPoint *GeoCircle::o()
{
    if (_masters.size() != 2) return &nanpoint;
    if (_o) return _o;
    _o = dynamic_cast<GeoPoint *>(_masters[0]);
    return _o ? _o : (_o = &nanpoint);
}

GeoPoint *GeoCircle::onc()
{
    if (_masters.size() != 2) return &nanpoint;
    if (_onc) return _onc;
    _onc = dynamic_cast<GeoPoint *>(_masters[1]);
    return _onc ? _onc : (_onc = &nanpoint);
}

DecFloat GeoCircle::r()
{
    if (_masters.size() != 2) return nandf;
    if (_updated) return _cachedr;
    _updated = true;
    GeoPoint *p1 = o(), *p2 = onc();
    return _cachedr = p1 and p2 ?
        distanceTo(p1->pos(), p2->pos()) : nandf;
}

std::pair<PointPos, DecFloat> GeoCircle::oandr()
{
    if (_masters.size() != 2) return std::make_pair(nanpos, nandf);
    return std::make_pair(o()->pos(), r());
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
