"""
Data Confidence Scorer
Combines temporal, spatial, satellite, and historical validation
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class ConfidenceScorer:
    """
    Multi-dimensional confidence scoring for hydrological data
    """
    
    def __init__(self,
                 temporal_weight: float = 0.3,
                 spatial_weight: float = 0.25,
                 satellite_weight: float = 0.25,
                 historical_weight: float = 0.2):
        """
        Initialize confidence scorer
        
        Args:
            temporal_weight: Weight for temporal consistency
            spatial_weight: Weight for spatial consistency
            satellite_weight: Weight for satellite validation
            historical_weight: Weight for historical norm deviation
        """
        self.weights = {
            'temporal': temporal_weight,
            'spatial': spatial_weight,
            'satellite': satellite_weight,
            'historical': historical_weight
        }
    
    def score(self,
             observation: Dict,
             historical_data: List[Dict],
             neighbor_observations: List[Dict],
             satellite_data: Optional[Dict] = None) -> Dict:
        """
        Calculate comprehensive confidence score
        
        Args:
            observation: Current observation dict
            historical_data: Historical observations for this location
            neighbor_observations: Observations from nearby stations
            satellite_data: Satellite validation data
        
        Returns:
            Confidence score and components
        """
        # Component scores
        temporal_score = self.temporal_consistency(observation, historical_data)
        spatial_score = self.spatial_consistency(observation, neighbor_observations)
        satellite_score = self.satellite_validation(observation, satellite_data)
        historical_score = self.historical_norm_check(observation, historical_data)
        
        # Weighted combination
        confidence = (
            self.weights['temporal'] * temporal_score +
            self.weights['spatial'] * spatial_score +
            self.weights['satellite'] * satellite_score +
            self.weights['historical'] * historical_score
        )
        
        return {
            'confidence_score': float(confidence),
            'components': {
                'temporal_consistency': float(temporal_score),
                'spatial_consistency': float(spatial_score),
                'satellite_validation': float(satellite_score),
                'historical_norm': float(historical_score)
            },
            'is_reliable': confidence >= 0.7,
            'quality_level': self._quality_level(confidence)
        }
    
    def temporal_consistency(self,
                           observation: Dict,
                           historical_data: List[Dict]) -> float:
        """
        Check temporal consistency (smooth evolution)
        
        Args:
            observation: Current observation
            historical_data: Past observations
        
        Returns:
            Temporal consistency score (0-1)
        """
        if not historical_data or len(historical_data) < 2:
            return 0.5  # Neutral score
        
        # Get recent values
        recent_values = [obs['discharge'] for obs in historical_data[-5:]]
        current_value = observation['discharge']
        
        # Calculate expected range (mean ± 2*std)
        mean = np.mean(recent_values)
        std = np.std(recent_values)
        
        # Z-score
        z_score = abs(current_value - mean) / (std + 1e-6)
        
        # Score: 1.0 if within 2 std, decreases with distance
        score = max(0.0, 1.0 - z_score / 4.0)
        
        return score
    
    def spatial_consistency(self,
                          observation: Dict,
                          neighbor_observations: List[Dict]) -> float:
        """
        Check consistency with nearby stations
        
        Args:
            observation: Current observation
            neighbor_observations: Observations from neighbors
        
        Returns:
            Spatial consistency score (0-1)
        """
        if not neighbor_observations:
            return 0.5  # Neutral
        
        current_discharge = observation['discharge']
        neighbor_discharges = [obs['discharge'] for obs in neighbor_observations]
        
        # Expected value (weighted average by distance)
        # For simplicity, use simple mean
        expected = np.mean(neighbor_discharges)
        std = np.std(neighbor_discharges)
        
        # Deviation score
        deviation = abs(current_discharge - expected) / (std + 1e-6)
        score = max(0.0, 1.0 - deviation / 3.0)
        
        return score
    
    def satellite_validation(self,
                           observation: Dict,
                           satellite_data: Optional[Dict]) -> float:
        """
        Validate with satellite observations (e.g., Sentinel-2 water extent)
        
        Args:
            observation: Current observation
            satellite_data: Satellite-derived data
        
        Returns:
            Satellite validation score (0-1)
        """
        if not satellite_data:
            return 0.7  # Default good score if no satellite data
        
        # Compare water level with satellite-derived water extent
        # (placeholder logic - real implementation would use actual satellite processing)
        
        water_level = observation.get('water_level', 0)
        satellite_extent = satellite_data.get('water_extent_index', 0.5)
        
        # Correlation check (simplified)
        correlation = 1.0 - abs(water_level / 10.0 - satellite_extent)
        score = max(0.0, min(1.0, correlation))
        
        return score
    
    def historical_norm_check(self,
                            observation: Dict,
                            historical_data: List[Dict]) -> float:
        """
        Check against historical norms for this time of year
        
        Args:
            observation: Current observation
            historical_data: Historical observations
        
        Returns:
            Historical norm score (0-1)
        """
        if not historical_data:
            return 0.5
        
        # Get month/season
        obs_date = observation.get('timestamp', datetime.now())
        if isinstance(obs_date, str):
            obs_date = datetime.fromisoformat(obs_date)
        
        month = obs_date.month
        
        # Filter historical data for same month
        monthly_values = [
            obs['discharge'] for obs in historical_data
            if datetime.fromisoformat(str(obs['timestamp'])).month == month
        ]
        
        if not monthly_values:
            return 0.5
        
        # Calculate percentile
        current_value = observation['discharge']
        percentile = sum(v <= current_value for v in monthly_values) / len(monthly_values)
        
        # Score: high if within 10-90 percentile, lower at extremes
        if 0.1 <= percentile <= 0.9:
            score = 1.0
        elif 0.05 <= percentile <= 0.95:
            score = 0.8
        else:
            score = 0.5
        
        return score
    
    def _quality_level(self, confidence: float) -> str:
        """Map confidence to quality level"""
        if confidence >= 0.9:
            return "excellent"
        elif confidence >= 0.7:
            return "good"
        elif confidence >= 0.5:
            return "acceptable"
        else:
            return "poor"


# ==========================================
# Real-time Confidence Monitoring
# ==========================================

class ConfidenceMonitor:
    """
    Real-time monitoring of data quality
    """
    
    def __init__(self, scorer: ConfidenceScorer):
        self.scorer = scorer
        self.alerts = []
    
    def monitor(self, observation: Dict, context: Dict) -> Dict:
        """
        Monitor observation and generate alerts if needed
        
        Args:
            observation: Current observation
            context: Historical and spatial context
        
        Returns:
            Monitoring result with alerts
        """
        # Calculate confidence
        confidence_result = self.scorer.score(
            observation,
            context.get('historical_data', []),
            context.get('neighbor_observations', []),
            context.get('satellite_data')
        )
        
        #Generate alerts for low confidence
        if confidence_result['confidence_score'] < 0.5:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'station_id': observation.get('station_id'),
                'confidence': confidence_result['confidence_score'],
                'severity': 'high',
                'message': f"Low confidence ({confidence_result['confidence_score']:.2f}) detected"
            }
            self.alerts.append(alert)
            confidence_result['alert'] = alert
        
        return confidence_result
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get alerts from last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff
        ]
        
        return recent
