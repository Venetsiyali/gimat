"""
Vercel Serverless Entry Point for GIMAT API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Create FastAPI app
app = FastAPI(
    title="GIMAT API",
    description="Gidrologik Intellektual Monitoring va Axborot Tizimi",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def root():
    return {
        "message": "GIMAT API is running",
        "version": "2.0.0",
        "deployment": "Vercel Serverless"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import lightweight routes only
# Heavy ML operations should be moved to external service

try:
    from api.routes import simple_data
    app.include_router(simple_data.router, prefix="/api/data", tags=["Data"])
except ImportError:
    print("Warning: Some routes not available in serverless mode")

# Vercel handler (required)
handler = Mangum(app)
