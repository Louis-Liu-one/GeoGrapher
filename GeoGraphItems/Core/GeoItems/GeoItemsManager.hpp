/* GeoItemsManager - 图元管理
 */
#ifndef GeoItemsManager_HPP
#define GeoItemsManager_HPP

#include <unordered_set>
#include "GeoItem.hpp"

using ItemSet = std::unordered_set<GeoItem *>;

class GeoItemsManager
{
public:
    GeoItemsManager();
    void addItem(GeoItem& item);        // 添加图元
    void removeItem(GeoItem& item);     // 删除图元
    bool isAncestorItem(GeoItem& item); // 判断图元是否为自由图元
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

bool GeoItemsManager::isAncestorItem(GeoItem& item)
{
    return item.masters().empty();
}

#endif
