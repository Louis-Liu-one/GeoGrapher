
#include "GeoItems/GeoIntersection.hpp"
#include "GeoItems/GeoItemsManager.hpp"

DecFloat (*distanceTo_P)(PointPos, PointPos) = &distanceTo;
DecFloat (*distanceTo_L)(PointPos, LineArgs) = &distanceTo;
PointPos (*footPoint_L)(PointPos, LineArgs) = &footPoint;
PointPos (*footPoint_C)(PointPos, PointPos, DecFloat) = &footPoint;
PointPos (*intersec_LL)(LineArgs, LineArgs) = &intersec;
bp::tuple (*intersec_LC)(LineArgs, PointPos, DecFloat)
    = [](LineArgs l, PointPos o, DecFloat r){
        auto [p1, p2] = intersec(l, o, r);
        return bp::make_tuple(p1, p2);};

BOOST_PYTHON_MODULE(Core)
{
    using namespace boost::python;
    class_<DecFloat>("DecFloat",
        "`boost::python::multiprecision::"
        "cpp_dec_float_50`在Python中的暴露。",
        init<double>(
            (arg("self"), "num"), "以整数或浮点数初始化`DecFloat`对象。"))
        .def("__float__", &dfloat2double,
            arg("self"), "转换为Python的`float`对象。")
        .def("is_nan", &dfloatisnan, arg("self"), "判断对象是否为NaN。");
    class_<PointPos>("PointPos",
        "点图元坐标类，对应`std::pair<DecFloat, DecFloat>`。",
        init<DecFloat, DecFloat>((arg("self"), "x", "y"),
            "以一对`DecFloat`对象初始化点图元坐标。"))
        .def_readonly("x", &PointPos::first, "横坐标")
        .def_readonly("y", &PointPos::second, "纵坐标");
    class_<LineArgs>("GeoLineArgs",
        "直线参数类，相当于`std::tuple<DecFloat, DecFloat, DecFloat>`。\n"
        "三个参数分别是直线方程$ax + by + c = 0$中的$a, b, c$。",
        init<DecFloat, DecFloat, DecFloat>(
            (arg("self"), "a", "b", "c"), "初始化直线参数。"))
        .def("a", &getla, arg("self"), "直线方程中x项系数。")
        .def("b", &getlb, arg("self"), "直线方程中y项系数。")
        .def("c", &getlc, arg("self"), "直线方程中常数项。");
    class_<GeoItemsManager>("GeoItemsManager", "图元管理类。",
        init<>(arg("self"), "初始化图元管理对象。"))
        .def("addItem", &GeoItemsManager::addItem,
            (arg("self"), "item"), "添加图元。")
        .def("removeItem", &GeoItemsManager::removeItem,
            (arg("self"), "item"), "删除图元。")
        .def("isAncestorItem", &GeoItemsManager::isAncestorItem,
            (arg("self"), "item"), "查询图元是否没有父图元。");
    class_<GeoItem>("GeoItem", "所有图元类的基类。",
        init<>(arg("self"), "初始化图元。"))
        .def("addMaster", &GeoItem::addMaster, (arg("self"), "master"),
            "添加父图元，并将自身添加为父图元的子图元。")
        .def("addChild", &GeoItem::addChild,
            (arg("self"), "child"), "添加子图元。")
        .def("removeChild", &GeoItem::removeChild,
            (arg("self"), "child"), "删除子图元。")
        .def("update", &GeoItem::update, arg("self"), "递归更新图元。");
    class_<GeoPoint, bases<GeoItem>>("GeoPoint", "点图元类。",
        init<object, object>((arg("self"), "x", "y"), "初始化点图元。"))
        .def("pos", &GeoPoint::posPy, arg("self"), "点图元位置。");
    class_<GeoSegment, bases<GeoItem>>("GeoSegment", "线段图元类。",
        init<>(arg("self"), "初始化线段图元。"))
        .def("abc", &GeoSegment::abc, arg("self"), "线段参数。");
    class_<GeoCircle, bases<GeoItem>>("GeoCircle", "圆图元类。",
        init<>(arg("self"), "初始化圆图元。"))
        .def("o", &GeoCircle::o, arg("self"), "圆心。",
            return_value_policy<reference_existing_object>())
        .def("onc", &GeoCircle::onc, arg("self"), "圆上一点。",
            return_value_policy<reference_existing_object>())
        .def("oandr", &GeoCircle::oandrPy, arg("self"), "圆心坐标和半径。")
        .def("r", &GeoCircle::r, arg("self"), "半径。");
    class_<GeoIntersection, bases<GeoPoint>>(
        "GeoIntersection", "交点图元类。",
        init<>(arg("self"), "初始化交点图元。"))
        .def("pos", &GeoIntersection::posPy, arg("self"), "交点坐标。");
    class_<GeoVariable<int>, bases<GeoItem>>("GeoIntVar",
        "整型变量图元类。", init<int>((arg("self"), "v"), "以整数初始化变量图元。"))
        .def("get", &GeoVariable<int>::get, arg("self"), "获取值。")
        .def("set", &GeoVariable<int>::set, (arg("self"), "v"), "设置值。");
    def("distanceTo", distanceTo_P, (arg("p1"), "p2"), "两点之间的距离。");
    def("distanceTo", distanceTo_L, (arg("p"), "l"),
        "点到直线的距离，直线由`LineArgs`对象定义。");
    def("footPoint", footPoint_L, (arg("p"), "l"),
        "点在直线上的投影，直线由`LineArgs`对象定义。");
    def("footPoint", footPoint_C, (arg("p"), "o", "r"),
        "以圆心为端点、经过给定点的射线与圆周的交点，圆由圆心与半径定义。");
    def("isLeftPoint", isLeftPoint, (arg("p1"), "p2"),
        "返回一个布尔值，表示第一个参数是否是两参数中的“左点”。\n"
        "若两点横坐标不相等，则横坐标较小的一点是“左点”；\n"
        "若横坐标相等，则纵坐标较大的一点是“左点”。\n"
        "另一点是两点中的“右点”。");
    def("intersec", intersec_LL, (arg("l1"), "l2"), "求两直线的交点。");
    def("intersec", intersec_LC,
        (arg("l"), "o", "r"), "求直线与圆的两交点，以元组返回。");
}
