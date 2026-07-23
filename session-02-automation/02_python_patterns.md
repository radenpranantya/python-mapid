# Python Automation Patterns for Geospatial

## Pattern 1: Configuration (no hardcoded secrets)

Use `config.yaml` + environment variables:

```yaml
api:
  base_url: https://geoserver.mapid.io
  project_id: your-project-id
  layer_id: your-layer-id
  page_size: 100
  use_cached: false
  cached_file: data/sample_batch_response.json

output:
  dir: ./output
  target_crs: EPSG:32748
```

```python
import os
api_key = os.environ["MAPID_API_KEY"]
project_id = os.environ["MAPID_PROJECT_ID"]
```

## Pattern 2: MAPID GeoServer fetch

```python
from mapid_client import fetch_all_features

features = fetch_all_features(
    base_url="https://geoserver.mapid.io",
    api_key=api_key,
    project_id=project_id,
    layer_id=config["api"]["layer_id"],
)
```

Or implement manually:

```python
def fetch_all_features(base_url, api_key, project_id, layer_id):
    resp = requests.get(
        f"{base_url.rstrip('/')}/layers_new/get_layer_data_list",
        params={"api_key": api_key, "project_id": project_id, "layer_id": layer_id},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    # Normalize to GeoJSON features — see mapid_client.normalize_to_feature_collection
    return data["features"]
```

## Pattern 3: Pure processing pipeline

```python
def process_gdf(gdf, target_crs):
    gdf = gdf[gdf.geometry.notna()].copy()
    gdf["geometry"] = gdf.geometry.buffer(0)
    gdf["geometry_valid"] = gdf.geometry.is_valid

    gdf_proj = gdf.to_crs(target_crs)
    gdf["area_ha"] = gdf_proj.geometry.area / 10_000

    centroids = gdf_proj.geometry.centroid.to_crs(4326)
    gdf["centroid_lat"] = centroids.y
    gdf["centroid_lon"] = centroids.x
    return gdf
```

## Pattern 4: Logging and resilient execution

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("output/run.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

logger.info("Fetched %d features", len(features))
```

## Pattern 5: CLI entry point

```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run_pipeline(args.config)

if __name__ == "__main__":
    main()
```

## Refactoring checklist (notebook → script)

1. Extract fetch logic → `fetch_all_features()`
2. Extract processing → `process_gdf()`
3. Extract export → `export_outputs()`
4. Add `config.yaml` for all settings
5. Add logging to file + console
6. Add `--config` CLI argument

See reference implementation: [`pipeline.py`](pipeline.py)

---

## Pattern 6: n8n orchestration (mandatory)

After `pipeline.py` works standalone, wrap it in n8n:

```
n8n Manual Trigger → Execute Command: python pipeline.py --config config.yaml
                  → IF success → Set Success / notify
                  → IF failure → Set Failure / alert
```

**Division of labor:**
- Python = fetch, process, export
- n8n = when to run, success/failure routing, notifications

Hands-on guide: [`../docs/session02_n8n_hands_on.md`](../docs/session02_n8n_hands_on.md)
