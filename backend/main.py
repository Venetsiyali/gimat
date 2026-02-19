"""
GIMAT API - Absolute Minimum for Railway
Zero dependencies on other modules
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Minimal app - NO external imports
app = FastAPI(
    title="GIMAT API",
    version="1.0.0-minimal"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gimat.vercel.app",
        "https://gimat-production.up.railway.app",
        "http://localhost:3000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "running", "app": "GIMAT", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/status")
def status():
    return {"railway": True, "deployment": "success"}

@app.get("/api/ontology/network/{river_name}")
def get_network(river_name: str):
    """
    Returns mock network data for visualization
    """
    # Mock data for Chirchiq river
    if river_name == "Chirchiq":
        return {
            "river_name": "Chirchiq",
            "node_count": 5,
            "edge_count": 4,
            "nodes": [
                {"id": "node1", "label": "Chorvoq suv ombori", "type": "hydropost", "data": {"type": "reservoir"}},
                {"id": "node2", "label": "G'azalkent GES", "type": "hydropost", "data": {"type": "hpp"}},
                {"id": "node3", "label": "Chirchiq sh.", "type": "hydropost", "data": {"type": "post"}},
                {"id": "node4", "label": "Toshkent (Oqtepa)", "type": "hydropost", "data": {"type": "post"}},
                {"id": "node5", "label": "Chinoz", "type": "hydropost", "data": {"type": "post"}}
            ],
            "edges": [
                {"source": "node1", "target": "node2", "label": "Oqim"},
                {"source": "node2", "target": "node3", "label": "Oqim"},
                {"source": "node3", "target": "node4", "label": "Oqim"},
                {"source": "node4", "target": "node5", "label": "Oqim"}
            ]
        }
    
    # Mock data for Zarafshon
    return {
        "river_name": river_name,
        "nodes": [
            {"id": "z1", "label": "Tojikiston chegarasi", "type": "hydropost", "data": {"type": "border"}},
            {"id": "z2", "label": "Ravotxo'ja tuguni", "type": "hydropost", "data": {"type": "node"}},
            {"id": "z3", "label": "Navoiy", "type": "hydropost", "data": {"type": "post"}}
        ],
        "edges": [
            {"source": "z1", "target": "z2"},
            {"source": "z2", "target": "z3"}
        ]
    }

@app.post("/api/predictions/forecast")
def get_forecast(data: dict):
    """
    Returns mock forecast data for visualization.
    Accepts any JSON body.
    """
    import random
    from datetime import datetime, timedelta

    # Generate mock time series
    history = []
    forecast = []
    start_date = datetime.now() - timedelta(days=30)

    # 30 days of history
    for i in range(30):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        val_h = 2.0 + (i * 0.05) + (random.random() * 0.5)
        val_q = 120 + (i * 2) + (random.random() * 10)
        history.append({"date": date, "H": round(val_h, 2), "Q": int(val_q), "type": "history"})

    # 7 days of forecast
    for i in range(7):
        date = (start_date + timedelta(days=30+i)).strftime("%Y-%m-%d")
        val_h = 3.5 + (random.random() * 0.5)
        val_q = 180 + (random.random() * 10)
        forecast.append({"date": date, "H": round(val_h, 2), "Q": int(val_q), "type": "forecast"})

    return {
        "status": "success",
        "model": "Hybrid-Wavelet-BiLSTM",
        "metrics": {
            "NSE": 0.92,
            "RMSE": 0.045,
            "MAE": 0.032,
            "R2": 0.94
        },
        "data": history + forecast
    }

# No lifespan, no database, no imports - just works
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
