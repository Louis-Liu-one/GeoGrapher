/* GeoItemsManager - 图元管理
 */
#ifndef GeoItemsManager_HPP
#define GeoItemsManager_HPP

#include "GeoItem.hpp"

class GeoItemsManager
{
public:
    GeoItemsManager();
    void addItem(GeoItem& item);        // 添加图元
    void removeItem(GeoItem& item);     // 删除图元
private:
    ItemSet _items;
};

GeoItemsManager::GeoItemsManager()
{
    _items.clear();
}

void GeoItemsManager::addItem(GeoItem& item)
{
    _items.insert(&item);
}

void GeoItemsManager::removeItem(GeoItem& item)
{
    if (_items.find(&item) != _items.end()) _items.erase(&item);
    for (auto& i : item.children()) removeItem(*i);
}

#endif
