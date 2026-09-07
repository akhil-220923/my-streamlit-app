# IBVAP — Streamlit Dashboard & UI Specifications
## 10. Dashboard Layout, Navigation & Page Breakdown

---

### 1. Web Application Architecture

The IBVAP dashboard is built using Streamlit with custom CSS glassmorphism, responsive grid layouts, SVG icons, and Plotly interactive charts.

- **Theme Configuration:** Custom Dark Navy Theme defined in `streamlit_app/.streamlit/config.toml` (Primary background `#060b14`, Card background `#0e1726`, Accent cyan `#00f5d4`).
- **Typography:** `Plus Jakarta Sans` Google Font loaded via CSS `@import`.
- **Navigation Options:**
  1. **Single-File App:** `src/app.py` (Full feature implementation in 1605 lines).
  2. **Modularized App:** `streamlit_app/app.py` + `streamlit_app/pages/` modules.

---

### 2. Detailed Page-by-Page Feature Matrix

```
                          ┌──────────────────────────┐
                          │    IBVAP MAIN APP        │
                          └────────────┬─────────────┘
                                       │
      ┌────────────────┬───────────────┼───────────────┬────────────────┐
      ▼                ▼               ▼               ▼                ▼
Command Center    Surveillance  Security Events Digital Evidence   Audit Log & System
```

#### Page 1: Command Center
- **Purpose:** Executive high-level operational surveillance dashboard.
- **Components:**
  - **4 Top KPI Cards:** Total Intrusion Events (`3`), Unique Person Tracks (`3`), Threat Level (`HIGH`), Digital Evidence Items Captured (`3`).
  - **Threat Status Card:** High-risk breach alert card with glowing red border and threat description.
  - **System Health Grid:** Real-time online indicators for AI Engine, Tracking Engine, Zone Monitor, Event Logger, Evidence Capture, and Audit System.
  - **AI Security Pipeline Component:** Step-by-step visual vector flowchart mapping processing from raw camera feed to audit logging.
  - **Interactive Plotly Charts:** Risk Level Bar Chart (HIGH/MEDIUM/LOW distribution) + Event Frame Scatter Plot.
  - **Recent Events Table:** Preview list of latest breach entries.

#### Page 2: Surveillance
- **Purpose:** Video monitoring, zone visualizer, and event timeline inspector.
- **Components:**
  - **Processed Video Stream Player:** Embeds and plays `output/final_intrusion_video.mp4`.
  - **Restricted Zone Visualizer:** Interactive SVG canvas overlay rendering the polygon restricted border area and active target markers (e.g. `T:2`, `T:7`, `T:36`).
  - **Interactive Event Timeline:** Button list of timestamped events. Clicking an event selects it for deep inspection.
  - **Selected Event Inspector:** Detailed sidebar card listing Event ID, Track ID, Frame, Timestamp, and direct link to evidence.

#### Page 3: Security Events
- **Purpose:** Master data management table for security incidents.
- **Components:**
  - **Filter Controls:** Free text search box (matches Event ID, Track, Timestamp), Risk Dropdown (`ALL`, `HIGH`, `MEDIUM`, `LOW`), Status Dropdown (`Confirmed`, `Pending`, `Resolved`), and Sorting Dropdown (`Frame`, `Timestamp`, `Risk`).
  - **Data Table:** Custom styled table rendering all recorded security breach rows.
  - **Event Summary Modal:** Interactive pop-up card displaying complete event metadata, evidence status, and JSON download capability.

#### Page 4: Digital Evidence
- **Purpose:** Visual evidence gallery and snapshot inspection.
- **Components:**
  - **Evidence Grid:** Responsive 2-column image card layout displaying snapshot images alongside track metadata.
  - **Action Toolbar:** Zoom button, direct JPEG image download button, and jump-to-event button.
  - **High-Resolution Modal Viewer:** Full-width image expansion for forensic analysis.

#### Page 5: Audit Log
- **Purpose:** Cryptographic audit trail and integrity verification hub.
- **Components:**
  - **Structured Log Table:** Complete history table with exact timestamps, frame indices, and creation metadata.
  - **One-Click CSV Export:** Downloads `ibvap_security_audit_log.csv`.
  - **Live Cryptographic Verification Panel:** Executes `verify_secure_audit_log()` and displays root hash, verification status, and chain validation.
  - **Blockchain Ledger Status:** Displays `blockchain_ledger.json` block count and SHA-256 block-chain status.
  - **Cybersecurity Architecture Comparison:** Deployed CSV/SHA-256 architecture vs Future Enterprise Blockchain Roadmap.

#### Page 6: System
- **Purpose:** System architecture specs, module inventory, and environment health.
- **Components:**
  - **Module Status Cards:** Specifications for YOLO11, ByteTrack, OpenCV, Polygon Zone, Risk Engine, CSV Logger, and Streamlit.
  - **End-to-End Pipeline View:** Complete processing flowchart.
  - **Architecture Specs:** Technical comparison of core pipeline vs enterprise multi-camera deployment roadmap.
