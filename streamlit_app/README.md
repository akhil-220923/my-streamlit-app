# IBVAP — Intelligent Border Video Analytics Platform

## Streamlit Python Application

AI-Powered Border Surveillance, Intrusion Detection & Security Analytics
SIH 2026 — Blockchain & Cybersecurity

## Quick Start

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

The app starts on http://localhost:8501

## Architecture

```
streamlit_app/
├── app.py                      # Main entry — navigation, sidebar, header, footer
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml             # Dark navy theme config
├── components/
│   └── ui_components.py         # Reusable UI: badges, cards, pipeline, empty states
├── pages/
│   ├── command_center.py        # Dashboard — metrics, system health, threat status, charts
│   ├── surveillance.py          # Video player, event timeline, restricted zone panel
│   ├── security_events.py       # Event table with search/filter/sort, detail modal
│   ├── digital_evidence.py       # Evidence gallery with zoom/download/viewer
│   ├── audit_log.py             # Audit table, CSV download, cybersecurity architecture
│   └── system_page.py            # Technical info, pipeline, current vs future architecture
├── utils/
│   └── data_service.py          # Data layer — Supabase / CSV / seed fallback
└── pages/__init__.py
```

## Data Sources

The data service layer tries three sources in order:

1. **Supabase** — if `SUPABASE_URL` and `SUPABASE_ANON_KEY` env vars are set, fetches from the `intrusion_events` table
2. **Local CSV** — reads `output/intrusion_log.csv` if it exists
3. **Seed data** — falls back to the three prototype events (Track 2, Track 7, Track 36)

This makes the data layer replaceable by a REST API later.

## Pages

| Page | Description |
|------|-------------|
| Command Center | Executive dashboard with 4 metric cards, system health, threat status, AI pipeline, charts |
| Surveillance | Video player, interactive event timeline, restricted zone visualization |
| Security Events | Data table with search/filter/sort, event detail modal with evidence/video/download |
| Digital Evidence | Evidence gallery with image cards, zoom viewer, download |
| Audit Log | Structured audit table, CSV export, current vs future blockchain architecture |
| System | Technical module info, security pipeline, cybersecurity architecture |

## AI Pipeline

```
Video Input → YOLO11 Detection → ByteTrack Tracking → Zone Analysis →
Intrusion Detection → Timestamp → Risk Classification → Evidence Capture → Audit Log
```

## Tech Stack

- **Streamlit** — web framework
- **Plotly** — charts (risk distribution, intrusion timeline)
- **Pandas** — data manipulation
- **Supabase** — optional database backend
- **Pillow** — image handling for evidence
- **Requests** — fetching evidence images

## Environment Variables

Optional — only needed if using Supabase as the data source:

```
SUPABASE_URL=your_project_url
SUPABASE_ANON_KEY=your_anon_key
```

Without these, the app uses seed data or the local CSV.

## Notes

- Person Track IDs are ByteTrack session identifiers, not permanent real-world identities
- Blockchain integration is labeled as "Future Enhancement" — not yet implemented
- The app does not claim facial recognition, SMS/email alerts, or cloud deployment
