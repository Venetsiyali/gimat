"""
GIMAT - Pydantic Schemas
Data validation and serialization models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==========================================
# Observation Schemas
# ==========================================

class ObservationCreate(BaseModel):
    """Schema for creating a new observation"""
    timestamp: datetime
    station_id: str
    station_name: Optional[str] = None
    river_name: Optional[str] = None
    
    # Hydrological parameters
    water_level: Optional[float] = None
    discharge: Optional[float] = None
    temperature: Optional[float] = None
    
    # Meteorological parameters
    precipitation: Optional[float] = None
    air_temperature: Optional[float] = None
    humidity: Optional[float] = None
    
    # Spatial info
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Source
    data_source: Optional[str] = "manual"
    quality_flag: Optional[str] = "good"


class ObservationResponse(ObservationCreate):
    """Schema for observation response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StationListResponse(BaseModel):
    """Schema for station list"""
    station_id: str
    station_name: Optional[str]
    river_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class TimeSeriesDataPoint(BaseModel):
    """Single data point in time series"""
    timestamp: datetime
    value: float


class TimeSeriesResponse(BaseModel):
    """Schema for time series data"""
    station_id: str
    station_name: Optional[str]
    river_name: Optional[str]
    parameter: str
    start_date: datetime
    end_date: datetime
    data_points: List[TimeSeriesDataPoint]
    count: int


# ==========================================
# Prediction Schemas
# ==========================================

class PredictionResponse(BaseModel):
    """Schema for prediction response"""
    id: int
    timestamp: datetime
    forecast_timestamp: datetime
    station_id: str
    river_name: Optional[str]
    predicted_discharge: Optional[float]
    predicted_water_level: Optional[float]
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    confidence_level: Optional[float]
    model_name: str
    model_version: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ForecastRequest(BaseModel):
    """Schema for forecast request"""
    station_id: str
    forecast_horizon_days: int = Field(default=7, ge=1, le=30)
    model_name: Optional[str] = "hybrid"


class ForecastDataPoint(BaseModel):
    """Single forecast data point"""
    timestamp: datetime
    predicted_discharge: Optional[float]
    predicted_water_level: Optional[float]
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    confidence_level: float


class ForecastResponse(BaseModel):
    """Schema for forecast response"""
    station_id: str
    model_name: str
    forecast_timestamp: datetime
    forecast_horizon_days: int
    predictions: List[ForecastDataPoint]
    message: str


# ==========================================
# Ontology Schemas
# ==========================================

class RiverCreateRequest(BaseModel):
    """Schema for creating a river"""
    name: str
    basin: str
    length_km: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None


class HydropostCreateRequest(BaseModel):
    """Schema for creating a hydropost"""
    station_id: str
    name: str
    river_name: str
    latitude: float
    longitude: float
    river_km: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None


class ReservoirCreateRequest(BaseModel):
    """Schema for creating a reservoir"""
    reservoir_id: str
    name: str
    river_name: str
    capacity_m3: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None


class NetworkNode(BaseModel):
    """Schema for graph network node"""
    id: str
    type: str  # river_reach, hydropost, reservoir, etc.
    properties: Dict[str, Any]


class NetworkEdge(BaseModel):
    """Schema for graph network edge"""
    from_: str = Field(alias="from")
    to: str
    type: str  # FLOWS_TO, MONITORS, INFLUENCES, etc.
    
    class Config:
        populate_by_name = True


class NetworkResponse(BaseModel):
    """Schema for network topology response"""
    river_name: str
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    node_count: int
    edge_count: int


# ==========================================
# ML Model Schemas
# ==========================================

class WaveletDecompositionResult(BaseModel):
    """Schema for wavelet decomposition result"""
    approximation: List[float]
    details: List[List[float]]
    level: int
    wavelet_type: str


class ModelTrainingRequest(BaseModel):
    """Schema for model training request"""
    station_id: str
    model_name: str
    start_date: datetime
    end_date: datetime
    hyperparameters: Optional[Dict[str, Any]] = None


class ModelEvaluationMetrics(BaseModel):
    """Schema for model evaluation metrics"""
    nse: Optional[float] = None
    kge: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2: Optional[float] = None
    pbias: Optional[float] = None


# ==========================================
# XAI Schemas
# ==========================================

class SHAPExplanation(BaseModel):
    """Schema for SHAP explanation"""
    feature_names: List[str]
    shap_values: List[float]
    base_value: float
    predicted_value: float


class LIMEExplanation(BaseModel):
    """Schema for LIME explanation"""
    feature_names: List[str]
    feature_weights: List[float]
    score: float
    local_prediction: float
