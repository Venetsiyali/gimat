"""
GIMAT - Data Endpoints
Hydrological observations CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta

from database.timescale import get_db, Observation
from models.schemas import (
    ObservationCreate, ObservationResponse,
    StationListResponse, TimeSeriesResponse
)

router = APIRouter()


# ==========================================
# Observations Endpoints
# ==========================================

@router.post("/observations", response_model=ObservationResponse, status_code=201)
async def create_observation(
    observation: ObservationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new hydrological observation"""
    
    db_observation = Observation(**observation.model_dump())
    db.add(db_observation)
    await db.commit()
    await db.refresh(db_observation)
    
    return db_observation


@router.get("/observations", response_model=List[ObservationResponse])
async def get_observations(
    station_id: Optional[str] = None,
    river_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get hydrological observations with filters
    
    - **station_id**: Filter by hydropost station ID
    - **river_name**: Filter by river name
    - **start_date**: Start of time range (ISO format)
    - **end_date**: End of time range (ISO format)
    - **limit**: Maximum number of results (max 1000)
    """
    
    query = select(Observation)
    
    # Build filters
    filters = []
    if station_id:
        filters.append(Observation.station_id == station_id)
    if river_name:
        filters.append(Observation.river_name == river_name)
    if start_date:
        filters.append(Observation.timestamp >= start_date)
    if end_date:
        filters.append(Observation.timestamp <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(Observation.timestamp.desc()).limit(limit)
    
    result = await db.execute(query)
    observations = result.scalars().all()
    
    return observations


@router.get("/observations/{observation_id}", response_model=ObservationResponse)
async def get_observation(
    observation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific observation by ID"""
    
    result = await db.execute(
        select(Observation).where(Observation.id == observation_id)
    )
    observation = result.scalar_one_or_none()
    
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    return observation


# ==========================================
# Stations Endpoints
# ==========================================

@router.get("/stations", response_model=List[StationListResponse])
async def get_stations(
    river_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all monitoring stations
    
    - **river_name**: Optional filter by river name
    """
    
    query = select(
        Observation.station_id,
        Observation.station_name,
        Observation.river_name,
        Observation.latitude,
        Observation.longitude
    ).distinct()
    
    if river_name:
        query = query.where(Observation.river_name == river_name)
    
    result = await db.execute(query)
    stations = result.all()
    
    return [
        {
            "station_id": s[0],
            "station_name": s[1],
            "river_name": s[2],
            "latitude": s[3],
            "longitude": s[4]
        }
        for s in stations
    ]


@router.get("/stations/{station_id}/latest", response_model=ObservationResponse)
async def get_latest_observation(
    station_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the latest observation for a station"""
    
    result = await db.execute(
        select(Observation)
        .where(Observation.station_id == station_id)
        .order_by(Observation.timestamp.desc())
        .limit(1)
    )
    observation = result.scalar_one_or_none()
    
    if not observation:
        raise HTTPException(
            status_code=404,
            detail=f"No observations found for station {station_id}"
        )
    
    return observation


# ==========================================
# Time Series Endpoints
# ==========================================

@router.get("/timeseries/{station_id}", response_model=TimeSeriesResponse)
async def get_time_series(
    station_id: str,
    parameter: str = Query(..., description="discharge, water_level, precipitation, temperature"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get time series data for a specific parameter
    
    - **station_id**: Hydropost station ID
    - **parameter**: Hydrological parameter (discharge, water_level, precipitation, temperature)
    - **start_date**: Start date (default: 30 days ago)
    - **end_date**: End date (default: now)
    """
    
    # Default time range
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Validate parameter
    valid_parameters = ["discharge", "water_level", "precipitation", "temperature", 
                       "air_temperature", "humidity"]
    if parameter not in valid_parameters:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameter. Must be one of: {', '.join(valid_parameters)}"
        )
    
    # Query observations
    result = await db.execute(
        select(Observation)
        .where(
            and_(
                Observation.station_id == station_id,
                Observation.timestamp >= start_date,
                Observation.timestamp <= end_date
            )
        )
        .order_by(Observation.timestamp)
    )
    observations = result.scalars().all()
    
    if not observations:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for station {station_id}"
        )
    
    # Extract time series
    timestamps = [obs.timestamp for obs in observations]
    values = [getattr(obs, parameter) for obs in observations]
    
    # Filter out None values
    data_points = [
        {"timestamp": t, "value": v}
        for t, v in zip(timestamps, values)
        if v is not None
    ]
    
    return {
        "station_id": station_id,
        "station_name": observations[0].station_name,
        "river_name": observations[0].river_name,
        "parameter": parameter,
        "start_date": start_date,
        "end_date": end_date,
        "data_points": data_points,
        "count": len(data_points)
    }


# ==========================================
# Statistics Endpoints
# ==========================================

@router.get("/stations/{station_id}/statistics")
async def get_station_statistics(
    station_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get basic statistics for a station"""
    
    # Default time range
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=365)  # 1 year
    
    result = await db.execute(
        select(Observation)
        .where(
            and_(
                Observation.station_id == station_id,
                Observation.timestamp >= start_date,
                Observation.timestamp <= end_date
            )
        )
    )
    observations = result.scalars().all()
    
    if not observations:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for station {station_id}"
        )
    
    # Calculate statistics
    import numpy as np
    
    discharges = [o.discharge for o in observations if o.discharge is not None]
    water_levels = [o.water_level for o in observations if o.water_level is not None]
    
    stats = {
        "station_id": station_id,
        "period": {
            "start": start_date,
            "end": end_date
        },
        "total_observations": len(observations),
        "discharge": {
            "mean": np.mean(discharges) if discharges else None,
            "min": np.min(discharges) if discharges else None,
            "max": np.max(discharges) if discharges else None,
            "std": np.std(discharges) if discharges else None,
            "count": len(discharges)
        } if discharges else None,
        "water_level": {
            "mean": float(np.mean(water_levels)) if water_levels else None,
            "min": float(np.min(water_levels)) if water_levels else None,
            "max": float(np.max(water_levels)) if water_levels else None,
            "std": float(np.std(water_levels)) if water_levels else None,
            "count": len(water_levels)
        } if water_levels else None
    }
    
    return stats
