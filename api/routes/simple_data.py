"""
Simple data routes for Vercel serverless
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()


class StationInfo(BaseModel):
    station_id: str
    station_name: str
    river_name: str
    status: str


@router.get("/stations")
async def get_stations():
    """Get list of hydroposts"""
    # Mock data - in production, connect to database
    stations = [
        {
            "station_id": "HP_CHIRCHIQ_001",
            "station_name": "Gazalkent",
            "river_name": "Chirchiq",
            "status": "active"
        },
        {
            "station_id": "HP_CHIRCHIQ_002",
            "station_name": "Tashkent",
            "river_name": "Chirchiq",
            "status": "active"
        },
        {
            "station_id": "HP_ZARAFSHON_001",
            "station_name": "Dupuli",
            "river_name": "Zarafshon",
            "status": "active"
        }
    ]
    
    return {"stations": stations, "count": len(stations)}


@router.get("/stations/{station_id}/latest")
async def get_latest_observation(station_id: str):
    """Get latest observation for a station"""
    # Mock data
    return {
        "station_id": station_id,
        "timestamp": datetime.now().isoformat(),
        "discharge": 125.3,
        "water_level": 2.45,
        "temperature": 15.2,
        "quality": "good"
    }


@router.get("/status")
async def api_status():
    """API status check"""
    return {
        "status": "operational",
        "version": "2.0.0",
        "mode": "serverless",
        "timestamp": datetime.now().isoformat()
    }
