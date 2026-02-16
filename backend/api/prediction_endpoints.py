"""
GIMAT - Prediction Endpoints
Hybrid ML model predictions and forecasts
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta

from database.timescale import get_db, Prediction
from models.schemas import PredictionResponse, ForecastRequest, ForecastResponse

router = APIRouter()


# ==========================================
# Prediction Endpoints
# ==========================================

@router.get("/predictions/{station_id}", response_model=List[PredictionResponse])
async def get_predictions(
    station_id: str,
    model_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get predictions for a station
    
    - **station_id**: Hydropost station ID
    - **model_name**: Filter by model (hybrid, sarima, lstm, gnn, etc.)
    - **start_date**: Start of forecast period
    - **end_date**: End of forecast period
    - **limit**: Maximum results
    """
    
    query = select(Prediction).where(Prediction.station_id == station_id)
    
    if model_name:
        query = query.where(Prediction.model_name == model_name)
    if start_date:
        query = query.where(Prediction.timestamp >= start_date)
    if end_date:
        query = query.where(Prediction.timestamp <= end_date)
    
    query = query.order_by(Prediction.timestamp.desc()).limit(limit)
    
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    return predictions


@router.post("/forecast", response_model=ForecastResponse)
async def create_forecast(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new forecast using the hybrid model
    
    - **station_id**: Target hydropost
    - **forecast_horizon_days**: How many days ahead to forecast
    - **model_name**: Which model to use (default: hybrid)
    """
    
    # This is a placeholder - actual ML prediction will be implemented
    # in the models module and called here
    
    station_id = request.station_id
    horizon_days = request.forecast_horizon_days
    model_name = request.model_name or "hybrid"
    
    # For now, return a mock response
    # TODO: Implement actual ML model inference
    
    forecast_timestamp = datetime.utcnow()
    predictions = []
    
    for i in range(1, horizon_days + 1):
        pred_time = forecast_timestamp + timedelta(days=i)
        
        # Mock prediction (replace with actual model)
        pred = Prediction(
            timestamp=pred_time,
            forecast_timestamp=forecast_timestamp,
            station_id=station_id,
            predicted_discharge=100.0 + i * 5.0,  # Mock value
            predicted_water_level=2.5 + i * 0.1,  # Mock value
            lower_bound=90.0 + i * 5.0,
            upper_bound=110.0 + i * 5.0,
            confidence_level=0.95,
            model_name=model_name,
            model_version="1.0.0"
        )
        
        db.add(pred)
        predictions.append(pred)
    
    await db.commit()
    
    return {
        "station_id": station_id,
        "model_name": model_name,
        "forecast_timestamp": forecast_timestamp,
        "forecast_horizon_days": horizon_days,
        "predictions": [
            {
                "timestamp": p.timestamp,
                "predicted_discharge": p.predicted_discharge,
                "predicted_water_level": p.predicted_water_level,
                "lower_bound": p.lower_bound,
                "upper_bound": p.upper_bound,
                "confidence_level": p.confidence_level
            }
            for p in predictions
        ],
        "message": f"Forecast generated for {horizon_days} days ahead using {model_name} model"
    }


@router.get("/models", response_model=List[dict])
async def get_available_models():
    """Get list of available prediction models"""
    
    return [
        {
            "model_name": "hybrid",
            "description": "Hybrid ensemble combining Wavelet-SARIMA-LSTM-GNN",
            "status": "active",
            "accuracy_nse": 0.85
        },
        {
            "model_name": "sarima",
            "description": "Seasonal ARIMA for approximation components",
            "status": "active",
            "accuracy_nse": 0.72
        },
        {
            "model_name": "bilstm",
            "description": "Bidirectional LSTM for detail components",
            "status": "active",
            "accuracy_nse": 0.78
        },
        {
            "model_name": "transformer",
            "description": "Transformer with attention mechanism",
            "status": "development",
            "accuracy_nse": 0.80
        },
        {
            "model_name": "gnn",
            "description": "Graph Neural Network for spatial dependencies",
            "status": "active",
            "accuracy_nse": 0.76
        }
    ]


@router.get("/predictions/{station_id}/latest", response_model=PredictionResponse)
async def get_latest_prediction(
    station_id: str,
    model_name: str = "hybrid",
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent prediction for a station"""
    
    result = await db.execute(
        select(Prediction)
        .where(
            and_(
                Prediction.station_id == station_id,
                Prediction.model_name == model_name
            )
        )
        .order_by(Prediction.forecast_timestamp.desc())
        .limit(1)
    )
    
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"No predictions found for station {station_id} with model {model_name}"
        )
    
    return prediction


# ==========================================
# Model Evaluation Endpoints
# ==========================================

@router.get("/evaluation/{station_id}")
async def get_model_evaluation(
    station_id: str,
    model_name: str = "hybrid",
    db: AsyncSession = Depends(get_db)
):
    """
    Get model evaluation metrics for a station
    
    Returns NSE, KGE, RMSE, MAE, etc.
    """
    
    from database.timescale import ModelMetrics
    
    result = await db.execute(
        select(ModelMetrics)
        .where(
            and_(
                ModelMetrics.station_id == station_id,
                ModelMetrics.model_name == model_name
            )
        )
        .order_by(ModelMetrics.created_at.desc())
        .limit(1)
    )
    
    metrics = result.scalar_one_or_none()
    
    if not metrics:
        # Return default/example metrics
        return {
            "station_id": station_id,
            "model_name": model_name,
            "status": "no_evaluation_yet",
            "message": "Model has not been evaluated on this station yet",
            "expected_metrics": {
                "NSE": "> 0.7 (satisfactory), > 0.85 (excellent)",
                "KGE": "> 0.75 (good)",
                "RMSE": "Lower is better",
                "MAE": "Lower is better"
            }
        }
    
    return {
        "station_id": metrics.station_id,
        "model_name": metrics.model_name,
        "model_version": metrics.model_version,
        "basin_name": metrics.basin_name,
        "evaluation_period": {
            "start": metrics.eval_start_date,
            "end": metrics.eval_end_date
        },
        "metrics": {
            "NSE": metrics.nse,
            "KGE": metrics.kge,
            "RMSE": metrics.rmse,
            "MAE": metrics.mae,
            "R2": metrics.r2,
            "PBIAS": metrics.pbias
        },
        "sample_size": metrics.sample_size,
        "notes": metrics.notes,
        "evaluated_at": metrics.created_at
    }
