/* GeoPoint - 点图元
 */
#ifndef GeoPoint_HPP
#define GeoPoint_HPP

#include "GeoBasic.hpp"
#include "GeoItem.hpp"

class GeoPoint : public GeoItem
{
    /* 点图元类。
     */
public:
    // 构造函数接受两个返回DecFloat的函数以获得坐标的动态变化
    GeoPoint(Func x, Func y);
    GeoPoint(bp::object x, bp::object y); // 构造函数的Python封装
    virtual PointPos pos(); // 点坐标
    bp::tuple posPy();      // 点坐标的Python封装
private:
    Func _x, _y;        // 构造函数传入的函数
    PointPos rawPos();  // 原始坐标，即(_x(), _y())
};

GeoPoint::GeoPoint(Func x, Func y) : GeoItem(), _x(x), _y(y) {}

GeoPoint::GeoPoint(bp::object x, bp::object y)
{
    _x = pyfunccv(x), _y = pyfunccv(y);
}

PointPos GeoPoint::pos()
{
    // 若_masters为空，则点是自由点
    if (_masters.empty()) return rawPos();
    // 若_masters非空，则点表示已知路径上的点
    GeoPathItem *onPath = dynamic_cast<GeoPathItem *>(_masters[0]);
    if (onPath) return onPath->footPointFrom(rawPos());
    return nanpos; // 否则点无意义
}

bp::tuple GeoPoint::posPy()
{
    auto [x, y] = pos();
    return bp::make_tuple(x, y);
}

PointPos GeoPoint::rawPos()
{
    return PointPos(_x(), _y());
}

GeoPoint nanpoint = GeoPoint(nanfunc, nanfunc);  // NaN点图元

#endif
