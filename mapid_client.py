"""MAPID GeoServer API client used by Session 1 notebook and Session 2 pipeline."""

from __future__ import annotations

import os
from typing import Any

import requests

DEFAULT_BASE_URL = "https://geoserver.mapid.io"
DEFAULT_FEATURES_ENDPOINT = "get_layer_data_list"
FALLBACK_FEATURES_ENDPOINTS = (
    "get_layer_data_list",
    "get_layer_data",
    "get_layer_geojson",
    "get_feature_list",
)


def get_api_key() -> str:
    """Return MAPID API key from env (supports legacy MAPID_API_TOKEN name)."""
    return os.getenv("MAPID_API_KEY") or os.getenv("MAPID_API_TOKEN") or ""


def get_project_id() -> str:
    return os.getenv("MAPID_PROJECT_ID", "")


def _query_params(api_key: str, project_id: str, **extra: Any) -> dict[str, Any]:
    params: dict[str, Any] = {"api_key": api_key, "project_id": project_id}
    params.update(extra)
    return params


def fetch_layer_list(
    base_url: str,
    api_key: str,
    project_id: str,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """List polygon layers in a MAPID project."""
    url = f"{base_url.rstrip('/')}/layers_new/get_layer_list"
    resp = requests.get(
        url,
        params=_query_params(api_key, project_id),
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        raise ValueError(f"Expected layer list array, got {type(data).__name__}")
    return data


def resolve_layer_id(
    layers: list[dict[str, Any]],
    layer_id: str = "",
    layer_name: str = "",
) -> str:
    """Find a layer `_id` by explicit id or by case-insensitive name match."""
    if layer_id:
        for layer in layers:
            if layer.get("_id") == layer_id:
                return layer_id
        raise ValueError(f"Layer id not found in project: {layer_id}")

    if not layer_name:
        raise ValueError("Set MAPID_LAYER_ID or MAPID_LAYER_NAME")

    target = layer_name.casefold()
    for layer in layers:
        if str(layer.get("name", "")).casefold() == target:
            return layer["_id"]

    names = [layer.get("name") for layer in layers]
    raise ValueError(f"Layer name not found: {layer_name!r}. Available: {names}")


def _records_to_features(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []
    for record in records:
        if record.get("type") == "Feature" and "geometry" in record:
            features.append(record)
            continue
        geometry = record.get("geometry")
        if not geometry:
            continue
        properties = {
            key: value
            for key, value in record.items()
            if key not in {"geometry", "_id", "type"}
        }
        feature_id = (
            record.get("id")
            or record.get("_id")
            or properties.get("id")
            or properties.get("poly_id")
        )
        features.append(
            {
                "type": "Feature",
                "id": feature_id,
                "geometry": geometry,
                "properties": properties,
            }
        )
    return features


def normalize_to_feature_collection(data: Any) -> dict[str, Any]:
    """Normalize MAPID responses into a GeoJSON FeatureCollection dict."""
    if isinstance(data, dict) and data.get("type") == "FeatureCollection":
        features = data.get("features") or []
        return {"type": "FeatureCollection", "features": features, "total": len(features)}

    if isinstance(data, dict):
        for key in ("features", "data", "result", "layer_data_list", "objects"):
            value = data.get(key)
            if isinstance(value, list):
                features = _records_to_features(value)
                if features:
                    return {
                        "type": "FeatureCollection",
                        "features": features,
                        "total": len(features),
                    }

    if isinstance(data, list):
        features = _records_to_features(data)
        if features:
            return {
                "type": "FeatureCollection",
                "features": features,
                "total": len(features),
            }

    raise ValueError(
        "Could not find polygon features in MAPID response. "
        "Inspect the JSON shape and set MAPID_FEATURES_ENDPOINT if needed."
    )


def fetch_layer_features_raw(
    base_url: str,
    api_key: str,
    project_id: str,
    layer_id: str,
    endpoint: str | None = None,
    timeout: int = 30,
) -> Any:
    """Fetch raw polygon data for one layer."""
    endpoint = endpoint or os.getenv("MAPID_FEATURES_ENDPOINT", DEFAULT_FEATURES_ENDPOINT)
    url = f"{base_url.rstrip('/')}/layers_new/{endpoint}"
    params = _query_params(api_key, project_id, layer_id=layer_id)

    resp = requests.get(url, params=params, timeout=timeout)
    if resp.status_code == 404 and endpoint == DEFAULT_FEATURES_ENDPOINT:
        last_error = resp
        for candidate in FALLBACK_FEATURES_ENDPOINTS:
            if candidate == endpoint:
                continue
            candidate_url = f"{base_url.rstrip('/')}/layers_new/{candidate}"
            candidate_resp = requests.get(
                candidate_url,
                params=params,
                timeout=timeout,
            )
            if candidate_resp.status_code == 200:
                return candidate_resp.json()
            last_error = candidate_resp
        last_error.raise_for_status()

    resp.raise_for_status()
    return resp.json()


def fetch_feature_collection(
    base_url: str,
    api_key: str,
    project_id: str,
    layer_id: str,
    endpoint: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Fetch layer polygons and return a GeoJSON FeatureCollection dict."""
    raw = fetch_layer_features_raw(
        base_url,
        api_key,
        project_id,
        layer_id,
        endpoint=endpoint,
        timeout=timeout,
    )
    return normalize_to_feature_collection(raw)


def fetch_all_features(
    base_url: str,
    api_key: str,
    project_id: str,
    layer_id: str,
    page_size: int = 100,
    endpoint: str | None = None,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """
    Fetch all polygon features for a layer.

    MAPID GeoServer commonly returns the full layer in one response. If the API
    later exposes offset/limit pagination, this function can be extended.
    """
    del page_size  # reserved for future pagination support
    collection = fetch_feature_collection(
        base_url,
        api_key,
        project_id,
        layer_id,
        endpoint=endpoint,
        timeout=timeout,
    )
    return collection["features"]
