#!/usr/bin/env python3
"""MAPID polygon batch processing pipeline — beginner template.

Fill in the TODO sections during Session 2.
Run: python pipeline_template.py --config config.yaml
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import geopandas as gpd
import requests
import yaml

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(output_dir / "run.log", mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def fetch_all_features(base_url: str, layer_id: str, headers: dict, page_size: int = 100) -> list:
    """TODO: Implement paginated fetch from MAPID API.

    Hint:
    - Loop with offset += page_size
    - Break when batch is empty
    - Extend all_features list each iteration
    """
    all_features = []
    offset = 0

    # TODO: Write pagination loop here
    raise NotImplementedError("Implement fetch_all_features pagination loop")


def load_cached_features(cached_file: Path) -> list:
    with cached_file.open(encoding="utf-8") as f:
        return json.load(f)["features"]


def features_to_gdf(features: list, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame.from_features(features, crs=crs)


def process_gdf(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:
    """TODO: Implement processing steps.

    Required:
    1. Drop null geometries
    2. Fix invalid geometries with buffer(0)
    3. Set geometry_valid column
    4. Compute area_ha in target_crs
    5. Compute centroid_lat and centroid_lon (WGS84)
    """
    gdf = gdf[gdf.geometry.notna()].copy()

    # TODO: Fix invalid geometries and set geometry_valid

    # TODO: Compute area_ha using projected CRS

    # TODO: Compute centroid_lat and centroid_lon

    return gdf


def export_outputs(gdf: gpd.GeoDataFrame, output_dir: Path) -> None:
    """TODO: Export summary.csv and polygons_processed.gpkg"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # TODO: Write summary.csv with columns:
    # id, name, area_ha, centroid_lat, centroid_lon, geometry_valid

    # TODO: Write polygons_processed.gpkg

    logger.info("Export complete.")


def run_pipeline(config: dict) -> gpd.GeoDataFrame:
    api_cfg = config["api"]
    output_cfg = config["output"]
    output_dir = Path(output_cfg["dir"])
    target_crs = output_cfg["target_crs"]

    setup_logging(output_dir)

    if api_cfg.get("use_cached", False):
        features = load_cached_features(Path(api_cfg["cached_file"]))
    else:
        token = os.environ["MAPID_API_TOKEN"]
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        features = fetch_all_features(
            api_cfg["base_url"],
            api_cfg["layer_id"],
            headers,
            page_size=api_cfg.get("page_size", 100),
        )

    gdf = features_to_gdf(features)
    gdf = process_gdf(gdf, target_crs)
    export_outputs(gdf, output_dir)
    return gdf


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run_pipeline(load_config(args.config))


if __name__ == "__main__":
    main()
