# IBVAP — Future Scope & System Enhancement Roadmap
## 20. Strategic Enhancements Without Breaking Current Code

---

### 1. Future Technical Enhancements (Top 10 Additions)

#### 1. Multi-Camera RTSP Stream Ingestion
- **Description:** Upgrade single-stream file reading (`video.mp4`) to multi-threaded RTSP IP camera feed ingestion using GStreamer / OpenCV async workers.
- **Impact:** Scales coverage to dozens of simultaneous border camera channels.

#### 2. Interactive Restricted Zone Canvas UI
- **Description:** Add a Streamlit dynamic canvas component allowing operators to draw, edit, and save polygon zones directly on top of live video feeds.
- **Impact:** Eliminates manual polygon coordinate configuration in code files.

#### 3. Thermal / Infrared (FLIR) Model Fine-Tuning
- **Description:** Fine-tune YOLO11 weights on public thermal IR datasets (e.g. FLIR, OTCBVS).
- **Impact:** Enhances night surveillance and bad-weather target identification accuracy.

#### 4. Permissioned Hyperledger Fabric Blockchain Integration
- **Description:** Replace single-node `blockchain_ledger.json` with a multi-node Hyperledger Fabric network running Raft consensus and chaincode smart contracts.
- **Impact:** Delivers decentralized multi-agency (e.g. BSF, Army, Intelligence) tamper-proof audit consensus.

#### 5. IPFS (InterPlanetary File System) Evidence Storage
- **Description:** Store captured evidence JPEG snapshots on IPFS and write content multi-hashes (CIDs) to the audit log.
- **Impact:** Guarantees decentralized, unalterable visual evidence preservation.

#### 6. Real-Time SMS / WhatsApp / Telegram Emergency Alerts
- **Description:** Integrate Twilio / Telegram Bot API to broadcast high-risk breach notifications (`HIGH`) directly to patrol officers' mobile phones within 1 second of breach.
- **Impact:** Drastically reduces tactical response latency.

#### 7. TensorRT Model Acceleration on NVIDIA Jetson Edge Nodes
- **Description:** Export YOLO11 PyTorch model weights to NVIDIA TensorRT (`.engine` format) for edge deployment on Jetson Orin Nano hardware.
- **Impact:** Increases inference frame rates to 60+ FPS at low wattage.

#### 8. Drone / PTZ Camera Auto-Tracking Handshake
- **Description:** Send pan-tilt-zoom (PTZ) optical movement vectors or drone flight commands toward detected breach coordinates $(x, y)$.
- **Impact:** Automates active target tracking beyond static camera fields of view.

#### 9. AI Anomaly & Loitering Behavior Analysis
- **Description:** Add temporal sequence modeling (LSTM / Transformer) on target trajectories to detect suspicious loitering or crawling behaviors prior to zone entry.
- **Impact:** Provides predictive threat warnings before an intrusion occurs.

#### 10. Role-Based Access Control (RBAC) & OAuth2 Authentication
- **Description:** Implement JWT/OAuth2 login with granular roles (`Operator`, `Commander`, `Auditor`).
- **Impact:** Enforces strict operational security governance across dashboard actions.
