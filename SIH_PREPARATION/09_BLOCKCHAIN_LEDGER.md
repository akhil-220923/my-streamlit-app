# IBVAP — Blockchain Audit Ledger Specifications
## 09. Local Proof-of-Concept Ledger & Decentralization Truth

---

### 1. Zero-Hallucination Technical Truth

> **CRITICAL SIH POSITIONING:**  
> IBVAP currently implements a **Local Cryptographic Hash-Linked Audit Ledger** (`blockchain_ledger.json`).  
> It is **NOT** a distributed peer-to-peer network (such as Ethereum Mainnet or Hyperledger Fabric node cluster). It does **NOT** currently execute Solidity smart contracts or run distributed consensus protocols (Proof-of-Work / Proof-of-Stake).  
> 
> During SIH presentation, describe it accurately as:  
> *"A lightweight, single-node tamper-evident cryptographic blockchain ledger designed as a local proof-of-concept, architected for future seamless deployment onto enterprise permissioned blockchains like Hyperledger Fabric."*

---

### 2. Concrete Ledger Implementation Details

- **File Path:** `output/blockchain_ledger.json`
- **Network Name:** `"IBVAP-LOCAL-AUDIT-LEDGER"`
- **Hash Algorithm:** `"SHA-256"`
- **Block Count:** `4` Blocks (Block 0 Genesis + 3 Event Blocks)
- **Generator Functions:** `create_blockchain_ledger()` and `verify_blockchain_ledger()` in `src/app.py` (Lines 433–542)

---

### 3. Complete Block-by-Block Inventory

#### Block 0: Genesis Block
```json
{
  "block_index": 0,
  "timestamp": "2026-09-06T10:33:44.368118",
  "data": {
    "type": "GENESIS",
    "system": "IBVAP",
    "description": "IBVAP Audit Blockchain Genesis Block"
  },
  "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "block_hash": "90bbb09388f2fba85c2b8261c1367bac2c27f92531ff74f1b370782cc150b9f5"
}
```

#### Block 1: Event EVT-001
```json
{
  "block_index": 1,
  "timestamp": "2026-09-06T10:33:44.368996",
  "data": {
    "event_id": "EVT-001",
    "event_type": "Zone Entry",
    "person_track_id": 2,
    "frame": 30,
    "timestamp": "00:01.20",
    "risk": "HIGH"
  },
  "previous_hash": "90bbb09388f2fba85c2b8261c1367bac2c27f92531ff74f1b370782cc150b9f5",
  "block_hash": "f829ffa4966ed71241ba086b5ff06f7f80ccb427c5bcda50840994a67d1ce9f9"
}
```

#### Block 2: Event EVT-002
```json
{
  "block_index": 2,
  "timestamp": "2026-09-06T10:33:44.369315",
  "data": {
    "event_id": "EVT-002",
    "event_type": "Zone Entry",
    "person_track_id": 7,
    "frame": 108,
    "timestamp": "00:04.33",
    "risk": "HIGH"
  },
  "previous_hash": "f829ffa4966ed71241ba086b5ff06f7f80ccb427c5bcda50840994a67d1ce9f9",
  "block_hash": "01323a8ff99690282c81ea51f17c95aaa47933e108d622bc4008df086d063232"
}
```

#### Block 3: Event EVT-003
```json
{
  "block_index": 3,
  "timestamp": "2026-09-06T10:33:44.373739",
  "data": {
    "event_id": "EVT-003",
    "event_type": "Zone Entry",
    "person_track_id": 36,
    "frame": 177,
    "timestamp": "00:07.10",
    "risk": "HIGH"
  },
  "previous_hash": "01323a8ff99690282c81ea51f17c95aaa47933e108d622bc4008df086d063232",
  "block_hash": "0db09a5ccb11059d8264c6ca61ec54de3523f27cc4db81e2ba76b1a36fa98139"
}
```

---

### 4. Technical Validation Algorithm

The ledger validation routine `verify_blockchain_ledger()` loads `blockchain_ledger.json` and performs block-by-block structural verification:
1. Verifies that Block 0 has `previous_hash` equal to 64 zeros (`00...00`).
2. For each block $k \ge 1$:
   - Reconstructs payload: `{"block_index": k, "data": block.data, "previous_hash": block.previous_hash}`
   - Computes expected SHA-256 hash.
   - Verifies `block["previous_hash"] == previous_block["block_hash"]`.
   - Verifies `block["block_hash"] == calculated_hash`.
3. Displays **"✓ Blockchain Audit Ledger VERIFIED"** on the UI.

---

### 5. Blockchain Feature Capability Matrix

| Feature | Implemented in IBVAP? | Description |
| :--- | :--- | :--- |
| **SHA-256 Hash Linking** | `YES` | Each block headers previous block's SHA-256 digest |
| **Genesis Block Initialization**| `YES` | Explicit Block 0 initialization |
| **Block Payload Serialization** | `YES` | Canonical JSON serialization |
| **Automated Ledger Verification**| `YES` | Dynamic verification algorithm |
| **Peer-to-Peer Node Network** | `NO (Future Scope)` | Single node local ledger |
| **Distributed Consensus Protocol**| `NO (Future Scope)`| PoW/PoS not required for single-node prototype |
| **Smart Contracts** | `NO (Future Scope)`| Chaincode / Solidity integration planned for enterprise |
