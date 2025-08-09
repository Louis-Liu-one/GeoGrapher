/* GeoVariable.hpp - 变量图元
 */
#ifndef GeoVariable_HPP
#define GeoVariable_HPP

#include "GeoBasic.hpp"
#include "GeoItem.hpp"

template <class T>
class GeoVariable : public GeoItem
{
    /* 变量图元类，为变量提供图元接口。
     */
public:
    GeoVariable(T v);
    void set(T v);
    T get();
protected:
    T val;
};

template <class T>
GeoVariable<T>::GeoVariable(T v) : val(v) {}

template <class T>
void GeoVariable<T>::set(T v)
{
    val = v;
}

template <class T>
T GeoVariable<T>::get()
{
    return val;
}

#endif
