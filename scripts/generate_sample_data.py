#!/usr/bin/env python3
"""Generate synthetic MAPID polygon sample data for teaching module.

Instructor-only utility. Regenerates cached JSON files used when live API
is unavailable during class.

Session 1 sample: 25 polygons
  - 8 valid (no QA issue)
  - 10 self-intersection / sliver (6 severe + 4 mild, all fixable with buffer(0))
  - 7 overlap review (valid geometry, manual decision)

Outputs:
  - sample_response.json       — full teaching set (all 25)
  - sample_mapid_upload.geojson — buffer(0) on fixable features for MAPID upload

Usage:
    python scripts/generate_sample_data.py
"""

from __future__ import annotations

import json
import random
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SESSION1_DATA = ROOT / "session-01-python-for-spatial" / "data" / "sample_response.json"
SESSION1_MAPID_UPLOAD = ROOT / "session-01-python-for-spatial" / "data" / "sample_mapid_upload.geojson"
SESSION2_DATA = ROOT / "session-02-automation" / "data" / "sample_batch_response.json"

CATEGORIES = ["commercial", "residential", "industrial", "mixed", "green"]

LON_MIN, LON_MAX = 106.75, 107.05
LAT_MIN, LAT_MAX = -6.35, -6.05


def _square_ring(lon: float, lat: float, half: float) -> list:
    return [
        [lon - half, lat - half],
        [lon + half, lat - half],
        [lon + half, lat + half],
        [lon - half, lat + half],
        [lon - half, lat - half],
    ]


def _bowtie_ring(lon: float, lat: float, half: float) -> list:
    return [
        [lon - half, lat - half],
        [lon + half, lat + half],
        [lon + half, lat - half],
        [lon - half, lat + half],
        [lon - half, lat - half],
    ]


def _kink_ring(lon: float, lat: float, half: float) -> list:
    return [
        [lon - half, lat - half],
        [lon, lat + half],
        [lon + half, lat - half],
        [lon - half, lat],
        [lon + half, lat + half],
        [lon - half, lat - half],
    ]


def _duplicate_vertex_ring(lon: float, lat: float, half: float) -> list:
    ring = _square_ring(lon, lat, half)
    ring.insert(2, ring[2][:])
    return ring


def _spike_ring(lon: float, lat: float, half: float) -> list:
    return [
        [lon - half, lat - half],
        [lon + half, lat - half],
        [lon + half, lat + half],
        [lon - half, lat + half],
        [lon, lat + half * 3],
        [lon - half, lat + half],
        [lon - half, lat - half],
    ]


def _offset_square_ring(lon: float, lat: float, half: float, d_lon: float, d_lat: float = 0.0) -> list:
    return _square_ring(lon + d_lon, lat + d_lat, half)


def _feature(
    idx: int,
    coords: list,
    category: str,
    *,
    qa_flag: str = "none",
    fixable: bool = False,
    fix_method: str = "none",
    invalid_severity: str | None = None,
    expected_mapid_upload: bool = True,
    overlap_with: list[str] | None = None,
    overlap_pct: float | None = None,
    instructor_note: str = "",
) -> dict:
    feature_id = f"poly-{idx:03d}"
    return {
        "type": "Feature",
        "id": feature_id,
        "geometry": {"type": "Polygon", "coordinates": [coords]},
        "properties": {
            "id": feature_id,
            "name": f"Zone {idx:02d}",
            "category": category,
            "qa_flag": qa_flag,
            "fixable": fixable,
            "fix_method": fix_method,
            "invalid_severity": invalid_severity,
            "expected_mapid_upload": expected_mapid_upload,
            "overlap_with": overlap_with,
            "overlap_pct": overlap_pct,
            "instructor_note": instructor_note,
        },
    }


