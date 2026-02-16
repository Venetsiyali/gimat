"""
GIMAT - Gidrologik Intellektual Monitoring va Axborot Tizimi
FastAPI Main Application
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from database.timescale import init_db as init_timescale
from database.neo4j_db import neo4j_db


# ==========================================
# Lifespan Context Manager
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("="*50)
    print("🚀 GIMAT Starting Up...")
    print("="*50)
    
    # Initialize databases
    try:
        await init_timescale()
        print("✓ TimescaleDB initialized")
    except Exception as e:
        print(f"⚠️  TimescaleDB initialization error: {e}")
    
    try:
        await neo4j_db.connect()
        print("✓ Neo4j connected")
    except Exception as e:
        print(f"⚠️  Neo4j connection error: {e}")
    
    print("="*50)
    print(f"✓ GIMAT is ready at http://{settings.api_host}:{settings.api_port}")
    print(f"📚 API Docs: http://{settings.api_host}:{settings.api_port}/docs")
    print("="*50)
    
    yield
    
    # Shutdown
    print("\n" + "="*50)
    print("🛑 GIMAT Shutting Down...")
    print("="*50)
    
    try:
        await neo4j_db.close()
        print("✓ Neo4j connection closed")
    except Exception as e:
        print(f"⚠️  Neo4j close error: {e}")
    
    print("✓ GIMAT shutdown complete")
    print("="*50)


# ==========================================
# FastAPI Application
# ==========================================

app = FastAPI(
    title="GIMAT API",
    description="""
    **GIMAT** — Gidrologik Intellektual Monitoring va Axborot Tizimi
    
    Hydrological Intelligent Monitoring and Information System
    
    ## Features
    
    * **Data Collection**: Automated scraping from O'zgidromet, CHIRPS API
    * **Graph Ontology**: Neo4j river network topology
    * **Time Series**: TimescaleDB for hydrological observations
    * **Hybrid ML Models**: Wavelet + SARIMA + Bi-LSTM + GNN
    * **Explainable AI**: SHAP and LIME explanations
    * **Real-time Monitoring**: WebSocket support
    
    ## Test Basins
    
    * Chirchiq Basin (Syr Darya tributary)
    * Zarafshon Basin (Transboundary river)
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ==========================================
# CORS Middleware
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Root Endpoint
# ==========================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - system information"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs",
        "message": "GIMAT — Gidrologik Intellektual Monitoring va Axborot Tizimi"
    }


@app.get("/health", tags=["Root"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "databases": {
            "timescaledb": "connected",
            "neo4j": "connected" if neo4j_db.driver else "disconnected"
        }
    }


# ==========================================
# Include Routers
# ==========================================

# Import and include API routers
from api.data_endpoints import router as data_router
from api.prediction_endpoints import router as prediction_router
from api.ontology_endpoints import router as ontology_router
from api.rag_endpoints import router as rag_router
from api.dss_endpoints import router as dss_router
from api.quality_endpoints import router as quality_router

# Register routers
app.include_router(data_router, prefix="/api/data", tags=["Data"])
app.include_router(prediction_router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(ontology_router, prefix="/api/ontology", tags=["Ontology"])
app.include_router(rag_router, prefix="/api/rag", tags=["RAG"])
app.include_router(dss_router, prefix="/api/dss", tags=["DSS"])
app.include_router(quality_router, prefix="/api/quality", tags=["Quality"])


# ==========================================
# Run Application
# ==========================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
