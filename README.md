# MAPID Geospatial Teaching Module

Two-session (2.5 hours each) module for teaching Python for geospatial analysis using MAPID custom polygon data via API.

## Audience

Mixed beginner to mid-level mentees. No senior track.

## Sessions

| Session | Topic | Folder |
|---------|-------|--------|
| 1 | Python for Spatial | [`session-01-python-for-spatial/`](session-01-python-for-spatial/) |
| 2 | Automation in Geospatial (Python + n8n) | [`session-02-automation/`](session-02-automation/) |

See agendas: [`docs/session01_agenda.md`](docs/session01_agenda.md), [`docs/session02_agenda.md`](docs/session02_agenda.md).

Session 1 live API run guide: [`docs/session01_run_guide.md`](docs/session01_run_guide.md).

## Pre-session setup (mentees)

### 1. Python environment

```bash
conda create -n mapid-geo python=3.11 -y
conda activate mapid-geo
pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
# Edit .env with MAPID_API_KEY, MAPID_PROJECT_ID, and MAPID_LAYER_ID
```

### 3. Verify install

```bash
python -c "import geopandas; import requests; print('OK')"
```

### 4. n8n access (required before Session 2)

Session 2 includes **mandatory** n8n hands-on (40 min). Before Session 2:

- Confirm access to shared n8n instance (instructor-provided), **or**
- Install local n8n via npm — see [`docs/install_n8n_npm.md`](docs/install_n8n_npm.md), **or**
- Install via Docker/self-hosted, **or**
- Create n8n.cloud account (webhook wrapper needed for Execute Command)

Install guide: [`docs/install_n8n_npm.md`](docs/install_n8n_npm.md)

Hands-on guide: [`docs/session02_n8n_hands_on.md`](docs/session02_n8n_hands_on.md)

## Repository layout

```
├── docs/                          # Agendas, API contract, rubric, instructor notes
├── session-01-python-for-spatial/ # Session 1 materials + sample data
├── session-02-automation/         # Session 2 pipeline, n8n workflow, batch data
├── hometask/                      # Assignment instructions + starter template
└── scripts/                       # Instructor utilities (sample data generator)
```

## API contract

MAPID GeoServer API contract and env vars:

[`docs/mapid_api_contract.md`](docs/mapid_api_contract.md)

Shared client: [`mapid_client.py`](mapid_client.py). Session 1 notebook and Session 2 pipeline read from `config.yaml` + environment variables.

## Offline fallback

If the live API is unavailable during class, both sessions include cached GeoJSON sample files under each session's `data/` folder.

## Hometask

Pure processing (100–200 polygons) **plus mandatory n8n workflow**. Both Python and n8n are required.

[`hometask/instructions.md`](hometask/instructions.md)

## Instructor resources

- [`docs/instructor_notes.md`](docs/instructor_notes.md)
- [`docs/hometask_rubric.md`](docs/hometask_rubric.md)
- [`docs/session01_code_mindmap.md`](docs/session01_code_mindmap.md)
- [`docs/install_n8n_npm.md`](docs/install_n8n_npm.md)
- [`docs/session02_n8n_hands_on.md`](docs/session02_n8n_hands_on.md)
