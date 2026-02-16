"""
GIMAT - TimescaleDB Database Configuration
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Index
from datetime import datetime
from config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


# ==========================================
# Database Models
# ==========================================

class Observation(Base):
    """Hydrological observation time series data"""
    __tablename__ = "observations"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    station_id = Column(String(50), nullable=False, index=True)
    station_name = Column(String(255))
    river_name = Column(String(255))
    
    # Hydrological parameters
    water_level = Column(Float)  # Water level (m)
    discharge = Column(Float)  # Discharge (m³/s)
    temperature = Column(Float)  # Water temperature (°C)
    
    # Meteorological parameters
    precipitation = Column(Float)  # Precipitation (mm)
    air_temperature = Column(Float)  # Air temperature (°C)
    humidity = Column(Float)  # Humidity (%)
    
    # Spatial info
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Source
    data_source = Column(String(100))  # uzhydromet, chirps, manual, etc.
    quality_flag = Column(String(20))  # good, suspect, missing, estimated
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_station_time', 'station_id', 'timestamp'),
        Index('idx_river_time', 'river_name', 'timestamp'),
    )


class Prediction(Base):
    """Model predictions time series"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    forecast_timestamp = Column(DateTime, nullable=False)  # When prediction was made
    station_id = Column(String(50), nullable=False, index=True)
    river_name = Column(String(255))
    
    # Predicted values
    predicted_discharge = Column(Float)
    predicted_water_level = Column(Float)
    
    # Uncertainty bounds
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    confidence_level = Column(Float)  # 0.95 for 95% confidence
    
    # Model info
    model_name = Column(String(100))  # hybrid, sarima, lstm, gnn, etc.
    model_version = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_station_forecast_time', 'station_id', 'forecast_timestamp', 'timestamp'),
    )


class WaveletComponent(Base):
    """Wavelet decomposition components for analysis"""
    __tablename__ = "wavelet_components"
    
    id = Column(Integer, primary_key=True, index=True)
    observation_id = Column(Integer, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    station_id = Column(String(50), nullable=False)
    
    # Wavelet decomposition
    wavelet_type = Column(String(20))  # db4, haar, etc.
    level = Column(Integer)  # Decomposition level
    component_type = Column(String(20))  # approximation, detail
    component_level = Column(Integer)  # 1, 2, 3, etc.
    
    # Component values
    coefficient_value = Column(Float)
    reconstructed_value = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelMetrics(Base):
    """Model performance metrics"""
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    station_id = Column(String(50))
    basin_name = Column(String(255))
    
    # Evaluation period
    eval_start_date = Column(DateTime)
    eval_end_date = Column(DateTime)
    
    # Performance metrics
    nse = Column(Float)  # Nash-Sutcliffe Efficiency
    kge = Column(Float)  # Kling-Gupta Efficiency
    rmse = Column(Float)  # Root Mean Squared Error
    mae = Column(Float)  # Mean Absolute Error
    r2 = Column(Float)  # R-squared
    pbias = Column(Float)  # Percent Bias
    
    # Additional info
    sample_size = Column(Integer)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_model_station', 'model_name', 'station_id'),
    )


# ==========================================
# Database Session Management
# ==========================================

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create TimescaleDB hypertables (run in sync mode)
    from sqlalchemy import create_engine, text
    sync_engine = create_engine(settings.sync_database_url)
    
    with sync_engine.connect() as conn:
        # Convert observations to hypertable
        try:
            conn.execute(text(
                "SELECT create_hypertable('observations', 'timestamp', "
                "if_not_exists => TRUE);"
            ))
            conn.commit()
        except Exception as e:
            print(f"Observations hypertable may already exist: {e}")
        
        # Convert predictions to hypertable
        try:
            conn.execute(text(
                "SELECT create_hypertable('predictions', 'timestamp', "
                "if_not_exists => TRUE);"
            ))
            conn.commit()
        except Exception as e:
            print(f"Predictions hypertable may already exist: {e}")
        
        # Convert wavelet_components to hypertable
        try:
            conn.execute(text(
                "SELECT create_hypertable('wavelet_components', 'timestamp', "
                "if_not_exists => TRUE);"
            ))
            conn.commit()
        except Exception as e:
            print(f"Wavelet components hypertable may already exist: {e}")
    
    sync_engine.dispose()
    print("✓ TimescaleDB initialized successfully")
