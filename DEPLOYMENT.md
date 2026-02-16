# GIMAT Deployment Guide

## 🚀 Vercel & GitHub Deploy

---

## Muhim Ogohlantirish ⚠️

**GIMAT loyihasi og'ir ML kutubxonalariga ega** (PyTorch ~500MB, GNN models), shuning uchun:

### ✅ Tavsiya: Hybrid Deployment

1. **Frontend** → Vercel (static)
2. **Light APIs** → Vercel (serverless)
3. **Heavy ML** → Railway.app yoki Render.com (Docker)

Yoki to'liq **Railway.app/Render.com** ishlatish tavsiya etiladi.

---

## Opsiya 1: Vercel (Frontend + Light APIs)

### 1️⃣ GitHub'ga Yuklash

```bash
cd C:\Users\Asus\Gimat

# Git initialize (agar bo'lmasa)
git init

# Remote qo'shish
git remote add origin https://github.com/Venetsiyali/gimat.git

# Barcha fayllarni qo'shish
git add .

# Commit
git commit -m "feat: Initial GIMAT deployment setup"

# Push
git branch -M main
git push -u origin main
```

### 2️⃣ Vercel CLI Setup

```bash
# Vercel CLI o'rnatish
npm install -g vercel

# Login
vercel login

# Deploy
cd C:\Users\Asus\Gimat
vercel

# Production deploy
vercel --prod
```

### 3️⃣ Environment Variables (Vercel Dashboard)

Vercel.com → Project → Settings → Environment Variables:

```
NEO4J_URI=neo4j+s://xxxxx.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
TIMESCALE_URL=postgres://user:pass@host/db
OPENAI_API_KEY=sk-xxxxx
REDIS_URL=redis://...
```

### 4️⃣ GitHub Actions Secrets

GitHub → Repo → Settings → Secrets and variables → Actions:

```
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=team_xxxxx
VERCEL_PROJECT_ID=prj_xxxxx
```

**Vercel token olish**: Vercel.com → Settings → Tokens

---

## Opsiya 2: Railway.app (Tavsiya - To'liq Deploy)

### Afzalliklari

- ✅ Docker support (har qanday kutubxona)
- ✅ PostgreSQL, Redis bepul
- ✅ Og'ir ML modellarga mos
- ✅ $5/month (hobby tier)

### Deploy

```bash
# Railway CLI o'rnatish
npm install -g @railway/cli

# Login
railway login

# Initialize
cd C:\Users\Asus\Gimat
railway init

# Deploy
railway up

# Database qo'shish
railway add postgres
railway add redis
```

### Docker Setup

`Dockerfile` loyiha ildizida:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/

# Copy frontend build
COPY frontend/build ./frontend/build

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Opsiya 3: Render.com

### Deploy Steps

1. Render.com → New → Web Service
2. Connect GitHub repository
3. Build Command: `pip install -r backend/requirements.txt`
4. Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables qo'shish

---

## Frontend Build (Vercel uchun)

```bash
cd frontend

# Install
npm install

# Build
npm run build

# Test locally
npm install -g serve
serve -s build
```

---

## GitHub Repository Structure

```
gimat/
├── .github/
│   └── workflows/
│       └── deploy.yml        # Auto-deploy
├── api/
│   ├── index.py              # Vercel entry
│   ├── routes/
│   │   └── simple_data.py
│   └── requirements.txt      # Lightweight
├── backend/                  # Full backend (Railway/Render)
│   ├── main.py
│   ├── models/
│   ├── rag/
│   └── requirements.txt      # Full dependencies
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── vercel.json               # Vercel config
├── .vercelignore
├── .gitignore
├── docker-compose.yml        # Local development
├── Dockerfile                # Railway/Render
└── README.md
```

---

## Git Commands Reference

### Clone (boshqa kompyuterda)

```bash
git clone https://github.com/Venetsiyali/gimat.git
cd gimat
```

### Pull latest changes

```bash
git pull origin main
```

### Make changes and push

```bash
git add .
git commit -m "your message"
git push origin main
```

### Create branch

```bash
git checkout -b feature/new-feature
git push -u origin feature/new-feature
```

---

## Troubleshooting

### Vercel 250MB Limit Error

**Yechim**: Og'ir kutubxonalarni olib tashlash yoki Railway'ga o'tish

```bash
# Check size
pip list --format=freeze | grep torch
# torch==2.1.0  # ~500MB ❌

# Alternative: ONNX Runtime
pip install onnxruntime  # ~50MB ✅
```

### Cold Start Slow

**Yechim**: Model caching yoki warm-up endpoint

```python
# api/index.py
import time

@app.on_event("startup")
async def warmup():
    # Pre-load models
    pass
```

### Database Connection Error

**Yechim**: Check environment variables

```bash
# Vercel CLI
vercel env ls
vercel env add NEO4J_URI
```

---

## Next Steps

1. **GitHub'ga push qiling**
2. **Railway.app yoki Vercel tanlang**
3. **Environment variables sozlang**
4. **Test qiling**: `https://your-project.vercel.app` yoki `https://your-project.up.railway.app`
5. **Custom domain** qo'shing (optional)

---

## Recommended: Railway.app

GIMAT uchun **Railway.app to'liq tavsiya etiladi** chunki:

- PostgreSQL va Neo4j container'da oson
- PyTorch va og'ir ML model'lar ishlaydi
- Docker Compose qo'llab-quvvatlaydi
- Cost-effective ($5-10/month)

**Deploy**: `railway up` — HAMMASI TAYYOR! 🚀
