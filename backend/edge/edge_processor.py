"""
Edge Processor - Lightweight Processing on Edge Devices
"""

import numpy as np
import pywt
from typing import Dict, List
from models.preprocessing import WaveletPreprocessor


class EdgeProcessor:
    """
    Lightweight data processing for edge devices (Raspberry Pi, etc.)
    """
    
    def __init__(self, wavelet: str = 'db4'):
        """
        Initialize edge processor
        
        Args:
            wavelet: Wavelet type for denoising
        """
        self.wavelet = wavelet
    
    def process_observation(self, raw_data: Dict) -> Dict:
        """
        Process raw sensor data on edge
        
        Pipeline:
        1. Denoise (wavelet)
        2. Outlier removal
        3. Compression
        
        Args:
            raw_data: Raw sensor reading
        
        Returns:
            Processed data
        """
        value = raw_data['value']
        
        # Simple denoising (for single value, use smoothing)
        # In practice, would batch values
        denoised_value = value  # Placeholder
        
        # Outlier check
        is_outlier = self._check_outlier(denoised_value, raw_data.get('recent_values', []))
        
        # Compression (round to reasonable precision)
        compressed_value = round(denoised_value, 2)
        
        processed = {
            'station_id': raw_data['station_id'],
            'timestamp': raw_data['timestamp'],
            'value': compressed_value,
            'raw_value': value,
            'is_outlier': is_outlier,
            'processed_on_edge': True
        }
        
        return processed
    
    def _check_outlier(self, value: float, recent_values: List[float]) -> bool:
        """Quick outlier check"""
        if len(recent_values) < 3:
            return False
        
        mean = np.mean(recent_values)
        std = np.std(recent_values)
        
        z_score = abs(value - mean) / (std + 1e-6)
        
        return z_score > 3.0
    
    def denoise_batch(self, values: List[float]) -> List[float]:
        """
        Wavelet denoising for batch of values
        
        Args:
            values: Time series values
        
        Returns:
            Denoised values
        """
        if len(values) < 4:
            return values
        
        # Wavelet denoising
        coeffs = pywt.wavedec(values, self.wavelet, level=2)
        
        # Threshold detail coefficients
        threshold = np.std(coeffs[-1]) * np.sqrt(2 * np.log(len(values)))
        coeffs[1:] = [pywt.threshold(c, threshold, mode='soft') for c in coeffs[1:]]
        
        # Reconstruct
        denoised = pywt.waverec(coeffs, self.wavelet)
        
        return denoised[:len(values)]
    
    def compress_for_transmission(self, data: Dict) -> bytes:
        """
        Compress data for efficient transmission
        
        Args:
            data: Data dict
        
        Returns:
            Compressed bytes
        """
        import json
        import zlib
        
        # Convert to JSON
        json_data = json.dumps(data)
        
        # Compress
        compressed = zlib.compress(json_data.encode('utf-8'))
        
        return compressed


# ==========================================
# Buffer Manager
# ==========================================

class DataBuffer:
    """
    Buffer data on edge device before transmission
    """
    
    def __init__(self, max_size: int = 100, flush_interval: int = 60):
        """
        Initialize buffer
        
        Args:
            max_size: Maximum buffer size
            flush_interval: Flush interval in seconds
        """
        self.buffer = []
        self.max_size = max_size
        self.flush_interval = flush_interval
    
    def add(self, data: Dict):
        """Add data to buffer"""
        self.buffer.append(data)
        
        # Auto-flush if full
        if len(self.buffer) >= self.max_size:
            self.flush()
    
    def flush(self) -> List[Dict]:
        """Flush buffer and return data"""
        data = self.buffer.copy()
        self.buffer.clear()
        return data
    
    def get_size(self) -> int:
        """Get current buffer size"""
        return len(self.buffer)
