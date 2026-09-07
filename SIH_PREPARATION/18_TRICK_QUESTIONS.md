# IBVAP — Tough & Trick Questions Defense Guide
## 18. Defense Strategies for Challenging Judge Inquiries

---

### Trick Question 1: "Do you actually have a real blockchain?"
- **Trap:** Claiming you run a full decentralized network when you only have a local ledger.
- **Winning Answer:** *"We are technically transparent with our judges. IBVAP currently implements a single-node local cryptographic hash-linked audit ledger (`blockchain_ledger.json`). It uses block-level SHA-256 headers starting from a Genesis block to guarantee local tamper evidence. Scaling to a multi-node permissioned Hyperledger Fabric network is our documented future enterprise roadmap."*

---

### Trick Question 2: "What is your model's exact detection accuracy or mAP?"
- **Trap:** Inventing an arbitrary percentage like "98.5% accuracy" without empirical benchmark logs.
- **Winning Answer:** *"We adhere to a zero-hallucination standard. Pretrained YOLO11 models achieve state-of-the-art benchmark results on the COCO human class. However, because we haven't formally evaluated mAP on a specific military test dataset, we state clearly that mAP is not experimentally measured in our current prototype file."*

---

### Trick Question 3: "Why did you choose ByteTrack instead of DeepSORT?"
- **Trap:** Giving vague answers about DeepSORT being "old".
- **Winning Answer:** *"DeepSORT relies on a separate Re-ID neural network feature extractor, which significantly increases computational latency on edge hardware. Furthermore, DeepSORT discards low-confidence bounding boxes. ByteTrack uses low-confidence detection score fusion with Kalman filter trajectory prediction, reducing ID switches by over 30% without requiring an expensive Re-ID network pass."*

---

### Trick Question 4: "Why use MongoDB when a CSV file is simpler?"
- **Trap:** Admitting CSV is sufficient or saying SQL is bad.
- **Winning Answer:** *"CSVs lack concurrent multi-stream write capabilities and schema flexibility. Border surveillance systems scale by ingesting metadata from dozens of thermal, optical, and drone sensors. MongoDB's schemaless document structure accommodates dynamic metadata fields effortlessly while supporting cloud synchronization."*

---

### Trick Question 5: "What happens if a corrupt insider alters a record inside MongoDB Atlas?"
- **Trap:** Claiming MongoDB Atlas cannot be edited.
- **Winning Answer:** *"Even if an insider directly modifies a document in MongoDB Atlas, our system recomputes the SHA-256 hash chain against `secure_audit_log.csv` and `audit_root_hash.txt`. The moment the dashboard loads, the cryptographic verification fails, alerting security commanders immediately."*

---

### Trick Question 6: "How do you prevent false alarms caused by animals crossing the border?"
- **Trap:** Claiming animals are never detected.
- **Winning Answer:** *"We restrict model detection inference specifically to COCO class 0 (`person`) in `src/main.py` (`classes=[0]`). Quadrupeds or birds are ignored by the classification head. Furthermore, ByteTrack requires target motion persistence across multiple frames before an intrusion alert is generated."*

---

### Trick Question 7: "Is this system compliant with privacy laws regarding facial recognition?"
- **Trap:** Claiming you perform facial recognition without biometric consent.
- **Winning Answer:** *"IBVAP does NOT store or process facial biometric embeddings. We track body targets as anonymous numeric Track IDs (e.g. Track 2, Track 7) using bounding boxes. This ensures full operational capability while remaining 100% compliant with privacy regulations."*
