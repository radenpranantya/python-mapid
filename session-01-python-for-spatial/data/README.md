# Session 1 Sample Data

## Files

| File | Polygons | Purpose |
|------|----------|---------|
| [`sample_response.json`](sample_response.json) | 25 | Notebook fallback (`USE_CACHED = True`) — full QA teaching set |
| [`sample_mapid_upload.geojson`](sample_mapid_upload.geojson) | 25 | **Upload to MAPID** — fixable geometries pre-repaired with buffer(0) |

Regenerate both:

```bash
python3 scripts/generate_sample_data.py
```

Requires `shapely` for the MAPID upload export.

## Composition (25 polygons)

| Group | IDs | Count | MAPID raw upload |
|-------|-----|-------|------------------|
| Valid | poly-001 – poly-008 | 8 | Accepted |
| Severe self-intersection | poly-009 – poly-014 | 6 | Rejected |
| Mild self-intersection | poly-015 – poly-018 | 4 | Often accepted |
| Overlap review | poly-019 – poly-025 | 7 | Accepted |

**Raw JSON upload:** expect ~19 polygons on MAPID (matches platform geometry validation).

**Fixed GeoJSON upload:** all 25 polygons.

## Property fields

| Field | Description |
|-------|-------------|
| `qa_flag` | `none`, `self_intersection`, `sliver`, `minor_overlap`, `major_overlap` |
| `fixable` | `true` if `buffer(0)` applies |
| `invalid_severity` | `severe`, `mild`, or null |
| `expected_mapid_upload` | Predicted acceptance on raw upload |
| `overlap_with` | Partner polygon IDs for overlap cases |
