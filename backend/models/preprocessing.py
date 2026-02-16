"""
GIMAT - Preprocessing Module
Wavelet decomposition and time series preprocessing
"""

import numpy as np
import pywt
from typing import Tuple, List, Dict
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class WaveletPreprocessor:
    """
    Wavelet decomposition for time series
    
    Uses Discrete Wavelet Transform (DWT) or Maximal Overlap DWT (MODWT)
    to decompose time series into approximation and detail components
    """
    
    def __init__(self, wavelet: str = 'db4', level: int = 3, mode: str = 'symmetric'):
        """
        Initialize wavelet preprocessor
        
        Args:
            wavelet: Wavelet type (db4, haar, sym4, etc.)
            level: Decomposition level
            mode: Signal extension mode
        """
        self.wavelet = wavelet
        self.level = level
        self.mode = mode
        self.scaler = MinMaxScaler(feature_range=(0, 1))
    
    def decompose(self, signal: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Decompose signal using DWT
        
        Args:
            signal: Input time series (1D array)
        
        Returns:
            Dictionary with 'approximation' and 'details' components
        """
        # Perform DWT decomposition
        coeffs = pywt.wavedec(signal, self.wavelet, level=self.level, mode=self.mode)
        
        # coeffs[0] = approximation (low-frequency trend)
        # coeffs[1:] = details (high-frequency fluctuations)
        
        return {
            'approximation': coeffs[0],
            'details': coeffs[1:],  # List of detail coefficients
            'level': self.level,
            'wavelet': self.wavelet
        }
    
    def reconstruct(self, approximation: np.ndarray, details: List[np.ndarray]) -> np.ndarray:
        """
        Reconstruct signal from wavelet coefficients
        
        Args:
            approximation: Approximation coefficients
            details: List of detail coefficients
        
        Returns:
            Reconstructed signal
        """
        coeffs = [approximation] + list(details)
        reconstructed = pywt.waverec(coeffs, self.wavelet, mode=self.mode)
        
        return reconstructed
    
    def reconstruct_component(self, approximation: np.ndarray, details: List[np.ndarray], 
                            component_idx: int = None) -> np.ndarray:
        """
        Reconstruct specific component
        
        Args:
            approximation: Approximation coefficients
            details: Detail coefficients
            component_idx: If None, reconstruct approximation; otherwise reconstruct detail[component_idx]
        
        Returns:
            Reconstructed component signal
        """
        if component_idx is None:
            # Reconstruct approximation only
            coeffs = [approximation] + [np.zeros_like(d) for d in details]
        else:
            # Reconstruct specific detail level
            coeffs = [np.zeros_like(approximation)]
            for i, d in enumerate(details):
                if i == component_idx:
                    coeffs.append(d)
                else:
                    coeffs.append(np.zeros_like(d))
        
        reconstructed = pywt.waverec(coeffs, self.wavelet, mode=self.mode)
        return reconstructed
    
    def normalize(self, data: np.ndarray) -> np.ndarray:
        """Normalize data using MinMaxScaler"""
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        normalized = self.scaler.fit_transform(data)
        return normalized.flatten() if data.shape[1] == 1 else normalized
    
    def denormalize(self, data: np.ndarray) -> np.ndarray:
        """Inverse transform normalized data"""
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        denormalized = self.scaler.inverse_transform(data)
        return denormalized.flatten() if data.shape[1] == 1 else denormalized


class TimeSeriesPreprocessor:
    """
    General time series preprocessing utilities
    """
    
    @staticmethod
    def fill_missing_values(data: pd.DataFrame, method: str = 'linear') -> pd.DataFrame:
        """
        Fill missing values in time series
        
        Args:
            data: DataFrame with time series
            method: Interpolation method ('linear', 'polynomial', 'spline', etc.)
        
        Returns:
            DataFrame with filled values
        """
        return data.interpolate(method=method, limit_direction='both')
    
    @staticmethod
    def detect_outliers(data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """
        Detect outliers using Z-score method
        
        Args:
            data: Input array
            threshold: Z-score threshold (default: 3.0)
        
        Returns:
            Boolean mask where True indicates outlier
        """
        z_scores = np.abs((data - np.mean(data)) / np.std(data))
        return z_scores > threshold
    
    @staticmethod
    def remove_outliers(data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """
        Remove outliers and replace with interpolated values
        
        Args:
            data: Input array
            threshold: Z-score threshold
        
        Returns:
            Data with outliers replaced
        """
        outlier_mask = TimeSeriesPreprocessor.detect_outliers(data, threshold)
        cleaned_data = data.copy()
        
        # Replace outliers with NaN and interpolate
        cleaned_data[outlier_mask] = np.nan
        cleaned_series = pd.Series(cleaned_data).interpolate(method='linear', limit_direction='both')
        
        return cleaned_series.values
    
    @staticmethod
    def create_sequences(data: np.ndarray, lookback: int, forecast_horizon: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create input-output sequences for supervised learning
        
        Args:
            data: Time series data
            lookback: Number of past timesteps to use as input
            forecast_horizon: Number of future timesteps to predict
        
        Returns:
            X (input sequences), y (output sequences)
        """
        X, y = [], []
        
        for i in range(len(data) - lookback - forecast_horizon + 1):
            X.append(data[i:i + lookback])
            y.append(data[i + lookback:i + lookback + forecast_horizon])
        
        return np.array(X), np.array(y)
    
    @staticmethod
    def train_test_split_timeseries(data: np.ndarray, train_ratio: float = 0.8) -> Tuple[np.ndarray, np.ndarray]:
        """
        Split time series into train and test sets (chronologically)
        
        Args:
            data: Time series data
            train_ratio: Ratio of training data
        
        Returns:
            train_data, test_data
        """
        split_idx = int(len(data) * train_ratio)
        return data[:split_idx], data[split_idx:]
    
    @staticmethod
    def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
        """Calculate basic statistics of time series"""
        return {
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'median': float(np.median(data)),
            'q25': float(np.percentile(data, 25)),
            'q75': float(np.percentile(data, 75))
        }


# ==========================================
# Utility Functions
# ==========================================

def preprocess_hydrological_data(
    data: pd.DataFrame,
    target_column: str = 'discharge',
    wavelet: str = 'db4',
    level: int = 3,
    fill_missing: bool = True,
    remove_outliers: bool = True
) -> Dict:
    """
    Complete preprocessing pipeline for hydrological data
    
    Args:
        data: DataFrame with hydrological observations
        target_column: Column to decompose
        wavelet: Wavelet type
        level: Decomposition level
        fill_missing: Whether to fill missing values
        remove_outliers: Whether to remove outliers
    
    Returns:
        Dictionary with preprocessed data and wavelet components
    """
    # Extract target series
    series = data[target_column].values
    
    # Fill missing values
    if fill_missing:
        series_df = pd.DataFrame({target_column: series})
        series_df = TimeSeriesPreprocessor.fill_missing_values(series_df)
        series = series_df[target_column].values
    
    # Remove outliers
    if remove_outliers:
        series = TimeSeriesPreprocessor.remove_outliers(series)
    
    # Wavelet decomposition
    wavelet_proc = WaveletPreprocessor(wavelet=wavelet, level=level)
    decomposition = wavelet_proc.decompose(series)
    
    # Normalize
    normalized_series = wavelet_proc.normalize(series)
    
    return {
        'original_series': series,
        'normalized_series': normalized_series,
        'wavelet_decomposition': decomposition,
        'wavelet_preprocessor': wavelet_proc,
        'statistics': TimeSeriesPreprocessor.calculate_statistics(series)
    }
