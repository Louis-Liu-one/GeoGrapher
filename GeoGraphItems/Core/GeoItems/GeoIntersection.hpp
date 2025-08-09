
#ifndef GeoIntersection_HPP
#define GeoIntersection_HPP

#include "GeoSegment.hpp"
#include "GeoCircle.hpp"
#include "GeoVariable.hpp"

class GeoIntersection : public GeoPoint
{
    /* 交点图元类。
     */
public:
    GeoIntersection();
    PointPos pos();  // 交点坐标
private:
    enum {undefined, LL, LC, CC} _mode;  // 交点模式
    GeoSegment *s[2]; // 线段图元数组，存储_masters中的线段图元（如有）
    GeoCircle *c[2];  // 圆图元，同上
    GeoVariable<int> *i;  // 交点编号，仅有圆时使用
    // 检查_masters[i]的类型并存入c或s中
    // 返回值中第一个表示是否成功，第二个表示是否为线段
    std::pair<bool, bool> _checkMode(int i);
    // 检查_masters的类型并存入c或s中，并设置交点编号（如需），返回是否成功
    bool _checkMode();
};

GeoIntersection::GeoIntersection()
    : GeoPoint(nanfunc, nanfunc), _mode(undefined) {}

PointPos GeoIntersection::pos()
{
    if (_mode == undefined and not _checkMode()) return nanpos;
    if (_mode == LL) return intersec(s[0]->abc(), s[1]->abc());
    if (_mode == LC)
    {
        auto [p1, p2] = intersec(s[0]->abc(), c[1]->oandr());
        if (not isLeftPoint(p1, p2)) std::swap(p1, p2);
        return i->get() == 1 ? p1 : p2;
    }
    return nanpos;
}

std::pair<bool, bool> GeoIntersection::_checkMode(int i)
{
    bool res = true;
    s[i] = dynamic_cast<GeoSegment *>(_masters[i]);
    if (not s[i])
        c[i] = dynamic_cast<GeoCircle *>(_masters[i]), res = false;
    if (not c[i]) return std::make_pair(false, res);
    return std::make_pair(true, res);
}

bool GeoIntersection::_checkMode()
{
    // 此函数一般只执行一次
    if (_masters.size() < 2 or _masters.size() > 3) return false;
    if (_masters.size() == 3 and not (
            i = dynamic_cast<GeoVariable<int> *>(_masters[2])))
        return false;
    auto [p1ok, p1] = _checkMode(0);
    auto [p2ok, p2] = _checkMode(1);
    if (not p1ok or not p2ok) return false;
    // LL -> s[0], s[1]
    // LC -> s[0], c[1]
    // CC -> c[0], c[1]
    if (p1) _mode = p2 ? LL : LC;
    else if (p2) _mode = LC, s[0] = s[1], c[1] = c[0];
    else _mode = CC;
    return true;
}

#endif
