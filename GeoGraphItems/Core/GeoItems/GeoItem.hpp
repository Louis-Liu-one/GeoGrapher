/* GeoItem - 所有图元的基础
 */
#ifndef GeoItem_HPP
#define GeoItem_HPP

#include <vector>

class GeoItem;

using ItemVec = std::vector<GeoItem *>;

class GeoItem
{
    /* 所有图元类的基类。
     */
public:
    GeoItem();
    virtual ~GeoItem(); // 析构前重新初始化，使子图元不存留野指针
    void addMaster(GeoItem& master);  // 添加父图元，并将自身添加为父图元的子图元
    void addChild(GeoItem& child);    // 添加子图元，而不将自身添加为子图元的父图元
    void removeChild(GeoItem& child); // 删除子图元
    void update(); // 递归更新图元
protected:
    ItemVec _masters, _children;
    bool _updated; // 是否已是最新
private:
    // 重新初始化，并将所有子图元重新初始化
    // top表示是否为顶层调用
    void reinitialize(bool top = true);
};

class GeoPathItem : public GeoItem
{
public:
    GeoPathItem();
    virtual PointPos footPointFrom(PointPos p) = 0;
};

GeoItem::GeoItem() : _updated(false)
{
    _masters.clear();
    _children.clear();
}

GeoItem::~GeoItem()
{
    reinitialize();
}

void GeoItem::addMaster(GeoItem& master)
{
    if (std::find(_masters.begin(), _masters.end(),
            &master) == _masters.end())
    {
        _masters.push_back(&master);
        master.addChild(*this);
    }
}

void GeoItem::addChild(GeoItem& child)
{
    if (std::find(_children.begin(), _children.end(),
            &child) == _children.end())
        _children.push_back(&child);
}

void GeoItem::removeChild(GeoItem& child)
{
    auto ch = std::find(_children.begin(), _children.end(), &child);
    if (ch != _children.end()) _children.erase(ch);
}

void GeoItem::reinitialize(bool top)
{
    for (auto& i : _children) i->reinitialize(false);
    if (top) for (auto& i : _masters) i->removeChild(*this);
    _masters.clear();
    _children.clear();
}

void GeoItem::update()
{
    for (auto& i : _children) i->update();
    _updated = false;
}

GeoPathItem::GeoPathItem() : GeoItem() {}

#endif
