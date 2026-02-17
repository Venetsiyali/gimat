"""
GIMAT API - Minimal Railway Version
Only essential endpoints, no heavy dependencies
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup with graceful degradation"""
    print("="*50)
    print("GIMAT API Starting (Railway Minimal)")
    print("="*50)
    
    # Optional database connections
    try:
        from backend.database.railway_db import db_manager
        await db_manager.connect_all()
        print("✓ Databases connected")
    except ImportError:
        print("⚠ Database module not available")
    except Exception as e:
        print(f"⚠ Database skipped: {str(e)[:100]}")
    
    print("✓ API Ready!")
    print("="*50)
    
    yield
    
    print("Shutting down...")

# Create app
app = FastAPI(
    title="GIMAT API",
    description="Hydrological Intelligence System - Railway Deployment",
    version="1.0.0-railway",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Essential Endpoints
# ==========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "GIMAT",
        "version": "1.0.0-railway",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """Health check - always returns healthy if app is running"""
    return {
        "status": "healthy",
        "version": "1.0.0-railway"
    }

@app.get("/api/status")
async def api_status():
    """API status information"""
    return {
        "api": "operational",
        "mode": "minimal",
        "features": ["basic-api", "database-ready"],
        "railway": True
    }

# ==========================================
# Optional routers (graceful import)
# ==========================================

try:
    from backend.api.data_endpoints import router as data_router
    app.include_router(data_router, prefix="/api/data", tags=["Data"])
    print("✓ Data endpoints loaded"
)
except ImportError as e:
    print(f"⚠ Data endpoints skipped: {e}")

try:
    from backend.api.prediction_endpoints import router as prediction_router
    app.include_router(prediction_router, prefix="/api/predictions", tags=["Predictions"])
    print("✓ Prediction endpoints loaded")
except ImportError:
    print("⚠ Prediction endpoints skipped")

# Main
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
