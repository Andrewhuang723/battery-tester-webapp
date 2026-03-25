# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

**Development** (port 5001):
```bash
pip install -r requirements.txt
python app.py
```

**Production** (port 5000):
```bash
python app_production.py
# or with gunicorn:
gunicorn --bind 0.0.0.0:5000 --workers 2 app_production:app
```

**One-click startup with auto-dependency check**:
```bash
./start_webapp.sh
```

**Health check**: `GET /health`

## Architecture

Flask web app for processing CSV output from Chengde brand battery charger/discharger devices.

### Two App Versions

| | `app.py` | `app_production.py` |
|---|---|---|
| Port | 5001 | 5000 |
| Storage | `uploads/`, `processed/` | `/tmp/uploads/`, `/tmp/processed/` |
| Response | Full CSV in JSON | Gzip + Base64 compressed |
| Memory | Standard | Optimized (StringIO, gc.collect) |

### Data Flow

1. User uploads CSV → `POST /upload` (multipart form)
2. `extract_origin_csv()` parses the Chengde-specific format → returns StringIO buffer + step boundary indices
3. Pandas reads the buffer → validates dates, converts numeric columns
4. Two outputs generated: **detail CSV** (all rows) and **step CSV** (rows at step boundaries only)
5. In production: both CSVs are gzip-compressed then base64-encoded to stay under Vercel's 4.5MB limit
6. Browser decompresses using Pako library and generates download Blobs

### Key Components

- **`app_production.py`**: Main production entry point. Contains `extract_origin_csv()`, `process_battery_data()`, and all Flask routes.
- **`utils.py`**: Shared utility functions.
- **`templates/index.html`**: Single-page frontend — drag-and-drop upload, progress bar, status badges, download links. Uses Pako for client-side gzip decompression.
- **`run_gui.py`**: Standalone Tkinter desktop GUI (no web server).

### Chengde CSV Format

The source CSVs have a non-standard multi-section header:
```
%	Time
@	16
Label	Fuction	Set	Record Time	Change	...
            "Charge	CC-CV	I=2.500	V=3.700"	00:15.0	...
$	16	Loop (S1)=1/2000	Loop (S2)=8/100	...
System Time	Step Time	V	I	T	R	P	mAh	Wh	Total Time
[data rows...]
```

`extract_origin_csv()` parses this by detecting the `%` marker line, extracting step names from label rows, then reading actual data rows. It detects encoding automatically (UTF-8 → CP950/Traditional Chinese → Latin-1).

## Deployment

Supported platforms: Vercel (`vercel.json`), Railway (`railway.json`), Render, Docker (`Dockerfile`), Heroku (`Procfile`).

For serverless platforms (Vercel): the compressed response pattern is critical — serverless functions cannot store files between requests, so all data must be returned in the response body within the payload limit.
