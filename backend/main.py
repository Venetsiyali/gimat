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
        "http://localhost:3000",
        "https://gimat-frontend.vercel.app",
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

# No lifespan, no database, no imports - just works
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
