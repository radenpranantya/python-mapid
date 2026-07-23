# n8n Workflow — MAPID Polygon Pipeline

Importable workflow for **mandatory** Session 2 hands-on and hometask submission.

**File:** [`mapid_polygon_pipeline.json`](mapid_polygon_pipeline.json)

**Hands-on guide:** [`../../docs/session02_n8n_hands_on.md`](../../docs/session02_n8n_hands_on.md)

## Architecture

```
Manual Trigger → Set Variables → HTTP Request (MAPID API)
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
- MAPID API bearer token

## Import steps

1. Open n8n → **Workflows** → **Import from File**
2. Select `mapid_polygon_pipeline.json`
3. Open imported workflow and update nodes (see below)

## Node configuration

### 1. Set Variables

Update these assignment values:

| Variable | Description |
|----------|-------------|
| `base_url` | MAPID API base URL (placeholder: `https://api.mapid.example/v1`) |
| `layer_id` | Your polygon layer ID |
| `page_size` | API page size (default: 100) |
| `offset` | Start at 0 (used for single-page demo) |
| `pipeline_dir` | Absolute path to `session-02-automation/` on the n8n host |

### 2. HTTP Request MAPID

- **Method:** GET
- **URL:** `={{ $json.base_url }}/layers/{{ $json.layer_id }}/features`
- **Auth:** HTTP Bearer Auth credential

**Create credential:**
1. n8n → Credentials → Add → **Bearer Auth**
2. Name: `MAPID Bearer Token`
3. Token: your `MAPID_API_TOKEN`

Re-link credential on the HTTP Request node after import.

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

Output status for demo and hometask. Extend with Slack or Email node for production.

## Recommended pattern (mandatory cohort)

**n8n triggers Python; Python handles pagination.**

1. Set `use_cached: false` for hometask submission (live API)
2. n8n runs: `python3 pipeline.py --config config.yaml`
3. Pagination lives in Python — simpler for beginners, still meets n8n requirement

## Extending with pagination in n8n (mid mentees)

For mentees who want HTTP pagination inside n8n:

### Option A: HTTP Request built-in pagination

1. Open HTTP Request node → **Add Option** → **Pagination**
2. Mode: **Update a Parameter in Each Request**
3. Parameter: `offset`, increment by `page_size` each request
4. Stop when response `features` array is empty

### Option B: Loop node

```
Set Variables (offset=0)
  → Loop:
      HTTP Request (offset={{ $json.offset }})
      → IF features.length > 0
          → Append to aggregate
          → offset += page_size
      → ELSE break
  → Execute Python Pipeline
```

## Testing without live API

1. Set `use_cached: true` in `config.yaml`
2. Run workflow manually in n8n
3. Verify `output/summary.csv` and `output/run.log` created on n8n host

## Hometask submission

Export workflow after successful test:

1. n8n → Workflow → **Download**
2. Submit as `workflow.json`
3. Include screenshot of successful execution
4. Include `n8n_README.md` with credential setup notes (no tokens)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Execute Command not available | Use self-hosted n8n or webhook wrapper |
| `python3: not found` | Use full path or conda env path |
| Permission denied on pipeline_dir | Check n8n process user has read/execute access |
| 401 from MAPID | Re-create Bearer credential |
| Pipeline runs but empty output | Check `config.yaml` paths relative to `pipeline_dir` |
