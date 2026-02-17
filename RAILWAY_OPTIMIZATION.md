# Railway Deployment Strategy

## Problem
Build timeout (10+ minutes) due to heavy dependencies:
- PyTorch: ~500MB
- Playwright: ~300MB
- SpaCy models: ~100MB

## Solution: Lightweight + External Services

### 1. Optimized Requirements
**Removed**:
- ✅ PyTorch → External API
- ✅ Playwright → httpx only
- ✅ Heavy NLP models → transformers only
- ✅ Prophet → statsmodels only

**Build time**: 10+ min → **~2-3 min** ✅

### 2. ML Model Strategy

#### Option A: Hugging Face Inference API (Recommended)
```python
# Free tier: 30,000 calls/month
# No local GPU needed

HUGGINGFACE_API_KEY=your_key
```

Upload models to Hugging Face:
```bash
huggingface-cli login
huggingface-cli upload your-username/gimat-lstm-model ./models/
```

#### Option B: Separate ML Service on Railway
Deploy heavy models on separate Railway service with GPU:

```
Project Structure:
├── gimat-api (main service) - Lightweight
└── gimat-ml (ML service) - PyTorch + GPU
```

Railway supports multiple services - ML service can use GPU:
```json
{
  "build": {"builder": "DOCKERFILE"},
  "deploy": {"restartPolicyType": "ON_FAILURE"},
  "resources": {
    "memory": "8GB",
    "gpu": true
  }
}
```

Cost: ~$20/mo for GPU service

#### Option C: ONNX Runtime
Convert PyTorch → ONNX (smaller, faster):
```bash
# On your local machine
python convert_to_onnx.py

# In requirements.txt
onnxruntime==1.16.3  # Much smaller than PyTorch
```

### 3. Deployment Steps

```bash
# 1. Commit optimized code
git add .
git commit -m "feat: Lightweight Railway deployment"
git push origin main

# 2. Railway auto-deploys
# Build time: ~2-3 minutes ✅

# 3. Add environment variables
railway variables set HUGGINGFACE_API_KEY=your_key
railway variables set ML_MODEL_API_URL=https://your-ml-service.railway.app
```

### 4. Cost Comparison

| Strategy | Build Time | Monthly Cost |
|----------|-----------|--------------|
| Heavy (all local) | 10-15 min ❌ | Timeout ❌ |
| **Lightweight + HF API** | **2-3 min** ✅ | **$5-10** ✅ |
| Separate ML Service | 2-3 min (API) + 5 min (ML) | $20-30 |
| ONNX local | 3-4 min | $10-15 |

### 5. Features Status

| Feature | Status | Notes |
|---------|--------|-------|
| Basic API | ✅ | FastAPI + DB |
| Data ingestion | ✅ | Scrapers work |
| Neo4j graph | ✅ | Lightweight driver |
| RAG Q&A | ✅ | sentence-transformers |
| **ML forecasting** | ⚠️ | **External API** |
| PINN models | ⚠️ | **External API** |
| GNN spatial | ⚠️ | **External API** |
| XAI (SHAP/LIME) | ❌ | Can add later |

### 6. Production Workflow

```
User Request → Railway API → Check cache (Redis)
                          ↓
                      Cache miss?
                          ↓
                   Call HF API / ML Service
                          ↓
                   Cache result (1 hour)
                          ↓
                   Return to user
```

### 7. Next Steps

1. ✅ Deploy lightweight version NOW
2. Test basic functionality
3. Add ML inference later via:
   - Hugging Face API (easiest)
   - Separate Railway ML service (more control)
   - ONNX models (offline capable)

---

**Current Status**: Ready to deploy in 2-3 minutes! ⚡