def build_session1_collection(seed: int = 42) -> dict:
    """25 polygons: 8 valid + 10 fixable self-intersection + 7 overlap review."""
    rng = random.Random(seed)
    features: list[dict] = []
    idx = 1

    valid_centers = [
        (106.76, -6.32),
        (106.79, -6.32),
        (106.82, -6.32),
        (106.85, -6.32),
        (106.76, -6.28),
        (106.79, -6.28),
        (106.82, -6.28),
        (106.85, -6.28),
    ]
    for lon, lat in valid_centers:
        features.append(
            _feature(
                idx,
                _square_ring(lon, lat, 0.004),
                rng.choice(CATEGORIES),
                qa_flag="none",
                fixable=False,
                invalid_severity=None,
                expected_mapid_upload=True,
                instructor_note="Valid geometry — no correction needed",
            )
        )
        idx += 1

    severe_specs = [
        ("self_intersection", _bowtie_ring(106.77, -6.24, 0.005), "Severe bowtie — MAPID likely rejects; fix with buffer(0)"),
        ("self_intersection", _bowtie_ring(106.80, -6.24, 0.005), "Severe bowtie — MAPID likely rejects; fix with buffer(0)"),
        ("self_intersection", _bowtie_ring(106.83, -6.24, 0.005), "Severe bowtie — MAPID likely rejects; fix with buffer(0)"),
        ("self_intersection", _kink_ring(106.86, -6.24, 0.005), "Severe kink — MAPID likely rejects; fix with buffer(0)"),
        ("self_intersection", _kink_ring(106.89, -6.24, 0.005), "Severe kink — MAPID likely rejects; fix with buffer(0)"),
        ("sliver", _spike_ring(106.92, -6.24, 0.004), "Severe spike — MAPID likely rejects; fix with buffer(0)"),
    ]
    for qa_flag, ring, note in severe_specs:
        features.append(
            _feature(
                idx,
                ring,
                rng.choice(CATEGORIES),
                qa_flag=qa_flag,
                fixable=True,
                fix_method="buffer_0",
                invalid_severity="severe",
                expected_mapid_upload=False,
                instructor_note=note,
            )
        )
        idx += 1

    mild_specs = [
        ("sliver", _duplicate_vertex_ring(106.77, -6.20, 0.004), "Mild duplicate vertex — MAPID may accept; fix with buffer(0)"),
        ("sliver", _duplicate_vertex_ring(106.80, -6.20, 0.004), "Mild duplicate vertex — MAPID may accept; fix with buffer(0)"),
        ("self_intersection", _bowtie_ring(106.83, -6.20, 0.002), "Mild small bowtie — borderline upload; fix with buffer(0)"),
        ("self_intersection", _bowtie_ring(106.86, -6.20, 0.002), "Mild small bowtie — borderline upload; fix with buffer(0)"),
    ]
    for qa_flag, ring, note in mild_specs:
        features.append(
            _feature(
                idx,
                ring,
                rng.choice(CATEGORIES),
                qa_flag=qa_flag,
                fixable=True,
                fix_method="buffer_0",
                invalid_severity="mild",
                expected_mapid_upload=True,
                instructor_note=note,
            )
        )
        idx += 1

    half = 0.005
    base_lon, base_lat = 106.90, -6.30
    id_a, id_b = f"poly-{idx:03d}", f"poly-{idx + 1:03d}"
    features.append(
        _feature(
            idx,
            _square_ring(base_lon, base_lat, half),
            "commercial",
            qa_flag="minor_overlap",
            fixable=False,
            fix_method="manual_review",
            invalid_severity=None,
            expected_mapid_upload=True,
            overlap_with=[id_b],
            overlap_pct=12.0,
            instructor_note="Minor overlap — valid geometry, needs human decision",
        )
    )
    idx += 1
    features.append(
        _feature(
            idx,
            _offset_square_ring(base_lon, base_lat, half, d_lon=0.0088),
            "commercial",
            qa_flag="minor_overlap",
            fixable=False,
            fix_method="manual_review",
            invalid_severity=None,
            expected_mapid_upload=True,
            overlap_with=[id_a],
            overlap_pct=12.0,
            instructor_note="Minor overlap — valid geometry, needs human decision",
        )
    )
    idx += 1

    base_lon, base_lat = 106.90, -6.26
    id_a, id_b = f"poly-{idx:03d}", f"poly-{idx + 1:03d}"
    features.append(
        _feature(
            idx,
            _square_ring(base_lon, base_lat, half),
            "residential",
            qa_flag="minor_overlap",
            fixable=False,
            fix_method="manual_review",
            invalid_severity=None,
            expected_mapid_upload=True,
            overlap_with=[id_b],
            overlap_pct=22.0,
            instructor_note="Minor overlap — valid geometry, needs human decision",
        )
    )
    idx += 1
    features.append(
        _feature(
            idx,
            _offset_square_ring(base_lon, base_lat, half, d_lon=0.0078),
            "residential",
            qa_flag="minor_overlap",
            fixable=False,
            fix_method="manual_review",
            invalid_severity=None,
            expected_mapid_upload=True,
            overlap_with=[id_a],
            overlap_pct=22.0,
            instructor_note="Minor overlap — valid geometry, needs human decision",
        )
    )
    idx += 1

    center_lon, center_lat = 106.94, -6.22
    ids = [f"poly-{idx:03d}", f"poly-{idx + 1:03d}", f"poly-{idx + 2:03d}"]
    halves = [0.008, 0.006, 0.004]
    categories = ["industrial", "mixed", "green"]
    for i, (h, cat) in enumerate(zip(halves, categories)):
        others = [x for j, x in enumerate(ids) if j != i]
        features.append(
            _feature(
                idx,
                _square_ring(center_lon, center_lat, h),
                cat,
                qa_flag="major_overlap",
                fixable=False,
                fix_method="manual_review",
                invalid_severity=None,
                expected_mapid_upload=True,
                overlap_with=others,
                overlap_pct=50.0,
                instructor_note="Major overlap — likely digitizing error, manual review required",
            )
        )
        idx += 1

    assert len(features) == 25, f"Expected 25 features, got {len(features)}"

    severe = sum(1 for f in features if f["properties"].get("invalid_severity") == "severe")
    mild = sum(1 for f in features if f["properties"].get("invalid_severity") == "mild")

    return {
        "type": "FeatureCollection",
        "total": 25,
        "features": features,
        "metadata": {
            "description": "Session 1 teaching sample: 8 valid + 10 fixable + 7 overlap",
            "valid_count": 8,
            "qa_issue_count": 17,
            "fixable_count": 10,
            "severe_invalid_count": severe,
            "mild_invalid_count": mild,
            "overlap_review_count": 7,
            "expected_mapid_upload_raw": sum(
                1 for f in features if f["properties"].get("expected_mapid_upload")
            ),
        },
    }


