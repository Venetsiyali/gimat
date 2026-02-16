"""
Anomaly Detection for Hydrological Data
"""

import numpy as np
from typing import List, Dict, Optional
from sklearn.ensemble import IsolationForest
from scipy import stats


class AnomalyDetector:
    """
    Statistical and ML-based anomaly detection
    """
    
    def __init__(self, method: str = 'statistical'):
        """
        Initialize anomaly detector
        
        Args:
            method: 'statistical', 'isolation_forest', or 'hybrid'
        """
        self.method = method
        
        if method in ['isolation_forest', 'hybrid']:
            self.ml_detector = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            self.ml_trained = False
    
    def detect(self, value: float, historical_data: List[float]) -> Dict:
        """
        Detect if value is anomalous
        
        Args:
            value: Current value
            historical_data: Historical values
        
        Returns:
            Detection result
        """
        if self.method == 'statistical':
            return self._statistical_detection(value, historical_data)
        
        elif self.method == 'isolation_forest':
            return self._ml_detection(value, historical_data)
        
        elif self.method == 'hybrid':
            stat_result = self._statistical_detection(value, historical_data)
            ml_result = self._ml_detection(value, historical_data)
            
            # Combine results
            is_anomaly = stat_result['is_anomaly'] or ml_result['is_anomaly']
            confidence = (stat_result['confidence'] + ml_result['confidence']) / 2
            
            return {
                'is_anomaly': is_anomaly,
                'confidence': confidence,
                'method': 'hybrid',
                'details': {
                    'statistical': stat_result,
                    'ml': ml_result
                }
            }
        
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _statistical_detection(self, value: float, historical_data: List[float]) -> Dict:
        """
        Statistical anomaly detection (Z-score + IQR)
        
        Args:
            value: Current value
            historical_data: Historical values
        
        Returns:
            Detection result
        """
        if len(historical_data) < 3:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'method': 'statistical',
                'reason': 'Insufficient data'
            }
        
        data = np.array(historical_data)
        
        # Z-score method
        mean = np.mean(data)
        std = np.std(data)
        z_score = abs(value - mean) / (std + 1e-6)
        
        z_anomaly = z_score > 3.0
        
        # IQR method
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        iqr_anomaly = value < lower_bound or value > upper_bound
        
        # Combined decision
        is_anomaly = z_anomaly or iqr_anomaly
        
        # Confidence based on both methods
        confidence = 0.0
        if z_anomaly and iqr_anomaly:
            confidence = 0.9
        elif z_anomaly or iqr_anomaly:
            confidence = 0.7
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': float(confidence),
            'method': 'statistical',
            'z_score': float(z_score),
            'iqr_bounds': [float(lower_bound), float(upper_bound)]
        }
    
    def _ml_detection(self, value: float, historical_data: List[float]) -> Dict:
        """
        ML-based anomaly detection (Isolation Forest)
        
        Args:
            value: Current value
            historical_data: Historical values
        
        Returns:
            Detection result
        """
        if len(historical_data) < 10:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'method': 'ml',
                'reason': 'Insufficient training data'
            }
        
        # Train if not trained
        if not self.ml_trained:
            X_train = np.array(historical_data).reshape(-1, 1)
            self.ml_detector.fit(X_train)
            self.ml_trained = True
        
        # Predict
        X_test = np.array([[value]])
        prediction = self.ml_detector.predict(X_test)[0]
        
        # -1 = anomaly, 1 = normal
        is_anomaly = (prediction == -1)
        
        # Anomaly score
        anomaly_score = self.ml_detector.score_samples(X_test)[0]
        confidence = abs(anomaly_score) if is_anomaly else 0.0
        
        return {
            'is_anomaly': bool(is_anomaly),
            'confidence': float(min(confidence, 1.0)),
            'method': 'ml',
            'anomaly_score': float(anomaly_score)
        }


# ==========================================
# Time Series Anomaly Detection
# ==========================================

class TimeSeriesAnomalyDetector:
    """
    Specialized for time series patterns
    """
    
    def __init__(self):
        self.detector = AnomalyDetector(method='hybrid')
    
    def detect_in_series(self,
                        time_series: List[Dict],
                        window_size: int = 24) -> List[Dict]:
        """
        Detect anomalies in time series
        
        Args:
            time_series: List of observations with timestamp and value
            window_size: Rolling window size
        
        Returns:
            List of anomalies with timestamps
        """
        anomalies = []
        
        for i in range(window_size, len(time_series)):
            current = time_series[i]
            historical = [obs['value'] for obs in time_series[i-window_size:i]]
            
            result = self.detector.detect(current['value'], historical)
            
            if result['is_anomaly']:
                anomalies.append({
                    'timestamp': current['timestamp'],
                    'value': current['value'],
                    'confidence': result['confidence'],
                    'details': result
                })
        
        return anomalies
