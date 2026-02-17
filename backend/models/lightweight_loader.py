"""
Lightweight ML Model Loader for Railway
Uses external APIs instead of local PyTorch models
"""

import os
import httpx
import pickle
import numpy as np
from typing import Dict, List, Optional
import asyncio


class ExternalModelAPI:
    """
    Call external ML inference APIs (Hugging Face, Replicate, etc.)
    instead of loading heavy PyTorch models locally
    """
    
    def __init__(self):
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model_api_url = os.getenv('ML_MODEL_API_URL')
    
    async def predict_discharge(self, features: Dict) -> Dict:
        """
        Predict river discharge using external API
        
        Args:
            features: {'temperature': float, 'precipitation': float, ...}
        
        Returns:
            {'prediction': float, 'confidence': float}
        """
        
        # Option 1: Use Hugging Face Inference API
        if self.hf_api_key:
            return await self._huggingface_inference(features)
        
        # Option 2: Use custom ML service (e.g., Railway separate service)
        elif self.model_api_url:
            return await self._custom_api_inference(features)
        
        # Option 3: Fallback to simple statistical model
        else:
            return await self._fallback_statistical_model(features)
    
    async def _huggingface_inference(self, features: Dict) -> Dict:
        """Call Hugging Face Inference API"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/your-model-name",
                headers={"Authorization": f"Bearer {self.hf_api_key}"},
                json={"inputs": features},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'prediction': result[0]['score'],
                    'confidence': 0.85
                }
            else:
                raise Exception(f"HF API error: {response.text}")
    
    async def _custom_api_inference(self, features: Dict) -> Dict:
        """Call custom ML service (e.g., separate Railway service with GPU)"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.model_api_url}/predict",
                json=features,
                timeout=30.0
            )
            
            return response.json()
    
    async def _fallback_statistical_model(self, features: Dict) -> Dict:
        """
        Lightweight fallback using statsmodels (no PyTorch needed)
        Uses simple SARIMA or linear regression
        """
        
        # Simple linear model as fallback
        # In production, use pre-trained statsmodels coefficients
        
        prediction = (
            features.get('temperature', 0) * 1.5 +
            features.get('precipitation', 0) * 2.3 +
            features.get('snow_cover', 0) * 0.8
        )
        
        return {
            'prediction': max(0, prediction),
            'confidence': 0.65,
            'model': 'fallback_linear'
        }


class LightweightSklearnModel:
    """
    Use scikit-learn for lightweight ML (already installed)
    Much faster than PyTorch for simple tasks
    """
    
    def __init__(self):
        self.models = {}
    
    async def load_model(self, model_path: str):
        """Load pre-trained sklearn model from file"""
        
        if not os.path.exists(model_path):
            return None
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        return model
    
    async def predict(self, model_name: str, features: np.ndarray):
        """Predict using sklearn model"""
        
        if model_name not in self.models:
            # Try to load from storage
            model_path = f"/app/data/models/{model_name}.pkl"
            self.models[model_name] = await self.load_model(model_path)
        
        model = self.models.get(model_name)
        
        if model is None:
            raise ValueError(f"Model {model_name} not found")
        
        prediction = model.predict(features)
        
        return {
            'prediction': float(prediction[0]),
            'model_type': 'sklearn'
        }


# Global instances
external_api = ExternalModelAPI()
sklearn_models = LightweightSklearnModel()


async def get_forecast(station_id: str, horizon: int = 7) -> List[Dict]:
    """
    Main forecast function - uses external APIs
    
    Args:
        station_id: Monitoring station ID
        horizon: Forecast horizon in days
    
    Returns:
        List of predictions
    """
    
    # Get historical data
    # features = await get_station_features(station_id)
    
    # Mock features for demo
    features = {
        'temperature': 15.0,
        'precipitation': 10.0,
        'snow_cover': 5.0
    }
    
    # Call external model
    result = await external_api.predict_discharge(features)
    
    # Generate forecast for horizon
    forecasts = []
    for day in range(horizon):
        forecasts.append({
            'day': day + 1,
            'discharge': result['prediction'] * (1 + day * 0.02),
            'confidence': result['confidence'] - (day * 0.05)
        })
    
    return forecasts
