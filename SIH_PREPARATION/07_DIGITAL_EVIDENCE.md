# IBVAP — Digital Evidence Capture & Storage
## 07. Visual Evidence Management & Immutable Association

---

### 1. Evidence Snapshot Generation Workflow

When the intrusion detection engine confirms a perimeter breach at frame $N$, the video processing pipeline executes an immediate frame grab:

```
 Perimeter Breach Confirmed at Frame N (Track ID X)
                        │
                        ▼
           OpenCV Bounding Box Plotting
                        │
                        ▼
         Evidence Image Frame Extraction
                        │
                        ▼
 File Saved: output/evidence/EVT-XXX_track_X_frame_N.jpg
                        │
                        ▼
 Path Linked to Event Payload & SHA-256 Record
```

---

### 2. Evidence Naming Convention & Directory Mapping

#### Project Evidence Files (Verified from Source)

| Event ID | Track ID | Frame | File Name | Disk Path |
| :--- | :--- | :--- | :--- | :--- |
| `EVT-001` | `Track 2` | `Frame 30` | `EVT-001_track_2_frame_30.jpg` | `output/evidence/EVT-001_track_2_frame_30.jpg` |
| `EVT-002` | `Track 7` | `Frame 108` | `EVT-002_track_7_frame_108.jpg` | `output/evidence/EVT-002_track_7_frame_108.jpg` |
| `EVT-003` | `Track 36` | `Frame 177` | `EVT-003_track_36_frame_177.jpg` | `output/evidence/EVT-003_track_36_frame_177.jpg` |

#### Additional Evidence Repositories in Codebase:
- `src/output/evidence/evidence_001.jpg`, `evidence_002.jpg`, `evidence_003.jpg` (Secondary fallback repository)
- `screenshots/intrusion_001.jpg`, `intrusion_002.jpg`, `intrusion_003.jpg` (UI demonstration snapshots)

---

### 3. Streamlit Evidence Gallery & High-Res Viewer

In the Streamlit Dashboard (`streamlit_app/pages/digital_evidence.py` & `src/app.py` Lines 1009–1080):
1. **Dynamic Image Fetcher:** `fetch_image_bytes(source)` dynamically loads images from local disk paths or remote URLs with timeout and memory caching (`@st.cache_data(ttl=300)`).
2. **Interactive Cards:** Each evidence snapshot is rendered alongside Event ID, Track ID, Frame number, Timestamp, and Risk Badge.
3. **High-Resolution Zoom Viewer:** Clicking `"Zoom"` opens a modal overlay displaying the raw full-resolution evidence image for detailed security inspection.
4. **Direct Download:** Users can download evidence snapshots (`.jpg`) directly from the UI for forensic handoff.

---

### 4. Digital Evidence Integrity & Immutability

- **SHA-256 Hash Association:** The evidence filename and metadata are included in the JSON string payload that generates the SHA-256 hash record in `secure_audit_log.csv`.
- **Tamper Evidence:** If an attacker modifies or replaces an evidence image file on disk, the associated audit hash validation will fail upon root digest verification.
- **Future Immutable Evidence Scope:** Storing evidence SHA-256 hashes on an IPFS (InterPlanetary File System) decentralized network or permissioned blockchain smart contract for legal admissibility.
