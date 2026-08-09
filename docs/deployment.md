# Deployment Guide

## Primary: Hugging Face Spaces (Recommended)

**Why:** 2 CPU, 16GB RAM, 50GB disk free, no sleep, native Streamlit support, free.

**Steps:**
1. Create HF account at https://huggingface.co
2. Create new Space: https://huggingface.co/new-space
   - Space name: insightforge
   - SDK: Streamlit
   - Hardware: CPU basic (free)
3. Clone Space repo locally:
   ```
   git clone https://huggingface.co/spaces/<username>/insightforge
   cd insightforge
   ```
4. Copy project files (streamlit_app.py, app/, src/, sample_data/, requirements.txt, .gitignore)
5. Create `packages.txt` if needed (empty)
6. Commit + push:
   ```
   git add .
   git commit -m "Initial InsightForge deployment"
   git push
   ```
7. Space auto-builds — check logs in Space UI
8. Add secrets if using LLM: Space Settings → Variables → OPENAI_API_KEY

**Entry file:** `streamlit_app.py` at root must exist. It should run `streamlit run streamlit_app.py --server.port 7860 --server.address 0.0.0.0`

**Troubleshooting:**
- Build fails: check requirements.txt versions, remove kaleido if fails (optional for PNG)
- Memory: HF free is 16GB, sufficient for 200MB CSV
- Sleep: Spaces does not sleep (vs Streamlit Cloud 7 days)

## Secondary: Streamlit Community Cloud

**Why:** Easiest, GitHub integration, but 1GB RAM and sleeps after 7 days.

**Steps:**
1. Push code to GitHub public repo
2. Go to https://share.streamlit.io
3. New app → Select repo, branch main, file `streamlit_app.py`
4. Advanced settings → Add secrets if needed
5. Deploy — cold start ~30s

**Limitations:** 1GB RAM — may OOM on large files. Add note in UI: "For files >100MB, use sampling".

## Tertiary: Render / Docker

**Dockerfile included.**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

**Render steps:**
1. Connect GitHub repo on Render
2. Create new Web Service → Docker or Python
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run streamlit_app.py --server.port 10000 --server.address 0.0.0.0`
5. Env var PORT=10000

## Local Development

```
git clone <repo>
cd insightforge
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Environment Variables

See `.env.example` — optional OPENAI_API_KEY, GROQ_API_KEY.

## Secrets Management

- Local: `.env` file (gitignored)
- HF Spaces: Settings → Variables
- Streamlit Cloud: App Settings → Secrets (TOML)

Never hardcode keys.
