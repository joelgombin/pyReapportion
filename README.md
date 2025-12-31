# pyReapportion

Reapportion data from one geography to another in Python.

This package allows you to reapportion data from one geography to another, for example when you have data distributed in some administrative units (e.g., IRIS) and need to have it in some other units (e.g., polling stations).

This is a Python port of the R package [spReapportion](https://github.com/joelgombin/spReapportion).

## Installation

```bash
pip install -e .
```

## Usage

```python
import geopandas as gpd
from pyreapportion import reapportion

# Load your geometries and data
old_geom = gpd.read_file("old_geometry.shp")
new_geom = gpd.read_file("new_geometry.shp")
data = pd.read_csv("data.csv")

# Reapportion data from old to new geometry
result = reapportion(
    old_geom=old_geom,
    new_geom=new_geom,
    data=data,
    old_id="old_id_column",
    new_id="new_id_column",
    data_id="data_id_column",
    variables=["population", "votes"],
    mode="count"
)
```

## Features

- **Two modes**:
  - `"count"` for absolute values
  - `"proportion"` for proportions (0-1 range)
- **Weight support**: Optional weight matrix for more accurate redistribution
- **Spatial operations**: Uses geopandas for robust spatial operations

## Development

Run tests with:
```bash
pytest tests/
```

## License

MIT License
