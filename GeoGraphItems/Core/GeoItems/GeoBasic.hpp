/* GeoBasic.hpp - GeoItems基础函数
 */
#ifndef GeoBasic_HPP
#define GeoBasic_HPP

#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/python.hpp>

using namespace boost::math;
namespace bp = boost::python;
using DecFloat = boost::multiprecision::cpp_dec_float_50;  // 高精度浮点数
using PointPos = std::pair<DecFloat, DecFloat>;            // 点坐标
using LineArgs = std::tuple<DecFloat, DecFloat, DecFloat>; // 表示一条直线的参数
using Func = std::function<DecFloat()>; // 返回DecFloat的函数，用于GeoPoint

DecFloat nandf = DecFloat(nan(""));               // NaN
PointPos nanpos = PointPos(nandf, nandf);         // NaN点
LineArgs nanline = LineArgs(nandf, nandf, nandf); // NaN直线
Func nanfunc = []() -> DecFloat {return nandf;};  // 返回NaN的函数
double dfloat2double(DecFloat& num);  // DecFloat转double
Func pyfunccv(bp::object f);  // Python函数转返回DecFloat的函数
DecFloat getla(LineArgs& l);  // 获取LineArgs的a
DecFloat getlb(LineArgs& l);  // 获取LineArgs的b
DecFloat getlc(LineArgs& l);  // 获取LineArgs的c

double dfloat2double(DecFloat& num)
{
    return (double)num;
}

bool dfloatisnan(DecFloat& num)
{
    return isnan((double)num);
}

Func pyfunccv(bp::object f)
{
    return [f]() -> DecFloat {
        return DecFloat((double)bp::extract<double>(f()));
    };
}

DecFloat getla(LineArgs& l)
{
    return std::get<0>(l);
}

DecFloat getlb(LineArgs& l)
{
    return std::get<1>(l);
}

DecFloat getlc(LineArgs& l)
{
    return std::get<2>(l);
}

#endif
