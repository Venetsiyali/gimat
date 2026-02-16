"""
GIMAT - SARIMA Model
Seasonal AutoRegressive Integrated Moving Average model for approximation components
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')


class SARIMAModel:
    """
    SARIMA model for time series forecasting
    
    Best suited for approximation components (low-frequency trends)
    from wavelet decomposition
    """
    
    def __init__(self, order: Tuple[int, int, int] = (2, 1, 2),
                 seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 12)):
        """
        Initialize SARIMA model
        
        Args:
            order: (p, d, q) - ARIMA order
                p: AutoRegressive order
                d: Differencing order
                q: Moving Average order
            seasonal_order: (P, D, Q, s) - Seasonal order
                P: Seasonal AR order
                D: Seasonal differencing
                Q: Seasonal MA order
                s: Seasonal period (e.g., 12 for monthly data)
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self.fitted_model = None
    
    def check_stationarity(self, data: np.ndarray, significance: float = 0.05) -> bool:
        """
        Check if time series is stationary using Augmented Dickey-Fuller test
        
        Args:
            data: Time series data
            significance: Significance level (default: 0.05)
        
        Returns:
            True if stationary, False otherwise
        """
        result = adfuller(data)
        p_value = result[1]
        
        is_stationary = p_value < significance
        
        return is_stationary
    
    def auto_find_order(self, data: np.ndarray, 
                       max_p: int = 3, max_d: int = 2, max_q: int = 3) -> Tuple[int, int, int]:
        """
        Automatically find optimal ARIMA order using AIC
        
        Args:
            data: Time series data
            max_p, max_d, max_q: Maximum values to try
        
        Returns:
            Optimal (p, d, q) order
        """
        best_aic = np.inf
        best_order = (1, 1, 1)
        
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        model = SARIMAX(data, order=(p, d, q))
                        fitted = model.fit(disp=False)
                        
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        return best_order
    
    def fit(self, data: np.ndarray, auto_order: bool = False):
        """
        Fit SARIMA model to data
        
        Args:
            data: Training time series
            auto_order: Whether to automatically find optimal order
        """
        if auto_order:
            self.order = self.auto_find_order(data)
            print(f"Auto-selected ARIMA order: {self.order}")
        
        self.model = SARIMAX(
            data,
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        self.fitted_model = self.model.fit(disp=False, maxiter=200)
        
        print(f"SARIMA model fitted successfully")
        print(f"AIC: {self.fitted_model.aic:.2f}")
        print(f"BIC: {self.fitted_model.bic:.2f}")
    
    def predict(self, steps: int = 1) -> np.ndarray:
        """
        Generate forecasts
        
        Args:
            steps: Number of steps to forecast
        
        Returns:
            Forecasted values
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before prediction")
        
        forecast = self.fitted_model.forecast(steps=steps)
        
        return forecast.values
    
    def predict_with_confidence(self, steps: int = 1, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate forecasts with confidence intervals
        
        Args:
            steps: Number of steps to forecast
            alpha: Significance level (default: 0.05 for 95% CI)
        
        Returns:
            forecasts, lower_bounds, upper_bounds
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted before prediction")
        
        forecast_result = self.fitted_model.get_forecast(steps=steps)
        
        forecasts = forecast_result.predicted_mean.values
        conf_int = forecast_result.conf_int(alpha=alpha)
        
        lower_bounds = conf_int.iloc[:, 0].values
        upper_bounds = conf_int.iloc[:, 1].values
        
        return forecasts, lower_bounds, upper_bounds
    
    def evaluate(self, test_data: np.ndarray) -> dict:
        """
        Evaluate model on test data
        
        Args:
            test_data: Test time series
        
        Returns:
            Dictionary with evaluation metrics
        """
        predictions = self.predict(steps=len(test_data))
        
        # Calculate metrics
        mse = np.mean((test_data - predictions) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(test_data - predictions))
        mape = np.mean(np.abs((test_data - predictions) / test_data)) * 100
        
        return {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'MAPE': mape
        }
    
    def get_summary(self):
        """Get model summary"""
        if self.fitted_model is None:
            raise ValueError("Model must be fitted first")
        
        return self.fitted_model.summary()


# ==========================================
# Utility Functions
# ==========================================

def train_sarima_on_approximation(
    approximation_component: np.ndarray,
    train_ratio: float = 0.8,
    order: Tuple[int, int, int] = (2, 1, 2),
    seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 12),
    auto_order: bool = False
) -> SARIMAModel:
    """
    Train SARIMA model on wavelet approximation component
    
    Args:
        approximation_component: Approximation from wavelet decomposition
        train_ratio: Ratio of training data
        order: ARIMA order
        seasonal_order: Seasonal ARIMA order
        auto_order: Whether to auto-select order
    
    Returns:
        Trained SARIMA model
    """
    # Split data
    split_idx = int(len(approximation_component) * train_ratio)
    train_data = approximation_component[:split_idx]
    
    # Initialize and train model
    model = SARIMAModel(order=order, seasonal_order=seasonal_order)
    model.fit(train_data, auto_order=auto_order)
    
    return model
