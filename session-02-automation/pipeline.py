#!/usr/bin/env python3
"""MAPID polygon batch processing pipeline — instructor reference solution."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mapid_client import fetch_all_features, get_api_key, get_project_id

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    base_url = os.getenv("MAPID_BASE_URL")
    if base_url:
        config.setdefault("api", {})["base_url"] = base_url

    return config


def setup_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "run.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def load_cached_features(cached_file: Path) -> list:
    logger.info("Loading cached data from %s", cached_file)
    with cached_file.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["features"]


def features_to_gdf(features: list, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    if not features:
        raise ValueError("No features to process")

    gdf = gpd.GeoDataFrame.from_features(features, crs=crs)
    logger.info("Created GeoDataFrame with %d rows", len(gdf))
    return gdf


def process_gdf(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:
    gdf = gdf[gdf.geometry.notna()].copy()
    logger.info("Rows after dropping null geometry: %d", len(gdf))

    invalid_before = (~gdf.geometry.is_valid).sum()
    if invalid_before:
        logger.warning("Fixing %d invalid geometries with buffer(0)", invalid_before)
        gdf["geometry"] = gdf.geometry.buffer(0)

    gdf["geometry_valid"] = gdf.geometry.is_valid

    gdf_proj = gdf.to_crs(target_crs)
    gdf["area_ha"] = gdf_proj.geometry.area / 10_000

    centroids = gdf_proj.geometry.centroid.to_crs(4326)
    gdf["centroid_lat"] = centroids.y
    gdf["centroid_lon"] = centroids.x

    logger.info(
        "Processed: area_ha min=%.2f max=%.2f mean=%.2f",
        gdf["area_ha"].min(),
        gdf["area_ha"].max(),
        gdf["area_ha"].mean(),
    )
    return gdf


def export_outputs(gdf: gpd.GeoDataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_cols = ["id", "name", "area_ha", "centroid_lat", "centroid_lon", "geometry_valid"]
    available = [c for c in summary_cols if c in gdf.columns]
    summary = gdf[available]
    summary_path = output_dir / "summary.csv"
    summary.to_csv(summary_path, index=False)
    logger.info("Wrote %s (%d rows)", summary_path, len(summary))

    gpkg_path = output_dir / "polygons_processed.gpkg"
    gdf.to_file(gpkg_path, driver="GPKG")
    logger.info("Wrote %s", gpkg_path)


def run_pipeline(config: dict) -> gpd.GeoDataFrame:
    api_cfg = config["api"]
    output_cfg = config["output"]
    output_dir = Path(output_cfg["dir"])
    target_crs = output_cfg["target_crs"]

    setup_logging(output_dir)

    if api_cfg.get("use_cached", False):
        cached_file = Path(api_cfg["cached_file"])
        features = load_cached_features(cached_file)
    else:
        api_key = get_api_key()
        project_id = api_cfg.get("project_id") or get_project_id()
        if not api_key:
            raise EnvironmentError("MAPID_API_KEY is required when use_cached is false")
        if not project_id:
            raise EnvironmentError("MAPID_PROJECT_ID is required when use_cached is false")

        features = fetch_all_features(
            api_cfg["base_url"],
            api_key,
            project_id,
            api_cfg["layer_id"],
            page_size=api_cfg.get("page_size", 100),
        )
        logger.info("Fetched %d features from MAPID API", len(features))

    gdf = features_to_gdf(features)
    gdf = process_gdf(gdf, target_crs)
    export_outputs(gdf, output_dir)

    logger.info("Pipeline complete.")
    return gdf


def main() -> None:
    parser = argparse.ArgumentParser(description="MAPID polygon batch processing pipeline")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    run_pipeline(config)


if __name__ == "__main__":
    main()
