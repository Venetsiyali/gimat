"""
GIMAT - Gidrologik Intellektual Monitoring va Axborot Tizimi
Configuration Management
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "GIMAT"
    app_version: str = "1.0.0"
    environment: str = "development"
    api_secret_key: str
    
    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # PostgreSQL / TimescaleDB
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str
    
    @property
    def database_url(self) -> str:
        """Construct database URL"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def sync_database_url(self) -> str:
        """Construct synchronous database URL"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str
    
    # External APIs
    chirps_api_url: str = "https://data.chc.ucsb.edu/products/CHIRPS-2.0"
    uzhydromet_url: str = "https://www.meteo.uz"
    
    # ML Models
    model_checkpoint_dir: str = "./ml_models/checkpoints"
    training_logs_dir: str = "./logs/training"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/gimat.log"
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Wavelet settings
    wavelet_type: str = "db4"  # Daubechies 4
    wavelet_level: int = 3
    
    # Model training
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Ensure directories exist
os.makedirs(settings.model_checkpoint_dir, exist_ok=True)
os.makedirs(settings.training_logs_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
