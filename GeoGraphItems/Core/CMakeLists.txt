
cmake_minimum_required(VERSION 4.0.3)
project(GeoItems)

set(MODULE_NAME GeoItems)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_SHARED_LIBRARY_SUFFIX ".so")
set(Boost_LIBRARIES /usr/local/Cellar/boost-python3/1.88.0/lib/libboost_python313.dylib)
set(PYTHON_LIBRARIES /Library/Frameworks/Python.framework/Versions/3.13/lib/libpython3.13.dylib)
set(Boost_INCLUDE /usr/local/Cellar/boost)
set(PYTHON_INCLUDE /Library/Frameworks/Python.framework/Versions/3.13/include/python3.13)

add_library(${MODULE_NAME} SHARED GeoItems.cpp)
target_link_libraries(${MODULE_NAME} ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
set_target_properties(${MODULE_NAME} PROPERTIES PREFIX "")
include_directories(${Boost_INCLUDE} ${PYTHON_INCLUDE})
link_directories(${Boost_INCLUDE} ${PYTHON_INCLUDE})
