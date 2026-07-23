# n8n Workflow — MAPID Polygon Pipeline

Importable workflow for **mandatory** Session 2 hands-on and hometask submission.

**File:** [`mapid_polygon_pipeline.json`](mapid_polygon_pipeline.json)

**Hands-on guide:** [`../../docs/session02_n8n_hands_on.md`](../../docs/session02_n8n_hands_on.md)

## Architecture

```
Manual Trigger → Set Variables → HTTP Request (MAPID GeoServer API)
                                      ↓
                               IF API Success?
                              ↙              ↘
              Execute Python Pipeline    Set Failure
                      ↓
                 Set Success
```

**Important:** All spatial processing stays in Python. n8n orchestrates trigger + status routing.

## Prerequisites

- n8n instance (shared self-hosted recommended for cohort) — install locally via [`../../docs/install_n8n_npm.md`](../../docs/install_n8n_npm.md)
- Python environment with module dependencies installed
- `pipeline.py` and `config.yaml` in `session-02-automation/`
- MAPID API key, project id, and layer id

## Import steps

1. Open n8n → **Workflows** → **Import from File**
2. Select `mapid_polygon_pipeline.json`
3. Open imported workflow and update nodes (see below)

## Node configuration

### 1. Set Variables

Update these assignment values:

| Variable | Description |
|----------|-------------|
| `base_url` | MAPID GeoServer base URL (`https://geoserver.mapid.io`) |
| `api_key` | Your MAPID API key (query param — not Bearer header) |
| `project_id` | GEO MAPID project id |
| `layer_id` | Layer `_id` from `get_layer_list` |
| `features_endpoint` | Feature endpoint name (default: `get_layer_data_list`) |
| `pipeline_dir` | Absolute path to `session-02-automation/` on the n8n host |

Find layer id:

```bash
curl -s "https://geoserver.mapid.io/layers_new/get_layer_list?api_key=YOUR_KEY&project_id=YOUR_PROJECT_ID"
```

### 2. HTTP Request MAPID

- **Method:** GET
- **URL:** `={{ $json.base_url }}/layers_new/{{ $json.features_endpoint }}`
- **Query params:** `api_key`, `project_id`, `layer_id`
- **Auth:** none (key is passed as query param)

For class demos, set `use_cached: true` in `config.yaml` so the Python pipeline still runs if the feature endpoint is unavailable.

### 3. IF API Success

Checks `statusCode == 200`. True branch runs pipeline; false branch sets error message.

### 4. Execute Python Pipeline

Runs on the **n8n host machine** (self-hosted):

```bash
cd {{ pipeline_dir }} && python3 pipeline.py --config config.yaml
```

**Requirements:**
- n8n must have shell access to the pipeline directory
- `config.yaml` should use `use_cached: true` for class demo if live API unavailable
- Python 3.11+ with geopandas installed in PATH

**n8n.cloud alternative:** Replace Execute Command with HTTP Request POST to a local webhook wrapper that runs the pipeline.

### 5. Set Success / Set Failure

Status nodes for workflow output and debugging.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 404 from MAPID | Confirm `features_endpoint` and `layer_id` |
| 401/403 from MAPID | Check `api_key` value in Set Variables |
| Pipeline not found | Set absolute `pipeline_dir` path |
| Python not found | Use full path to venv python in Execute Command |
| Empty features | Inspect HTTP response body; adjust endpoint per [`../../docs/mapid_api_contract.md`](../../docs/mapid_api_contract.md) |

## Security note

Do not hard-code live API keys in exported workflow JSON for production. Prefer n8n credentials or environment variables on the host.
