
GeoGraphItems/Core.so: GeoGraphItems/Core/* GeoGraphItems/Core/GeoItems/*
	source CoreBuilder.sh

run: *
	PYTHONPATH=.. python3 -m GeoGrapher
