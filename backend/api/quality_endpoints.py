"""
Quality API Endpoints - Confidence & Alerts
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional

router = APIRouter()


class ObservationWithContext(BaseModel):
    observation: Dict
    historical_data: List[Dict] = []
    neighbor_observations: List[Dict] = []
    satellite_data: Optional[Dict] = None


class ConfidenceResult(BaseModel):
    confidence_score: float
    components: Dict
    is_reliable: bool
    quality_level: str


@router.post("/confidence", response_model=ConfidenceResult)
async def calculate_confidence(data: ObservationWithContext):
    """
    Calculate data confidence score
    
    Args:
        data: Observation with context
    
    Returns:
        Confidence score and components
    """
    from quality.confidence_scorer import ConfidenceScorer
    
    scorer = ConfidenceScorer()
    
    result = scorer.score(
        observation=data.observation,
        historical_data=data.historical_data,
        neighbor_observations=data.neighbor_observations,
        satellite_data=data.satellite_data
    )
    
    return ConfidenceResult(**result)


@router.get("/alerts/active")
async def get_active_alerts():
    """Get active data quality alerts"""
    from quality.satellite_validator import AlertSystem
    
    alert_system = AlertSystem()
    alerts = alert_system.get_active_alerts()
    
    return {"alerts": alerts, "count": len(alerts)}


@router.post("/anomaly/detect")
async def detect_anomaly(value: float, historical_values: List[float]):
    """
    Detect anomaly in data
    
    Args:
        value: Current value
        historical_values: Historical values
    
    Returns:
        Anomaly detection result
    """
    from quality.anomaly_detector import AnomalyDetector
    
    detector = AnomalyDetector(method='hybrid')
    result = detector.detect(value, historical_values)
    
    return result
