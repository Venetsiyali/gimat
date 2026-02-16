"""
GIMAT - Bi-LSTM Model
Bidirectional Long Short-Term Memory network for detail components
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Optional
from torch.utils.data import DataLoader, TensorDataset


class BiLSTMModel(nn.Module):
    """
    Bidirectional LSTM neural network
    
    Suitable for detail components (high-frequency fluctuations)
    from wavelet decomposition
    """
    
    def __init__(self, input_size: int = 1, hidden_size: int = 64,
                 num_layers: int = 2, output_size: int = 1,
                 dropout: float = 0.2):
        """
        Initialize Bi-LSTM model
        
        Args:
            input_size: Number of input features
            hidden_size: Number of hidden units in LSTM
            num_layers: Number of LSTM layers
            output_size: Number of output features
            dropout: Dropout probability
        """
        super(BiLSTMModel, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        
        # Bidirectional LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Fully connected layer (hidden_size * 2 because bidirectional)
        self.fc = nn.Linear(hidden_size * 2, output_size)
        
        # Dropout layer
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input tensor [batch_size, sequence_length, input_size]
        
        Returns:
            Output tensor [batch_size, output_size]
        """
        # LSTM forward pass
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Take the output from the last time step
        # lstm_out shape: [batch_size, seq_len, hidden_size * 2]
        last_output = lstm_out[:, -1, :]
        
        # Apply dropout
        dropped = self.dropout(last_output)
        
        # Fully connected layer
        output = self.fc(dropped)
        
        return output


class BiLSTMTrainer:
    """Trainer for Bi-LSTM model"""
    
    def __init__(self, model: BiLSTMModel, learning_rate: float = 0.001,
                 device: str = 'cpu'):
        """
        Initialize trainer
        
        Args:
            model: Bi-LSTM model
            learning_rate: Learning rate for optimizer
            device: Device to train on ('cpu' or 'cuda')
        """
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
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        epoch_loss = 0.0
        
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(self.device)
            y_batch = y_batch.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            predictions = self.model(X_batch)
            loss = self.criterion(predictions, y_batch)
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            epoch_loss += loss.item()
        
        return epoch_loss / len(train_loader)
    
    def validate(self, val_loader: DataLoader) -> float:
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
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader,
              epochs: int = 100, patience: int = 10, verbose: bool = True):
        """
        Train model with early stopping
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Maximum number of epochs
            patience: Early stopping patience
            verbose: Whether to print progress
        """
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] - "
                      f"Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                self.best_model_state = self.model.state_dict()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    if verbose:
                        print(f"Early stopping at epoch {epoch+1}")
                    break
        
        # Load best model
        self.model.load_state_dict(self.best_model_state)
        
        if verbose:
            print(f"Training completed. Best validation loss: {best_val_loss:.6f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input data [num_samples, sequence_length, input_size]
        
        Returns:
            Predictions
        """
        self.model.eval()
        
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            predictions = self.model(X_tensor)
            return predictions.cpu().numpy()
    
    def save_model(self, path: str):
        """Save model to file"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }, path)
    
    def load_model(self, path: str):
        """Load model from file"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.train_losses = checkpoint['train_losses']
        self.val_losses = checkpoint['val_losses']


# ==========================================
# Utility Functions
# ==========================================

def prepare_lstm_data(data: np.ndarray, lookback: int = 10,
                     forecast_horizon: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare data for LSTM training
    
    Args:
        data: Time series data
        lookback: Number of past timesteps
        forecast_horizon: Number of future timesteps
    
    Returns:
        X, y arrays
    """
    X, y = [], []
    
    for i in range(len(data) - lookback - forecast_horizon + 1):
        X.append(data[i:i + lookback])
        y.append(data[i + lookback:i + lookback + forecast_horizon])
    
    X = np.array(X).reshape(-1, lookback, 1)
    y = np.array(y)
    
    return X, y


def create_dataloaders(X_train: np.ndarray, y_train: np.ndarray,
                      X_val: np.ndarray, y_val: np.ndarray,
                      batch_size: int = 32) -> Tuple[DataLoader, DataLoader]:
    """Create PyTorch DataLoaders"""
    
    train_dataset = TensorDataset(
        torch.FloatTensor(X_train),
        torch.FloatTensor(y_train)
    )
    val_dataset = TensorDataset(
        torch.FloatTensor(X_val),
        torch.FloatTensor(y_val)
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader
