# Why Python for Geospatial?

## Talking points (20 min)

### 1. One language for the full workflow

Python connects every step in a location analytics pipeline:

- Pull data from MAPID API
- Clean and validate geometries
- Compute area, centroids, spatial statistics
- Export results (CSV, GeoPackage, GeoJSON)
- Build maps for reports

No switching between desktop GIS, spreadsheets, and custom scripts.

### 2. Reproducibility

| Manual workflow | Python workflow |
|-----------------|-----------------|
| Click export 150 times | One script, same result every run |
| Forgot which CRS you used | CRS logged in code |
| Hard to share steps with team | Notebook or script is the documentation |

### 3. Integration with MAPID

GEO MAPID is where polygons are created and managed. Python is how you:

- **Scale** — process 100–200 polygons in minutes
- **Automate** — scheduled refresh via n8n (Session 2)
- **Extend** — combine MAPID layers with external datasets

### 4. Ecosystem

| Task | Library |
|------|---------|
| Vector data | GeoPandas, Shapely |
| API calls | requests |
| Analysis | Pandas, GeoPandas |
| Visualization | Matplotlib, Folium |
| Automation | n8n + Python scripts |

### 5. Hook for Session 2

> Today we explore **25 polygons** in a notebook — 8 valid, 10 self-intersection/sliver (fixable), and 7 overlap cases for review.

Upload: raw sample → ~19 on MAPID; use [`data/sample_mapid_upload.geojson`](data/sample_mapid_upload.geojson) for all 25.
> Session 2 we refactor the same logic into `pipeline.py` and orchestrate 100–200 polygons with n8n.

Code flow mind map: [`../docs/session01_code_mindmap.md`](../docs/session01_code_mindmap.md)

## Discussion questions

1. What repetitive GIS task do you do today that could be a script?
2. Where does MAPID fit in your current workflow?
3. What output do stakeholders ask for most (maps, tables, both)?
