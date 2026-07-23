# Commonly Used Python Libraries for Spatial Processing

## Overview

Three branches of spatial work — processing, analysis, visualization.

---

## 1. Processing Data

| Library | Role | Example |
|---------|------|---------|
| **GeoPandas** | Read/write vector data, spatial joins, CRS transforms | `gpd.GeoDataFrame.from_features()` |
| **Shapely** | Low-level geometry operations | `geom.area`, `geom.buffer(0)` |
| **PyProj** | Coordinate reference systems | `gdf.to_crs(32748)` |
| **Fiona** | Vector file I/O (used by GeoPandas) | `gdf.to_file("out.gpkg")` |

### Key operations

```python
import geopandas as gpd

# From API GeoJSON features
gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")

# Reproject for accurate area (Indonesia: UTM 48S/49S/50S)
gdf_proj = gdf.to_crs(32748)
gdf["area_ha"] = gdf_proj.geometry.area / 10_000

# Fix invalid geometries
gdf["geometry"] = gdf.geometry.buffer(0)
```

### CRS reminder

- **EPSG:4326** (WGS84) — lat/lon degrees, good for storage and API
- **EPSG:32748** (UTM 48S) — meters, use for area/distance in western Indonesia
- **Never compute area in EPSG:4326** — results will be wrong

---

## 2. Analysis and Statistics

| Library | Role | Example |
|---------|------|---------|
| **Pandas** | Attribute statistics | `gdf.groupby("category")["area_ha"].sum()` |
| **GeoPandas** | Spatial filter, join, dissolve | `gdf[gdf["area_ha"] > 5]` |
| **PySAL** | Spatial autocorrelation (advanced) | Optional for future modules |

### Example questions

- Which polygons exceed 5 hectares?
- Total area per category?
- Top 10 largest polygons?

```python
large = gdf[gdf["area_ha"] > 5]
summary = large.groupby("category")["area_ha"].agg(["count", "sum", "mean"])
top10 = gdf.nlargest(10, "area_ha")[["name", "category", "area_ha"]]
```

---

## 3. Visualization

| Library | Output | When to use |
|---------|--------|-------------|
| **Matplotlib** | Static choropleth | Reports, slides |
| **Folium** | Interactive web map | Exploration, sharing |
| **Contextily** | Basemap tiles | Publication-quality static maps |

### Static choropleth (everyone)

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 8))
gdf.plot(column="area_ha", legend=True, ax=ax, cmap="YlOrRd")
ax.set_title("Polygon Area (hectares)")
plt.show()
```

### Interactive map (Extend track)

```python
import folium

m = folium.Map(location=[gdf.geometry.centroid.y.mean(),
                          gdf.geometry.centroid.x.mean()], zoom_start=11)
folium.GeoJson(gdf).add_to(m)
m
```

---

## Quick reference: API → map

```
requests.get() → JSON features → GeoDataFrame → to_crs() → area_ha → plot()
```

See notebook: [`03_playground_mapid.ipynb`](03_playground_mapid.ipynb)
