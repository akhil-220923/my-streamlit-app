# IBVAP — Deployment & Production Setup
## 11. Deployment Architecture & Secret Management

---

### 1. Actual Production Deployment Pipeline

```
 Local Code Base / Google Colab
             │
             ▼
 Git Source Control (GitHub Repository)
             │
             ▼
 Streamlit Community Cloud (Public Web Host)
             │
             ▼
 Cloud Database Integration (MongoDB Atlas / Supabase)
```

---

### 2. Deployment Configurations & Files

- **Main Web Entry Point:** `src/app.py` or `streamlit_app/app.py`
- **Dependencies Specification File:** `streamlit_app/requirements.txt`
  - `streamlit>=1.38.0`
  - `pandas>=2.2.0`
  - `plotly>=5.24.0`
  - `supabase-py>=2.7.0`
  - `Pillow>=10.4.0`
  - `requests>=2.32.0`
  - `pymongo>=4.6.0` (included in single-file setup)
  - `certifi>=2024.0.0`
- **UI Theme Configuration:** `streamlit_app/.streamlit/config.toml`

---

### 3. Environment Variables & Secrets Management

To prevent hardcoding credentials in public GitHub repositories, IBVAP uses environment variable abstraction and Streamlit Secrets (`st.secrets`).

#### Configured Secret Keys
- `MONGODB_URI` / `MONGO_URI` / `MONGO_URL`
- `SUPABASE_URL` / `VITE_SUPABASE_URL`
- `SUPABASE_ANON_KEY` / `VITE_SUPABASE_ANON_KEY`

#### Access Code Snippet (`src/app.py` Lines 83–95)
```python
def get_mongo_uri():
    for key in ["MONGODB_URI", "MONGO_URI", "MONGO_URL"]:
        uri = os.environ.get(key, "").strip()
        if uri:
            return uri
    try:
        if hasattr(st, "secrets"):
            for key in ["MONGODB_URI", "MONGO_URI", "MONGO_URL"]:
                if key in st.secrets:
                    return str(st.secrets[key]).strip()
    except Exception:
        pass
    return ""
```

---

### 4. Step-by-Step Deployment Guide

#### Local / Server Execution
```bash
# 1. Clone repository
git clone https://github.com/your-org/ibvap.git
cd ibvap

# 2. Install dependencies
pip install -r streamlit_app/requirements.txt
pip install ultralytics opencv-python pymongo certifi python-dotenv

# 3. Set environment variables (or create .env file)
export MONGODB_URI="your_mongodb_connection_string"

# 4. Launch Streamlit dashboard
streamlit run src/app.py
```

#### Streamlit Community Cloud Deployment
1. Push codebase to GitHub.
2. Log into [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Select repository and branch.
4. Set Main file path to `src/app.py` or `streamlit_app/app.py`.
5. Under **Advanced Settings $\rightarrow$ Secrets**, paste secrets:
   ```toml
   MONGODB_URI = "mongodb+srv://..."
   SUPABASE_URL = "https://..."
   SUPABASE_ANON_KEY = "ey..."
   ```
6. Click **Deploy**. Public URL is generated automatically.