def build_mapid_upload_collection(session1: dict) -> dict:
    """Apply buffer(0) to fixable features for MAPID upload (all 25 valid geometry)."""
    from shapely.geometry import mapping, shape

    fixed_features = []
    for feature in session1["features"]:
        props = deepcopy(feature["properties"])
        geom = shape(feature["geometry"])
        if props.get("fixable"):
            geom = geom.buffer(0)
        fixed_features.append(
            {
                "type": "Feature",
                "id": feature["id"],
                "geometry": mapping(geom),
                "properties": props,
            }
        )

    return {
        "type": "FeatureCollection",
        "total": len(fixed_features),
        "features": fixed_features,
        "metadata": {
            "description": "MAPID upload version — fixable geometries repaired with buffer(0)",
            "source": "sample_response.json",
            "note": "Upload this file to MAPID for all 25 polygons. Overlap QA still present.",
        },
    }


def _random_polygon(lon: float, lat: float, size: float, rng: random.Random) -> list:
    half = size / 2
    return _square_ring(lon, lat, half)


def _bowtie_polygon(lon: float, lat: float, size: float) -> list:
    half = size / 2
    return _bowtie_ring(lon, lat, half)


def make_feature(
    idx: int,
    rng: random.Random,
    *,
    invalid: bool = False,
    lon_range=(LON_MIN, LON_MAX),
    lat_range=(LAT_MIN, LAT_MAX),
) -> dict:
    lon = rng.uniform(*lon_range)
    lat = rng.uniform(*lat_range)
    size = rng.uniform(0.002, 0.015)

    if invalid:
        coords = _bowtie_polygon(lon, lat, size)
    else:
        coords = _random_polygon(lon, lat, size, rng)

    feature_id = f"poly-{idx:03d}"
    return {
        "type": "Feature",
        "id": feature_id,
        "geometry": {"type": "Polygon", "coordinates": [coords]},
        "properties": {
            "id": feature_id,
            "name": f"Zone {chr(65 + (idx % 26))}{idx // 26 or ''}".strip(),
            "category": rng.choice(CATEGORIES),
            "qa_flag": "self_intersection" if invalid else "none",
            "fixable": invalid,
            "fix_method": "buffer_0" if invalid else "none",
            "invalid_severity": "severe" if invalid else None,
            "expected_mapid_upload": not invalid,
            "overlap_with": None,
            "overlap_pct": None,
            "instructor_note": "",
        },
    }


def build_collection(count: int, invalid_count: int = 0, seed: int = 42) -> dict:
    rng = random.Random(seed)
    features = []
    invalid_indices = set(rng.sample(range(count), min(invalid_count, count)))

    for i in range(count):
        features.append(
            make_feature(i + 1, rng, invalid=(i in invalid_indices))
        )

    return {
        "type": "FeatureCollection",
        "total": count,
        "features": features,
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {path} ({len(data['features'])} features)")


def print_session1_summary(data: dict) -> None:
    features = data["features"]
    props = [f["properties"] for f in features]
    none = sum(1 for p in props if p["qa_flag"] == "none")
    fixable = sum(1 for p in props if p["fixable"])
    overlap = sum(1 for p in props if "overlap" in p["qa_flag"])
    severe = sum(1 for p in props if p.get("invalid_severity") == "severe")
    mild = sum(1 for p in props if p.get("invalid_severity") == "mild")
    expected_raw = sum(1 for p in props if p.get("expected_mapid_upload"))
    print(f"  Valid (qa_flag=none): {none}")
    print(f"  Self-intersection/sliver (fixable): {fixable} (severe={severe}, mild={mild})")
    print(f"  Overlap review: {overlap}")
    print(f"  Expected MAPID upload (raw file): ~{expected_raw} polygons")


def main() -> None:
    session1 = build_session1_collection(seed=42)
    session2 = build_collection(150, invalid_count=5, seed=123)

    write_json(SESSION1_DATA, session1)
    print("Session 1 summary:")
    print_session1_summary(session1)

    try:
        mapid_upload = build_mapid_upload_collection(session1)
        write_json(SESSION1_MAPID_UPLOAD, mapid_upload)
        print("  MAPID upload file: all 25 with buffer(0) on fixable")
    except ImportError:
        print("  Skipped sample_mapid_upload.geojson (install shapely: pip install shapely)")

    write_json(SESSION2_DATA, session2)


if __name__ == "__main__":
    main()
