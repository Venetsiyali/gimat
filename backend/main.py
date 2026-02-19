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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
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

# No lifespan, no database, no imports - just works
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
