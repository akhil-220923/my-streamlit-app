# IBVAP — Database Architecture & MongoDB Atlas Integration
## 06. Multi-Tier Persistence & Document Schema

---

### 1. MongoDB Configuration & Connection Specs

- **Database System:** MongoDB Atlas (Cloud NoSQL DB)
- **Database Name:** `IBVAP` (Configured in `src/app.py` Line 98)
- **Collection Name:** `intrusion_events` (Configured in `src/app.py` Line 99)
- **Driver / Library:** PyMongo (`pymongo.MongoClient`) + `certifi` (TLS CA Certificate verification)
- **Connection Mechanism:** Reads URI dynamically from environment variables (`MONGODB_URI`, `MONGO_URI`, `MONGO_URL`) or Streamlit secrets (`st.secrets["MONGODB_URI"]`).
- **Timeout Configuration:** `serverSelectionTimeoutMS=10000` (10 seconds)
- **API Version:** `ServerApi(version="1")`

---

### 2. Standard MongoDB Document Schema

Below is an exact example MongoDB document produced by `save_events_to_mongodb()` in `src/app.py`:

```json
{
  "_id": {
    "$oid": "66dba12f8a4f9b2c3d4e5f60"
  },
  "event_id": "EVT-001",
  "event_type": "Zone Entry",
  "person_track_id": 2,
  "frame": 30,
  "timestamp": "00:01.20",
  "risk": "HIGH",
  "evidence_file": "https://images.pexels.com/photos/13530045/pexels-photo-13530045.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
  "status": "Confirmed",
  "detection_method": "Restricted Zone Entry",
  "created_at": "2026-09-06T10:33:44.368118"
}
```

---

### 3. Field Descriptions

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `event_id` | String | Primary business key (e.g. `"EVT-001"`). Used for upsert queries. |
| `event_type` | String | Type of security event (e.g. `"Zone Entry"`). |
| `person_track_id` | Integer | ByteTrack numeric session identifier (e.g. `2`). |
| `frame` | Integer | Video frame number where breach was confirmed (e.g. `30`). |
| `timestamp` | String | Video timestamp string in `MM:SS.ms` format (e.g. `"00:01.20"`). |
| `risk` | String | Threat level classification (`"HIGH"`, `"MEDIUM"`, `"LOW"`). |
| `evidence_file` | String / Null | File path or HTTPS URL of captured snapshot. |
| `status` | String | Operational status (`"Confirmed"`, `"Pending"`, `"Resolved"`). |
| `detection_method` | String | Detection trigger rule (`"Restricted Zone Entry"`). |
| `created_at` | String (ISO 8601) | System generation timestamp. |

---

### 4. Multi-Tier Fallback Strategy & Resilience

To guarantee 100% uptime during SIH demonstrations or cloud deployments where MongoDB Atlas may be unreachable due to network restrictions, IBVAP implements an automatic 3-tier fallback loader in `src/app.py` (`fetch_events()`):

```
                       fetch_events()
                             │
                             ▼
                  Try MongoDB Atlas (_try_mongodb)
                             │
                  ┌──────────┴──────────┐
               Success                Fail / Offline / Empty
                  │                     │
                  ▼                     ▼
            Return DB Data      Try Local CSV (_try_csv)
                                        │
                             ┌──────────┴──────────┐
                          Success                Fail / File Missing
                             │                     │
                             ▼                     ▼
                       Return CSV Data     Use Seed Data (_seed_events)
```

1. **Tier 1 (Cloud DB):** `_try_mongodb()` attempts to ping MongoDB Atlas. If successful, loads live documents sorted by `event_id`.
2. **Tier 2 (Local CSV):** `_try_csv()` parses `output/intrusion_log.csv` if MongoDB is down or unconfigured. Automatically syncs local CSV data up to MongoDB when connection restores.
3. **Tier 3 (Seed Data):** `_seed_events()` returns hardcoded fallback prototype events if both MongoDB and local CSV are missing.

---

### 5. Why MongoDB instead of SQL/CSV?

1. **Schemaless Flexibility:** Border surveillance sensors and multi-camera models frequently add metadata (e.g., thermal signatures, GPS coordinates, camera IDs, drone identifiers). MongoDB handles JSON field additions without database migration scripts.
2. **High Write Throughput:** Document databases handle bursts of parallel edge events from multiple camera streams cleanly.
3. **JSON Native Integration:** Direct 1-to-1 mapping with web API endpoints, Streamlit session state, and JSON audit ledgers.
