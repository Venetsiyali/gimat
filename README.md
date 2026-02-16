# 🚀 GIMAT - Railway.app Docker Deployment

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

---

## Tez Boshlash (Quick Start)

### 1️⃣ GitHub'ga Yuklash

```bash
cd C:\Users\Asus\Gimat

# Git setup (agar qilinmagan bo'lsa)
git add .
git commit -m "feat: Railway Docker deployment ready"
git push origin main
```

### 2️⃣ Railway'da Deploy

#### Web Interface orqali:

1. [Railway.app](https://railway.app) ga kirish
2. **"New Project"** → **"Deploy from GitHub repo"**
3. `Venetsiyali/gimat` repozitoriyasini tanlash
4. Dockerfile avtomatik topiladi ✓

#### CLI orqali:

```bash
# Railway CLI o'rnatish
npm install -g @railway/cli

# Login
railway login

# Initialize va deploy
railway init
railway up
```

### 3️⃣ Database Sozlash

Railway Dashboard → Add Service:

**PostgreSQL** (TimescaleDB o'rniga):
```
railway add postgres
```

**Redis**:
```
railway add redis
```

**Neo4j** (Dockerhub orqali):
```
Service → Docker Image → neo4j:5.15-community
```

Environment variables:
```
NEO4J_AUTH=neo4j/your_password
```

### 4️⃣ Environment Variables

Railway Dashboard → Variables:

```bash
# Auto-provided by Railway
DATABASE_URL=postgresql://...  # PostgreSQL
REDIS_URL=redis://...          # Redis

# Qo'lda qo'shish kerak
NEO4J_URI=bolt://neo4j.railway.internal:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=sk-xxxxx
ENVIRONMENT=production
```

---

## Loyiha Strukturasi

```
gimat/
├── Dockerfile              # Production build
├── docker-compose.yml      # Local development
├── railway.json           # Railway config
├── .env.railway           # Environment template
├── backend/
│   ├── main.py            # FastAPI app
│   ├── database/
│   │   └── railway_db.py  # Railway DB manager
│   ├── models/            # ML models
│   ├── rag/               # RAG module
│   └── requirements.txt
└── frontend/
    └── src/
```

---

## Local Development

```bash
# Docker Compose bilan
docker-compose up

# Faqat backend
docker-compose up backend

# View logs
docker-compose logs -f backend
```

**URL'lar**:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Neo4j Browser: http://localhost:7474
- Swagger Docs: http://localhost:8000/docs

---

## Railway Commands

```bash
# Logs
railway logs

# Environment variables
railway variables

# Connect to database
railway run psql

# Restart service
railway restart

# Remove project
railway delete
```

---

## Production Checklist

- [x] Dockerfile created
- [x] docker-compose.yml configured
- [x] Railway database manager
- [x] Environment variables template
- [x] Health check endpoint
- [ ] Custom domain setup
- [ ] SSL/TLS (auto via Railway)
- [ ] Monitoring setup
- [ ] Backup strategy

---

## Database Migrations

### TimescaleDB (PostgreSQL)

```bash
# Railway shell
railway run bash

# Run migrations
python -c "from database.railway_db import db_manager; import asyncio; asyncio.run(db_manager.connect_timescale())"
```

### Neo4j

```bash
# Railway Neo4j service
# Upload init script via Railway dashboard
# Or run via Cypher shell
```

---

## Monitoring

Railway provides:
- ✅ Automatic metrics
- ✅ Log aggregation
- ✅ Health checks
- ✅ Alerts

Custom monitoring:
```python
# backend/monitoring.py
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

---

## Cost Estimation

**Free Tier**:
- 500 hours/month
- $5 credit

**Hobby Tier** ($5/month):
- Unlimited hours
- 8GB memory
- 8 CPU cores

**GIMAT tahmini**:
- Backend: ~$5-10/month
- PostgreSQL: $5/month
- Neo4j: $10/month (custom Docker)
- Redis: Free (included)

**Total**: ~$20-25/month

---

## Troubleshooting

### Build fails

```bash
# Check logs
railway logs --deployment

# Rebuild
railway up --detach
```

### Database connection error

```bash
# Verify environment variables
railway variables

# Check service status
railway status
```

### Out of memory

```
# Railway dashboard → Settings → Change plan
```

---

## Custom Domain

Railway Dashboard → Settings → Domains:

```
gimat.uz → Custom domain
api.gimat.uz → Railway URL
```

DNS settings:
```
CNAME  api  your-project.up.railway.app
```

---

## GitHub Actions (Auto-deploy)

`.github/workflows/railway-deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        uses: railway/railway-action@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
```

Secrets qo'shish:
- GitHub → Settings → Secrets → `RAILWAY_TOKEN`

---

## Next Steps

1. **Deploy qiling** Railway'ga
2. **Test qiling** API endpoints
3. **Database'ni to'ldiring** initial data bilan
4. **Frontend'ni Deploy qiling** (Railway yoki Vercel)
5. **Custom domain sozlang**

---

## Support

- 📖 [Railway Docs](https://docs.railway.app)
- 💬 [Railway Discord](https://discord.gg/railway)
- 🐛 Issues: GitHub Issues

---

**Deploy vaqti**: ~5 daqiqa ⚡  
**Автоматик масштаблаш**: ✅  
**SSL сертификати**: Auto ✅
