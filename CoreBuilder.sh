
cd GeoGraphItems/Core
mkdir build
cd build
cmake ..
make
cd ..
mv build/*.so ..
rm -r build
cd ../..
