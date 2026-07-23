# Hometask — Processing + n8n Orchestration (Session 2)

## Overview

Build a **Python pipeline** and an **n8n workflow** that processes **100–200 custom polygons** from your assigned MAPID layer. **No visualization required.**

Both Python and n8n are **mandatory**.

**Deadline:** Set by instructor.

---

## Part 1 — Python pipeline (required)

### Task

1. **Fetches** all polygons from your assigned MAPID layer using API pagination
2. **Processes** each polygon:
   - Drop null geometries
   - Fix invalid geometries (`buffer(0)`) and log count fixed
   - Compute `area_ha` in a projected CRS (document your EPSG choice)
   - Compute `centroid_lat` and `centroid_lon` (WGS84)
   - Set `geometry_valid` (boolean)
3. **Exports** three files to `output/`:
   - `summary.csv`
   - `polygons_processed.gpkg`
   - `run.log`

### CLI

```bash
python pipeline.py --config config.yaml
```

### Config

```bash
cp config.example.yaml config.yaml
export MAPID_API_KEY=your_api_key
export MAPID_PROJECT_ID=your_project_id
```

Set `use_cached: false`, your assigned `layer_id`, and `project_id` in `config.yaml` for submission.

### Output schema — `summary.csv`

| Column | Type | Description |
|--------|------|-------------|
| `id` | string | Polygon ID |
| `name` | string | Polygon name (if available) |
| `area_ha` | float | Area in hectares |
| `centroid_lat` | float | Centroid latitude (WGS84) |
| `centroid_lon` | float | Centroid longitude (WGS84) |
| `geometry_valid` | bool | True if geometry is valid after processing |

---

## Part 2 — n8n workflow (required)

Wrap your Python pipeline in an n8n workflow that:

1. **Triggers** the pipeline (Manual Trigger or Schedule)
2. **Executes** `python pipeline.py --config config.yaml` (Execute Command or webhook)
3. **Branches** on success vs failure (IF node)
4. **Reports status** (Set node, Slack, email, or n8n execution log)

**Recommended:** n8n triggers Python; pagination stays in Python (not in n8n).

Starter template: [`../session-02-automation/n8n/`](../session-02-automation/n8n/)

Setup guide: [`../docs/session02_n8n_hands_on.md`](../docs/session02_n8n_hands_on.md)

---

## Submission structure

```
your-name-hometask/
├── pipeline.py
├── config.yaml              # NO token committed — use env var
├── README.md                # How to run Python, CRS choice, assumptions
├── workflow.json            # Exported n8n workflow — REQUIRED
├── n8n_README.md            # How to import and run the workflow
├── screenshot_success.png   # Proof of successful n8n execution
└── output/
    ├── summary.csv
    ├── polygons_processed.gpkg
    └── run.log
```

---

## Tips

- Test Python with cached data first (`use_cached: true`), then switch to live API
- Test n8n with `use_cached: true` before connecting live API
- Document which UTM zone you chose and why
- Do not commit `.env`, API tokens, or n8n credentials

## Rubric

See [`../docs/hometask_rubric.md`](../docs/hometask_rubric.md) — 60 pts Python + 40 pts n8n
