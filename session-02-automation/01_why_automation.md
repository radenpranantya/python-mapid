# Why Automation in Geospatial?

## The problem (15 min)

When you manage custom polygons on MAPID, repetitive tasks add up fast:

| Task | Manual (150 polygons) | Automated |
|------|----------------------|-----------|
| Fetch from API | Multiple copy-paste calls | One paginated script |
| Compute area + centroid | Spreadsheet per row | Vectorized GeoPandas |
| Fix invalid geometry | One-by-one in GIS UI | `buffer(0)` in batch |
| Export consistent outputs | Inconsistent filenames | `summary.csv` + `.gpkg` every run |
| Re-run next week | Start over | `python pipeline.py --config config.yaml` |
| Schedule weekly run | Calendar reminder | n8n schedule → auto-trigger |

## Session 1 vs Session 2

| Session 1 | Session 2 |
|-----------|-----------|
| Notebook prototype | Production script + n8n workflow |
| ~25 polygons (8 valid + 10 fixable + 7 overlap) | 100–200 polygons |
| Interactive exploration | Batch processing |
| Manual "Run All" | CLI + **mandatory** n8n orchestration |

## Production stack: Python + n8n

| Layer | Tool | Responsibility |
|-------|------|----------------|
| **Spatial engine** | Python / GeoPandas | Fetch, process, export |
| **Orchestrator** | n8n | Trigger, schedule, retry, notify |

You need **both** for production automation.

## What we automate (and what we don't)

**Python automates:**
- API fetch with pagination
- Geometry validation and repair
- CRS reprojection and area calculation
- File export and logging

**n8n automates:**
- When to run the pipeline (manual, schedule, webhook)
- Success vs failure routing
- Notifications (Slack, email, or status log)

**Don't put in n8n:**
- Spatial math (area, CRS, validity) — stays in Python/GeoPandas

## Real MAPID scenario

> Client layer has 187 custom polygons. Every Monday, export updated areas (ha) and centroids for reporting.

**Solution:** n8n schedule → trigger `pipeline.py` → CSV to shared drive → Slack notification.

## Discussion

1. What would you automate first in your MAPID workflow?
2. Where do errors happen most (API, geometry, export)?
3. Who needs the output (you, manager, client)?
