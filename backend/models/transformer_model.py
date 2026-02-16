"""
GIMAT - Transformer Model  
Transformer with attention mechanism for long-term dependencies
"""

import torch
import torch.nn as nn
import math
from typing import Tuple
import numpy as np


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                            (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        """Add positional encoding to input"""
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class TransformerModel(nn.Module):
    """
    Transformer model for time series forecasting
    
    Uses attention mechanism to capture long-term dependencies
    """
    
    def __init__(self, input_size: int = 1, d_model: int = 64,
                 nhead: int = 4, num_encoder_layers: int = 2,
                 dim_feedforward: int = 256, dropout: float = 0.1,
                 output_size: int = 1):
        """
        Initialize Transformer model
        
        Args:
            input_size: Number of input features
            d_model: Dimension of model (must be divisible by nhead)
            nhead: Number of attention heads
            num_encoder_layers: Number of encoder layers
            dim_feedforward: Dimension of feedforward network
            dropout: Dropout probability
            output_size: Number of output features
        """
        super(TransformerModel, self).__init__()
        
        self.d_model = d_model
        self.input_size = input_size
        
        # Input embedding
        self.input_embedding = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, dropout=dropout)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_encoder_layers
        )
        
        # Output layer
        self.fc_out = nn.Linear(d_model, output_size)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, src):
        """
        Forward pass
        
        Args:
            src: Input tensor [batch_size, seq_len, input_size]
        
        Returns:
            Output tensor [batch_size, output_size]
        """
        # Input embedding
        src = self.input_embedding(src) * math.sqrt(self.d_model)
        
        # Positional encoding
        src = self.pos_encoder(src)
        
        # Transformer encoding
        output = self.transformer_encoder(src)
        
        # Take the last time step
        output = output[:, -1, :]
        
        # Dropout and final layer
        output = self.dropout(output)
        output = self.fc_out(output)
        
        return output


class TransformerTrainer:
    """Trainer for Transformer model"""
    
    def __init__(self, model: TransformerModel, learning_rate: float = 0.0001,
                 device: str = 'cpu'):
        """Initialize trainer"""
        self.model = model
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )
        
        self.train_losses = []
        self.val_losses = []
    
    def train_epoch(self, train_loader) -> float:
        """Train for one epoch"""
        self.model.train()
        epoch_loss = 0.0
        
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(self.device)
            y_batch = y_batch.to(self.device)
            
            self.optimizer.zero_grad()
            predictions = self.model(X_batch)
            loss = self.criterion(predictions, y_batch)
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            epoch_loss += loss.item()
        
        return epoch_loss / len(train_loader)
    
    def validate(self, val_loader) -> float:
        """Validate model"""
        self.model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)
                
                predictions = self.model(X_batch)
                loss = self.criterion(predictions, y_batch)
                val_loss += loss.item()
        
        return val_loss / len(val_loader)
    
    def train(self, train_loader, val_loader, epochs: int = 100,
              patience: int = 10, verbose: bool = True):
        """Train with early stopping"""
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            
            self.scheduler.step(val_loss)
            
            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] - "
                      f"Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.best_model_state = self.model.state_dict()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    if verbose:
                        print(f"Early stopping at epoch {epoch+1}")
                    break
        
        self.model.load_state_dict(self.best_model_state)
        
        if verbose:
            print(f"Training completed. Best validation loss: {best_val_loss:.6f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        self.model.eval()
        
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            predictions = self.model(X_tensor)
            return predictions.cpu().numpy()
    
    def save_model(self, path: str):
        """Save model"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }, path)
    
    def load_model(self, path: str):
        """Load model"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.train_losses = checkpoint['train_losses']
        self.val_losses = checkpoint['val_losses']
