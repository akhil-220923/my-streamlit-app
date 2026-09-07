# IBVAP — Live SIH 3-Minute Demo Script & Click Flow
## 16. Step-by-Step Interactive Demo Walkthrough

---

### Timing & Navigation Schedule

| Time | Target UI Screen | Actions to Perform | What to Say |
| :---: | :--- | :--- | :--- |
| **0:00 - 0:30** | Slide Deck / Introduction | Stand in front of judges, display title slide. | *"Respected judges, traditional border CCTV systems require manual monitoring and store insecure logs. We present IBVAP—Intelligent Border Video Analytics Platform—a system combining AI vision with cryptographic audit protection."* |
| **0:30 - 1:00** | **Command Center** (`app.py`) | Open IBVAP web app in browser. Point out the top 4 KPI cards and system health indicators. | *"Here is our live Command Center. At a glance, commanders see real-time KPIs: 3 intrusion events detected, 3 unique person tracks, a HIGH threat level, and 3 digital evidence snapshots captured. All system modules are online."* |
| **1:00 - 1:30** | **Surveillance** Page | Click **Surveillance** in sidebar. Play `final_intrusion_video.mp4`. Point to the restricted zone vector diagram. | *"Under Surveillance, we process live camera feed CAM-01. Notice our YOLO11 model detecting targets while ByteTrack maintains persistent Track IDs like Track 2 and Track 7. The right panel shows our polygon restricted zone."* |
| **1:30 - 2:00** | **Security Events** Page | Click **Security Events**. Demonstrate searching `"EVT-001"` and filtering by Risk `HIGH`. Click **View EVT-001**. | *"In Security Events, operators can filter events by risk level or timestamp. Clicking an event opens our summary modal, showing track frame index 30, timestamp 00:01.20, and risk rating."* |
| **2:00 - 2:20** | **Digital Evidence** Page | Click **Digital Evidence**. Click **Zoom** on EVT-001 snapshot. | *"In Digital Evidence, IBVAP auto-captures snapshot images at the exact moment of zone breach. Clicking Zoom lets commanders inspect high-res visual proof for legal and forensic handoff."* |
| **2:20 - 2:45** | **Audit Log** Page | Click **Audit Log**. Highlight the green **✓ Audit Log Integrity VERIFIED** banner. Click **Export Audit Log CSV**. | *"To prevent insider log tampering, IBVAP uses SHA-256 linear hash chaining. Here you see our live cryptographic verification engine confirming all records are untampered. Operators can export this audit log with one click."* |
| **2:45 - 3:00** | **System** Page & Conclusion | Click **System**. Point to the tech stack cards and conclude presentation. | *"Our solution is fully functional, resilient, and deployed on the cloud. IBVAP turns passive cameras into active, tamper-proof border guardians. Thank you!"* |
