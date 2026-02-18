# 🚀 GIMAT - Hydrological Intelligence System

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/gimat)

**Gidrologik Intellektual Monitoring va Axborot Tizimi** - Advanced hydrological monitoring with AI/ML for Uzbekistan's river basins.

---

## 🎯 Features

- 🌊 **Real-time Monitoring** - Discharge, water level, temperature tracking
- 🧠 **Hybrid ML Models** - SARIMA + Bi-LSTM + Transformer + GNN ensemble
- 📊 **Physics-Informed NN** - PINN with mass balance constraints
- 📄 **RAG System** - Document-based Q&A with ChromaDB
- 🎛️ **What-if DSS** - Scenario simulation for reservoir operations
- 🌍 **Cross-border Data** - Integration with Tajikistan, Kyrgyzstan
- ✅ **Data Quality** - Multi-source confidence scoring & anomaly detection
- ⚡ **Edge Computing** - Real-time processing on edge devices

---

## 🚀 Quick Deploy to Railway

### 1️⃣ Deploy Button (Easiest)

Click the button above or:

```bash
railway init --template https://github.com/Venetsiyali/gimat
```

### 2️⃣ From GitHub Repo

1. Go to [Railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `Venetsiyali/gimat`
4. Railway automatically detects `Dockerfile` ✓

### 3️⃣ CLI Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Clone and deploy
git clone https://github.com/Venetsiyali/gimat.git
cd gimat
railway init
railway up
```

---

## 📦 Railway Services Setup

### Required Services

| Service | Type | Purpose |
|---------|------|---------|
| **Backend** | Dockerfile | FastAPI application |
| **PostgreSQL** | Plugin | TimescaleDB (time-series data) |
| **Redis** | Plugin | Caching & message queue |
| **Neo4j** | Docker | Graph database (river network) |

### Add Services

```bash
# PostgreSQL (auto-provides DATABASE_URL)
railway add postgres

# Redis (auto-provides REDIS_URL)
railway add redis

# Neo4j (custom Docker image)
railway add
# Then: Docker Image → neo4j:5.15-community
```

---

## ⚙️ Environment Variables

### Auto-Provided by Railway

| Variable | Service | Auto-Set |
|----------|---------|----------|
| `DATABASE_URL` | PostgreSQL | ✅ |
| `REDIS_URL` | Redis | ✅ |
| `PORT` | Backend | ✅ |

### Required Manual Setup

Railway Dashboard → Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `NEO4J_URI` | `bolt://neo4j.railway.internal:7687` | Neo4j connection |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `your_secure_password` | Neo4j password |
| `OPENAI_API_KEY` | `sk-xxxxx` | OpenAI API for RAG |
| `ENVIRONMENT` | `production` | App environment |
| `LOG_LEVEL` | `info` | Logging level |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_ORIGINS` | `*` | CORS origins |
| `SECRET_KEY` | auto-generated | JWT secret |
| `ML_MODEL_PATH` | `/app/models` | Model storage path |

---

## 🗺️ Google Maps Configuration

To remove the "For development purposes only" watermark:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project and go to **Billing**
3. Link a billing account (required even for free tier)
4. Go to **APIs & Services** → **Credentials**
5. Edit your API Key (`AIzaSy...`)
6. Under **Application restrictions**, add your domains:
   - `https://your-project.vercel.app`
   - `http://localhost:3000`
7. Under **API restrictions**, enable **Maps JavaScript API** and **Places API**

---

## 🗄️ Database Initialization & Seeding

After deployment, databases auto-initialize via `backend/database/init_railway.py`:

**TimescaleDB**:
- ✅ Hypertables for `observations` and `predictions`
- ✅ Compression (7-day policy)
- ✅ Indexes for fast queries

**Neo4j**:
- ✅ Constraints (unique station IDs)
- ✅ Indexes (station/river names)
- ✅ Sample Chirchiq basin data

**Manual initialization** (if needed):
**Manual initialization** (if needed):
```bash
railway run python backend/database/init_railway.py
```

### 🌱 Seeding Real Data (Uzbekistan)
To populate the database with real stations (Chorvoq, G'azalkent, etc.) and generate 30 days of mock data:

```bash
# Local
cd backend
python scripts/seed_data.py

# Railway
railway run python backend/scripts/seed_data.py
```
This script acts on both **PostgreSQL** (Observations) and **Neo4j** (Knowledge Graph).

---

## 💰 Cost Optimization

### Free Tier Strategy
- ✅ $5 free credit
- ✅ 500 hours/month
- ⚠️ Services sleep after 30min inactivity

### Resource Limits (in `railway.json`)

```json
{
  "resources": {
    "memory": "2GB",    // Sufficient for GIMAT
    "cpu": "1"          // Single CPU core
  }
}
```

### Cost-Saving Tips

1. **Use 1 Worker** - `--workers 1` in uvicorn
2. **Enable Sleep** - Railway auto-sleeps inactive services
3. **Compression** - TimescaleDB data compression enabled
4. **Lazy Loading** - ML models load on-demand
5. **Minimal Data** - Keep only essential time-series

### Estimated Monthly Cost

| Plan | Services | Cost |
|------|----------|------|
| **Free** | All (with sleep) | $0 (using $5 credit) |
| **Hobby** | Backend + 3 DBs | $15-20/mo |
| **Pro** | High availability | $50+/mo |

**GIMAT Recommendation**: Hobby tier ($5/mo base) → ~$15-20/mo total

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Railway Platform              │
│                                         │
│  ┌──────────┐  ┌──────────────────┐    │
│  │ Backend  │──│ PostgreSQL       │    │
│  │ (Docker) │  │ (TimescaleDB)    │    │
│  │          │  └──────────────────┘    │
│  │  Port:   │                          │
│  │  $PORT   │  ┌──────────────────┐    │
│  │          │──│ Neo4j (Docker)   │    │
│  │          │  │ bolt://7687      │    │
│  │          │  └──────────────────┘    │
│  │          │                          │
│  │          │  ┌──────────────────┐    │
│  │          │──│ Redis (Plugin)   │    │
│  └──────────┘  └──────────────────┘    │
│                                         │
│  Internal: *.railway.internal           │
└─────────────────────────────────────────┘
         │
         │ HTTPS (Auto SSL)
         ▼
    Internet
```

---

## 📡 API Endpoints

Once deployed, access via `https://your-project.up.railway.app`:

### Core APIs
- `GET /health` - Health check
- `GET /api/data/stations` - List monitoring stations
- `GET /api/data/stations/{id}/latest` - Latest observation
- `POST /api/predictions/forecast` - Generate forecast

### Advanced Features
- `POST /api/rag/query` - RAG document Q&A
- `POST /api/dss/simulate` - Scenario simulation
- `POST /api/quality/confidence` - Data confidence score
- `GET /api/ontology/network` - River network topology

**Swagger Docs**: `https://your-project.up.railway.app/docs`

---

## 🧪 Testing

### Local Development

```bash
# Docker Compose
docker-compose up

# Access
Backend: http://localhost:8000
Neo4j: http://localhost:7474
```

### Railway Testing

```bash
# View logs
railway logs

# Connect to database
railway run psql

# Run commands
railway run python backend/database/init_railway.py
```

---

## 📊 Scientific Background

**PhD Thesis (05.01.10 - Hydraulic Engineering)**:
- Hybrid ML ensemble (SARIMA + LSTM + Transformer + GNN)
- Physics-informed constraints (mass balance, continuity)
- Knowledge graph for river basin ontology
- RAG for normative document integration
- Multi-source data quality assessment

**Basins**: Chirchiq, Zarafshon (Uzbekistan)

---

## 🔧 Troubleshooting

### Build Fails
```bash
# Check logs
railway logs --deployment

# Rebuild
railway up --detach
```

### Database Connection Error
```bash
# Verify variables
railway variables

# Check service status
railway status
```

### Out of Memory
- Railway Dashboard → Settings → Increase memory
- Or optimize: lazy loading, reduce workers

---

## 📝 Development

### Local Setup

```bash
# Clone
git clone https://github.com/Venetsiyali/gimat.git
cd gimat

# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Frontend
cd frontend
npm install
npm start
```

### Project Structure

```
gimat/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── api/                 # API endpoints
│   ├── models/              # ML models
│   ├── rag/                 # RAG module
│   ├── quality/             # Data quality
│   ├── dss/                 # Decision support
│   └── database/            # DB managers
├── frontend/                # React app
├── Dockerfile               # Production build
├── docker-compose.yml       # Local dev
└── railway.json             # Railway config
```

---

## 📚 Documentation

- [Deployment Plan](./DEPLOYMENT.md)
- [Enhancement Plan](./docs/enhancement_plan.md)
- [API Documentation](https://your-project.up.railway.app/docs)

---

## 🤝 Contributing

For research collaboration or contributions, open an issue or PR.

---

## 📄 License

Research project - Tashkent Institute of Irrigation and Agricultural Mechanization Engineers (TIIAME)

---

## 🎓 Citation

```bibtex
@phdthesis{gimat2024,
  title={Hybrid Machine Learning Approach for River Discharge Forecasting with Physics-Informed Constraints},
  author={[Your Name]},
  year={2024},
  school={TIIAME},
  type={PhD Thesis (05.01.10)}
}
```

---

**Deploy Time**: ~5 minutes ⚡  
**Auto-Scaling**: ✅  
**SSL Certificate**: Auto (Let's Encrypt) ✅

**Start monitoring Uzbekistan's rivers with AI!** 🌊🤖
