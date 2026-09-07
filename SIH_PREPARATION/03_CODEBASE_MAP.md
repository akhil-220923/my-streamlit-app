# IBVAP — Exact Codebase Map & Module Inventory
## 03. Comprehensive Inventory & Symbol Mapping

---

### 1. Primary Source Files Inventory

| File Path | Purpose | Key Functions / Classes | Inputs | Outputs | Deployment Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `src/main.py` | Core execution script for YOLO tracking | Loop logic using Ultralytics & OpenCV | `../data/video.mp4`, `yolo11s.pt` | GUI Window display | Development / Standalone Pipeline |
| `src/app.py` | Complete single-file Streamlit web app | `fetch_events`, `_try_mongodb`, `_try_csv`, `verify_secure_audit_log`, `create_blockchain_ledger`, `verify_blockchain_ledger`, `render_*` | Env Vars, CSVs, JSON, Videos | Full Interactive Web App | Production / Streamlit Cloud Option 1 |
| `streamlit_app/app.py` | Modular Streamlit entry point | `main()`, `navigate()`, `render_sidebar()`, `render_header()` | Session State, Data Service | Navigated Web View | Production / Streamlit Cloud Option 2 |
| `streamlit_app/utils/data_service.py` | Abstraction layer for event data | `IntrusionEvent`, `fetch_events`, `_try_supabase`, `_try_csv`, `_seed_events` | Supabase API, CSV file | List of `IntrusionEvent` objects | Production Utility |
| `streamlit_app/components/ui_components.py` | Custom HTML/CSS component generators | `risk_badge`, `status_indicator`, `metric_card_html`, `security_pipeline_html` | Component parameters | HTML formatted string | Production UI Component |
| `streamlit_app/pages/command_center.py` | Command Center view renderer | `render(events)` | Event list | Executive Dashboard UI | Production Page |
| `streamlit_app/pages/surveillance.py` | Video Feed & Zone view renderer | `render(events)` | Event list, Video File | Surveillance Player & Timeline UI | Production Page |
| `streamlit_app/pages/security_events.py` | Security Event Management renderer | `render(events)`, `_render_event_modal(event)` | Event list | Data Table & Modal UI | Production Page |
| `streamlit_app/pages/digital_evidence.py` | Evidence Gallery renderer | `render(events)` | Event list, Image files/URLs | Evidence Grid & Viewer UI | Production Page |
| `streamlit_app/pages/audit_log.py` | Audit Log & Integrity renderer | `render(events)` | Event list, Audit files | Audit Table & Export UI | Production Page |
| `streamlit_app/pages/system_page.py` | Technical System info renderer | `render(events)` | Event list | System Module Info UI | Production Page |
| `bytetrack_day3.yaml` | ByteTrack tracker hyperparameters | `tracker_type`, `track_high_thresh`, `track_buffer`, etc. | YAML parser | Tracker Config Dict | Model Config File |

---

### 2. Configuration & Data Artifacts

| Artifact Name | Path | Description / Contents |
| :--- | :--- | :--- |
| `video.mp4` | `data/video.mp4` | Raw surveillance video input feed (2.19 MB) |
| `yolo11s.pt` | `models/yolo11s.pt` | Pretrained YOLO11 Small PyTorch weights file (19.3 MB) |
| `yolo11n.pt` | `models/yolo11n.pt` | Pretrained YOLO11 Nano PyTorch weights file (5.61 MB) |
| `intrusion_log.csv` | `output/intrusion_log.csv` | Standard event log (`Event,Person ID,Frame,Timestamp,Risk`) |
| `secure_audit_log.csv` | `output/secure_audit_log.csv` | Cryptographically chained audit log containing `previous_hash` and `record_hash` |
| `audit_root_hash.txt` | `output/audit_root_hash.txt` | 64-character SHA-256 root digest of the entire audit chain |
| `blockchain_ledger.json` | `output/blockchain_ledger.json` | JSON structure representing Genesis and event blocks linked by SHA-256 digests |
| `day3_zone_events.csv` | `output/day3_zone_events.csv` | Zone transition log recording `INITIAL_INSIDE`, `ENTER`, and `EXIT` events |
| `day3_id_switch_results.csv` | `output/day3_id_switch_results.csv` | Tracking ID stability evaluation log recording ID switches, frame gaps, and spatial distances |
| `day3_id_consistency.csv` | `output/day3_id_consistency.csv` | Track consistency IoU evaluation log across re-identification frames |
| `config.toml` | `streamlit_app/.streamlit/config.toml` | Streamlit dark navy theme color scheme definitions |

---

### 3. Feature-to-Code Map

| Feature | Primary File | Primary Function / Symbol | Input Data | Output / Effect |
| :--- | :--- | :--- | :--- | :--- |
| **Video Ingestion** | `src/main.py` | `cv2.VideoCapture` | Video file path | Raw video frames |
| **Person Detection** | `src/main.py` | `model.track(..., classes=[0])` | Frame array | Bounding boxes & confidence |
| **Object Tracking** | `bytetrack_day3.yaml` | ByteTrack engine | Detections + history | Track IDs |
| **MongoDB Sync** | `src/app.py` | `save_events_to_mongodb()` | List of `IntrusionEvent` | Upserted Mongo documents |
| **MongoDB Fetch** | `src/app.py` | `_try_mongodb()` | Mongo collection | Parsed event objects |
| **CSV Fallback** | `src/app.py` | `_try_csv()` | `intrusion_log.csv` | Parsed event objects |
| **Audit Verification** | `src/app.py` | `verify_secure_audit_log()` | `secure_audit_log.csv`, `audit_root_hash.txt` | Integrity boolean + message |
| **Blockchain Generator** | `src/app.py` | `create_blockchain_ledger()` | `secure_audit_log.csv` | Writes `blockchain_ledger.json` |
| **Blockchain Verification**| `src/app.py` | `verify_blockchain_ledger()` | `blockchain_ledger.json` | Integrity boolean + block count |
| **Evidence Fetcher** | `src/app.py` | `fetch_image_bytes()` | File path or HTTP URL | Binary Image bytes |
| **UI Metric Cards** | `streamlit_app/components/ui_components.py` | `metric_card_html()` | Label, Value, Icon | Formatted HTML string |
