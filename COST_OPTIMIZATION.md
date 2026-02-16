# Railway Cost Optimization Guide

## 💰 Free Tier Maximization

Railway gives **$5 free credit** - make it last!

### Resource Limits

Set in `railway.json`:
```json
{
  "resources": {
    "memory": "2GB",
    "cpu": "1"
  }
}
```

### Sleep Mode

Railway auto-sleeps services after **30 minutes** of inactivity.

**Manual sleep**:
```bash
railway service pause
railway service resume
```

### Database Optimization

**PostgreSQL**:
- Keep only last 30 days of data for testing
- Enable compression (auto-configured)
- Limit connections: `max_connections=20`

**Neo4j**:
- Limit heap size:
  ```
  NEO4J_dbms_memory_heap_max__size=1G
  ```
- Disable unused features:
  ```
  NEO4J_PLUGINS=[]  # For testing
  ```

**Redis**:
- Use Railway's free tier
- Set TTL for cache:
  ```python
  redis.setex('key', 3600, 'value')  # 1 hour
  ```

### Code Optimizations

**1. Lazy Loading**:
```python
# models/model_loader.py
class ModelLoader:
    _models = {}
    
    def get_model(self, name):
        if name not in self._models:
            self._models[name] = self._load_model(name)
        return self._models[name]
```

**2. Single Worker**:
```json
{
  "deploy": {
    "startCommand": "uvicorn backend.main:app --workers 1"
  }
}
```

**3. Cache Aggressively**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_computation(param):
    # ML inference
    pass
```

## 📊 Cost Monitoring

### Railway Dashboard

- Monitor usage: Dashboard → Metrics
- Set alerts: Settings → Usage Alerts

### Cost Calculator

| Service | RAM | CPU | Hours | Cost/mo |
|---------|-----|-----|-------|---------|
| Backend | 2GB | 1 | 720 | $8 |
| PostgreSQL | 1GB | 0.5 | 720 | $4 |
| Neo4j | 1GB | 0.5 | 720 | $4 |
| Redis | 512MB | 0.25 | 720 | $2 |
| **Total** | | | | **$18** |

**With sleep mode** (50% usage): ~$9/mo

**Using $5 credit**: First month free, then $3-4/mo

## 🎯 Optimization Targets

### Phase 1: Testing (Free Tier)
- Enable sleep mode
- Minimal data
- 1 worker
- **Target**: $0 (using credit)

### Phase 2: Demo (Hobby)
- Wake on request
- 7 days data retention
- **Target**: $5-10/mo

### Phase 3: Production
- Always on
- Full features
- **Target**: $15-25/mo

## 🔧 Implementation

Update `railway.json`:
```json
{
  "resources": {
    "memory": "2GB",
    "cpu": "1"
  },
  "scaling": {
    "minInstances": 0,
    "maxInstances": 1
  }
}
```

Update environment:
```bash
WORKERS=1
LOG_LEVEL=warning  # Reduce logs
CACHE_TTL=3600
```

## 📈 Monitoring Commands

```bash
# Current usage
railway usage

# Service metrics
railway metrics

# Cost estimate
railway estimates
```

## ✅ Checklist

- [ ] Set memory to 2GB
- [ ] Set CPU to 1 core
- [ ] Enable sleep mode
- [ ] Configure compression
- [ ] Lazy load models
- [ ] Cache responses
- [ ] Monitor usage weekly
- [ ] Clean old data monthly
