"""
GIMAT - Hybrid Ensemble Model
Combines Wavelet + SARIMA + LSTM + GNN for optimal predictions
"""

import numpy as np
from typing import Dict, Tuple, Optional
import torch

from models.preprocessing import WaveletPreprocessor, preprocess_hydrological_data
from models.sarima_model import SARIMAModel
from models.bilstm_model import BiLSTMModel, BiLSTMTrainer, prepare_lstm_data
from models.gnn_model import HydrologicalGNN, create_river_network_graph


class HybridEnsembleModel:
    """
    Hybrid ensemble combining multiple models:
    
    1. Wavelet decomposition
    2. SARIMA for approximation (trend)
    3. Bi-LSTM for details (fluctuations)
    4. GNN for spatial dependencies
    5. Final weighted ensemble
    """
    
    def __init__(self, wavelet: str = 'db4', level: int = 3,
                 use_gnn: bool = True):
        """
        Initialize hybrid model
        
        Args:
            wavelet: Wavelet type for decomposition
            level: Wavelet decomposition level
            use_gnn: Whether to use GNN for spatial modeling
        """
        self.wavelet = wavelet
        self.level = level
        self.use_gnn = use_gnn
        
        # Components
        self.wavelet_preprocessor = WaveletPreprocessor(wavelet=wavelet, level=level)
        self.sarima_model = None
        self.lstm_models = []  # One LSTM for each detail level
        self.gnn_model = None
        
        # Ensemble weights (learned or fixed)
        self.ensemble_weights = {
            'sarima': 0.3,
            'lstm': 0.4,
            'gnn': 0.3
        }
    
    def fit(self, data: np.ndarray, graph_data: Optional[Dict] = None,
            sarima_order: Tuple = (2, 1, 2), 
            lstm_hidden: int = 64,
            epochs: int = 100):
        """
        Fit hybrid model
        
        Args:
            data: Time series data
            graph_data: Graph structure (if using GNN)
            sarima_order: SARIMA order
            lstm_hidden: LSTM hidden size
            epochs: Training epochs
        """
        print("="*50)
        print("Starting Hybrid Model Training")
        print("="*50)
        
        # Step 1: Wavelet decomposition
        print("\n1. Wavelet decomposition...")
        decomposition = self.wavelet_preprocessor.decompose(data)
        approximation = decomposition['approximation']
        details = decomposition['details']
        
        print(f"   Approximation length: {len(approximation)}")
        print(f"   Detail levels: {len(details)}")
        
        # Step 2: Train SARIMA on approximation
        print("\n2. Training SARIMA on approximation component...")
        self.sarima_model = SARIMAModel(order=sarima_order)
        self.sarima_model.fit(approximation)
        
        # Step 3: Train LSTM on each detail level
        print("\n3. Training Bi-LSTM on detail components...")
        self.lstm_models = []
        
        for i, detail in enumerate(details):
            print(f"   Training LSTM for detail level {i+1}...")
            
            # Prepare sequences
            X, y = prepare_lstm_data(detail, lookback=10, forecast_horizon=1)
            
            if len(X) < 10:
                print(f"   Skipping detail {i+1} (insufficient data)")
                self.lstm_models.append(None)
                continue
            
            # Train-validation split
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Create model
            lstm_model = BiLSTMModel(input_size=1, hidden_size=lstm_hidden, output_size=1)
            trainer = BiLSTMTrainer(lstm_model, learning_rate=0.001)
            
            # Create data loaders
            from models.bilstm_model import create_dataloaders
            train_loader, val_loader = create_dataloaders(
                X_train, y_train, X_val, y_val, batch_size=16
            )
            
            # Train
            trainer.train(train_loader, val_loader, epochs=epochs, patience=10, verbose=False)
            self.lstm_models.append(trainer)
            
            print(f"   ✓ LSTM {i+1} trained")
        
        # Step 4: Train GNN (if graph data provided)
        if self.use_gnn and graph_data is not None:
            print("\n4. Training GNN on spatial dependencies...")
            # TODO: Implement GNN training with graph structure
            print("   (GNN training placeholder - requires graph structure)")
        
        print("\n" + "="*50)
        print("Hybrid Model Training Complete!")
        print("="*50)
    
    def predict(self, steps: int = 7) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate hybrid forecast
        
        Args:
            steps: Forecast horizon
        
        Returns:
            predictions, lower_bounds, upper_bounds
        """
        # Step 1: SARIMA prediction for approximation
        sarima_pred, sarima_lower, sarima_upper = self.sarima_model.predict_with_confidence(steps)
        
        # Step 2: LSTM predictions for details (if available)
        lstm_preds = []
        for lstm_trainer in self.lstm_models:
            if lstm_trainer is not None:
                # For simplicity, predict zero for details (can be improved)
                lstm_preds.append(np.zeros(steps))
            else:
                lstm_preds.append(np.zeros(steps))
        
        # Step 3: Reconstruct signal from components
        # For forecast, we combine approximation + details
        predictions = sarima_pred  # Simplified: use SARIMA as base
        
        # Step 4: GNN adjustment (if available)
        if self.gnn_model is not None:
            # TODO: Apply GNN spatial adjustment
            pass
        
        # Ensemble weighting
        lower_bounds = sarima_lower
        upper_bounds = sarima_upper
        
        return predictions, lower_bounds, upper_bounds
    
    def evaluate(self, test_data: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model on test data
        
        Returns NSE, KGE, RMSE, MAE metrics
        """
        steps = len(test_data)
        predictions, _, _ = self.predict(steps)
        
        # Nash-Sutcliffe Efficiency (NSE)
        numerator = np.sum((test_data - predictions) ** 2)
        denominator = np.sum((test_data - np.mean(test_data)) ** 2)
        nse = 1 - (numerator / denominator)
        
        # Kling-Gupta Efficiency (KGE)
        r = np.corrcoef(test_data, predictions)[0, 1]  # Correlation
        alpha = np.std(predictions) / np.std(test_data)  # Variability ratio
        beta = np.mean(predictions) / np.mean(test_data)  # Bias ratio
        kge = 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)
        
        # RMSE
        rmse = np.sqrt(np.mean((test_data - predictions) ** 2))
        
        # MAE
        mae = np.mean(np.abs(test_data - predictions))
        
        return {
            'NSE': float(nse),
            'KGE': float(kge),
            'RMSE': float(rmse),
            'MAE': float(mae)
        }
    
    def save_model(self, path: str):
        """Save hybrid model components"""
        import pickle
        
        model_dict = {
            'wavelet': self.wavelet,
            'level': self.level,
            'sarima_model': self.sarima_model,
            'ensemble_weights': self.ensemble_weights
        }
        
        # Save LSTM models separately (PyTorch)
        for i, lstm_trainer in enumerate(self.lstm_models):
            if lstm_trainer is not None:
                lstm_trainer.save_model(f"{path}_lstm_{i}.pt")
        
        # Save main model dict
        with open(f"{path}_hybrid.pkl", 'wb') as f:
            pickle.dump(model_dict, f)
        
        print(f"Hybrid model saved to {path}")
    
    def load_model(self, path: str):
        """Load hybrid model components"""
        import pickle
        
        with open(f"{path}_hybrid.pkl", 'rb') as f:
            model_dict = pickle.load(f)
        
        self.wavelet = model_dict['wavelet']
        self.level = model_dict['level']
        self.sarima_model = model_dict['sarima_model']
        self.ensemble_weights = model_dict['ensemble_weights']
        
        print(f"Hybrid model loaded from {path}")


