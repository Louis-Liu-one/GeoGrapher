/* GeoCalc - GeoItems相关计算函数
 */
#ifndef GeoCalc_HPP
#define GeoCalc_HPP

#include "GeoBasic.hpp"

DecFloat distanceTo(PointPos p1, PointPos p2);  // 两点距离
DecFloat distanceTo(PointPos p, LineArgs l);    // 点到直线距离
// 一次计算点到直线的距离、投影，以及直线x项系数与y项系数的平方和
std::tuple<DecFloat, PointPos, DecFloat> dstfpsq(PointPos p, LineArgs l);
PointPos footPoint(PointPos p, LineArgs l); // 点到直线垂足
// 点到圆垂足，意即以圆心为顶点、经过给定点的射线与圆的交点
PointPos footPoint(PointPos p, PointPos o, DecFloat r);
bool isLPoint(PointPos p1, PointPos p2);     // p1是否为“左点”，用于确定交点编号
PointPos intersec(LineArgs l1, LineArgs l2); // 两直线交点
// 直线与圆交点，圆用圆心与半径表示
std::pair<PointPos, PointPos> intersec(LineArgs l, PointPos o, DecFloat r);

DecFloat distanceTo(PointPos p1, PointPos p2)
{
    DecFloat dx = p1.first - p2.first, dy = p1.second - p2.second;
    return sqrt(fma(dx, dx, dy * dy));
}

DecFloat distanceTo(PointPos p, LineArgs l)
{
    auto [a, b, c] = l;
    DecFloat k = sqrt(fma(a, a, b * b));
    return k ? abs(fma(a, p.first, fma(b, p.second, c)) / k) : nandf;
}

std::tuple<DecFloat, PointPos, DecFloat> dstfpsq(PointPos p, LineArgs l)
{
    // 依次返回点到直线的距离（DiSTance）、点在直线上的投影坐标（FootPoint）、
    //   以及直线方程ax + by + c = 0中的a,b两项的平方和（SQuare）
    auto [a, b, c] = l;
    if (a == 0 and b == 0) return std::make_tuple(nandf, nanpos, nandf);
    auto [x, y] = p;
    DecFloat s = fma(a, a, b * b), k = -fma(a, x, fma(b, y, c)) / s;
    return std::make_tuple(
        abs(k * sqrt(s)), PointPos(fma(a, k, x), fma(b, k, y)), s);
}

PointPos footPoint(PointPos p, LineArgs l)
{
    auto [a, b, c] = l;
    if (a == 0 and b == 0) return nanpos;
    auto [x, y] = p;
    DecFloat k = -fma(a, x, fma(b, y, c)) / fma(a, a, b * b);
    return PointPos(fma(a, k, x), fma(b, k, y));
}

PointPos footPoint(PointPos p, PointPos o, DecFloat r)
{
    auto [x, y] = p;
    auto [ox, oy] = o;
    if (x == ox and y == oy) return nanpos;
    if (x == ox) return PointPos(x, oy + (y > oy ? r : -r));
    DecFloat k = (y - oy) / (x - ox),
        ks = fma(k, k, 1), kd = r / sqrt(ks), kt = x > ox ? kd : -kd;
    return PointPos(kt + ox, fma(k, kt, oy));
}

bool isLeftPoint(PointPos p1, PointPos p2)
{
    return p1.first != p2.first ?
        p1.first < p2.first : p1.second > p2.second;
}

PointPos intersec(LineArgs l1, LineArgs l2)
{
    auto [a1, b1, c1] = l1;
    auto [a2, b2, c2] = l2;
    DecFloat k = fma(a1, b2, -a2 * b1);
    return k ? PointPos(
        fma(b1, c2, -b2 * c1) / k,
        fma(a2, c1, -a1 * c2) / k) : nanpos;
}

std::pair<PointPos, PointPos> intersec(
    LineArgs l, PointPos o, DecFloat r)
{
    auto [a, b, c] = l;
    if (a == 0 and b == 0)
        return std::make_pair(nanpos, nanpos);
    auto [ox, oy] = o;
    auto [h, hp, s] = dstfpsq(o, l);
    if (r < h) return std::make_pair(nanpos, nanpos);
    auto [hx, hy] = hp;
    DecFloat d = (r + h) * (r - h), q = sqrt(d / s),
        dx = -b * q, dy = a * q;
    return std::make_pair(
        PointPos(hx + dx, hy + dy), PointPos(hx - dx, hy - dy));
}

#endif
