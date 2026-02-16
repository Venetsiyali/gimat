"""
Physics-Informed Neural Networks (PINN) Loss Functions
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Tuple


class PINNLoss(nn.Module):
    """
    Physics-Informed loss for hydrological models
    Combines data loss with physics-based constraints
    """
    
    def __init__(self, 
                 data_weight: float = 0.7,
                 physics_weight: float = 0.3):
        """
        Initialize PINN loss
        
        Args:
            data_weight: Weight for data fitting loss
            physics_weight: Weight for physics constraint loss
        """
        super().__init__()
        self.data_weight = data_weight
        self.physics_weight = physics_weight
        self.mse_loss = nn.MSELoss()
    
    def forward(self,
               predictions: torch.Tensor,
               targets: torch.Tensor,
               inputs: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict]:
        """
        Compute combined loss
        
        Args:
            predictions: Model predictions
            targets: Ground truth
            inputs: Input features (for physics calculations)
        
        Returns:
            Total loss and loss components dict
        """
        # Data loss (MSE)
        data_loss = self.mse_loss(predictions, targets)
        
        # Physics loss (mass balance)
        physics_loss = self.mass_balance_loss(inputs, predictions)
        
        # Combined loss
        total_loss = (self.data_weight * data_loss + 
                     self.physics_weight * physics_loss)
        
        return total_loss, {
            'data_loss': data_loss.item(),
            'physics_loss': physics_loss.item(),
            'total_loss': total_loss.item()
        }
    
    def mass_balance_loss(self,
                         inputs: Dict[str, torch.Tensor],
                         predictions: torch.Tensor) -> torch.Tensor:
        """
        Mass balance equation violation
        
        Equation: dS/dt = Q_in - Q_out - ET - Infiltration
        
        Args:
            inputs: Input dict with Q_in, ET, infiltration
            predictions: Predicted Q_out (discharge)
        
        Returns:
            Mass balance violation loss
        """
        # Extract components (if available in inputs)
        Q_in = inputs.get('upstream_flow', torch.zeros_like(predictions))
        Q_out = predictions
        ET = inputs.get('evapotranspiration', torch.zeros_like(predictions))
        infiltration = inputs.get('infiltration', torch.zeros_like(predictions))
        
        # Storage change (approximate from consecutive predictions)
        if predictions.shape[0] > 1:
            dS_dt = predictions[1:] - predictions[:-1]
            
            # Mass balance for consecutive time steps
            balance = dS_dt - (Q_in[1:] - Q_out[1:] - ET[1:] - infiltration[1:])
            
            # MSE of balance violation
            balance_loss = torch.mean(balance ** 2)
        else:
            balance_loss = torch.tensor(0.0)
        
        return balance_loss
    
    def continuity_equation_loss(self,
                                 discharge: torch.Tensor,
                                 cross_section_area: torch.Tensor) -> torch.Tensor:
        """
        Continuity equation constraint
        
        Equation: ∂Q/∂x + ∂A/∂t = 0
        
        Args:
            discharge: Discharge predictions
            cross_section_area: Cross-sectional area
        
        Returns:
            Continuity violation loss
        """
        # Spatial derivative ∂Q/∂x (approximate)
        if discharge.shape[0] > 1:
            dQ_dx = discharge[1:] - discharge[:-1]
            dA_dt = cross_section_area[1:] - cross_section_area[:-1]
            
            continuity_violation = dQ_dx + dA_dt
            loss = torch.mean(continuity_violation ** 2)
        else:
            loss = torch.tensor(0.0)
        
        return loss


# ==========================================
# Specialized PINN Models
# ==========================================

class PINNBiLSTM(nn.Module):
    """
    Bi-LSTM with PINN loss
    """
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        
        from models.bilstm_model import BiLSTMModel
        self.lstm = BiLSTMModel(input_size, hidden_size, output_size)
        self.pinn_loss = PINNLoss(data_weight=0.7, physics_weight=0.3)
    
    def forward(self, x):
        return self.lstm(x)
    
    def compute_loss(self, predictions, targets, inputs):
        return self.pinn_loss(predictions, targets, inputs)


class PINNTransformer(nn.Module):
    """
    Transformer with PINN loss
    """
    
    def __init__(self, input_dim: int, d_model: int, nhead: int, num_layers: int):
        super().__init__()
        
        from models.transformer_model import HydroTransformer
        self.transformer = HydroTransformer(input_dim, d_model, nhead, num_layers)
        self.pinn_loss = PINNLoss(data_weight=0.7, physics_weight=0.3)
    
    def forward(self, x):
        return self.transformer(x)
    
    def compute_loss(self, predictions, targets, inputs):
        return self.pinn_loss(predictions, targets, inputs)


# ==========================================
# Training Utilities
# ==========================================

class PINNTrainer:
    """
    Trainer with PINN loss monitoring
    """
    
    def __init__(self, model, learning_rate: float = 0.001):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.loss_history = {
            'data_loss': [],
            'physics_loss': [],
            'total_loss': []
        }
    
    def train_step(self, inputs, targets, physics_inputs):
        """
        Single training step with PINN loss
        
        Args:
            inputs: Model inputs
            targets: Ground truth
            physics_inputs: Dict with physics variables
        
        Returns:
            Loss components
        """
        self.model.train()
        self.optimizer.zero_grad()
        
        # Forward pass
        predictions = self.model(inputs)
        
        # Compute PINN loss
        total_loss, loss_components = self.model.compute_loss(
            predictions, targets, physics_inputs
        )
        
        # Backward pass
        total_loss.backward()
        self.optimizer.step()
        
        # Log losses
        for key in loss_components:
            self.loss_history[key].append(loss_components[key])
        
        return loss_components
    
    def get_loss_history(self) -> Dict:
        """Get training loss history"""
        return self.loss_history