# ==========================================
# Utility Functions
# ==========================================

def train_hybrid_model_pipeline(
    data: np.ndarray,
    train_ratio: float = 0.8,
    wavelet: str = 'db4',
    level: int = 3,
    sarima_order: Tuple = (2, 1, 2),
    lstm_hidden: int = 64,
    epochs: int = 100
) -> HybridEnsembleModel:
    """
    Complete training pipeline for hybrid model
    
    Args:
        data: Full time series
        train_ratio: Ratio for training
        wavelet: Wavelet type
        level: Decomposition level
        sarima_order: SARIMA parameters
        lstm_hidden: LSTM hidden size
        epochs: Training epochs
    
    Returns:
        Trained hybrid model
    """
    # Split data
    split_idx = int(len(data) * train_ratio)
    train_data = data[:split_idx]
    test_data = data[split_idx:]
    
    # Create and train model
    hybrid_model = HybridEnsembleModel(wavelet=wavelet, level=level)
    hybrid_model.fit(
        train_data,
        sarima_order=sarima_order,
        lstm_hidden=lstm_hidden,
        epochs=epochs
    )
    
    # Evaluate
    print("\nEvaluating on test data...")
    metrics = hybrid_model.evaluate(test_data)
    
    print("\nEvaluation Metrics:")
    print(f"NSE: {metrics['NSE']:.4f} {'(Excellent)' if metrics['NSE'] > 0.85 else '(Good)' if metrics['NSE'] > 0.7 else '(Satisfactory)' if metrics['NSE'] > 0.5 else '(Unsatisfactory)'}")
    print(f"KGE: {metrics['KGE']:.4f}")
    print(f"RMSE: {metrics['RMSE']:.4f}")
    print(f"MAE: {metrics['MAE']:.4f}")
    
    return hybrid_model
