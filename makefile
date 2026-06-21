
GeoGraphItems/Core.so: GeoGraphItems/Core/* GeoGraphItems/Core/GeoItems/*
	source CoreBuilder.sh

run: *
	PYTHONPATH=.. ./.venv/bin/python3 -m GeoGrapher
