"""
GIMAT - Graph Neural Network Model
Spatial-topological modeling using river network graph
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool
from torch_geometric.data import Data, DataLoader
import numpy as np
from typing import List, Tuple, Optional


class HydrologicalGNN(nn.Module):
    """
    Graph Neural Network for hydrological modeling
    
    Models spatial dependencies in river networks using graph structure
    """
    
    def __init__(self, input_features: int = 5, hidden_dim: int = 64,
                 output_dim: int = 1, num_layers: int = 3,
                 dropout: float = 0.2, conv_type: str = 'GCN'):
        """
        Initialize GNN model
        
        Args:
            input_features: Number of node features (e.g., discharge, water_level, precipitation, etc.)
            hidden_dim: Hidden dimension size
            output_dim: Output dimension (e.g., 1 for discharge prediction)
            num_layers: Number of GNN layers
            dropout: Dropout probability
            conv_type: Type of convolution ('GCN' or 'GAT')
        """
        super(HydrologicalGNN, self).__init__()
        
        self.input_features = input_features
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.conv_type = conv_type
        
        # Input layer
        if conv_type == 'GCN':
            self.convs = nn.ModuleList([
                GCNConv(input_features if i == 0 else hidden_dim, hidden_dim)
                for i in range(num_layers)
            ])
        elif conv_type == 'GAT':
            self.convs = nn.ModuleList([
                GATConv(input_features if i == 0 else hidden_dim, hidden_dim, heads=1)
                for i in range(num_layers)
            ])
        else:
            raise ValueError(f"Unknown convolution type: {conv_type}")
        
        # Batch normalization
        self.batch_norms = nn.ModuleList([
            nn.BatchNorm1d(hidden_dim) for _ in range(num_layers)
        ])
        
        # Output layer
        self.fc_out = nn.Linear(hidden_dim, output_dim)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, edge_index, batch=None):
        """
        Forward pass
        
        Args:
            x: Node feature matrix [num_nodes, input_features]
            edge_index: Graph connectivity [2, num_edges]
            batch: Batch vector (for batched graphs) [num_nodes]
        
        Returns:
            Node predictions [num_nodes, output_dim]
        """
        # Apply GNN layers
        for i, (conv, bn) in enumerate(zip(self.convs, self.batch_norms)):
            x = conv(x, edge_index)
            x = bn(x)
            x = F.relu(x)
            x = self.dropout(x)
        
        # Output layer
        x = self.fc_out(x)
        
        return x


class TemporalGNN(nn.Module):
    """
    Temporal Graph Neural Network combining GNN with LSTM
    
    Captures both spatial (graph) and temporal dependencies
    """
    
    def __init__(self, input_features: int = 5, hidden_dim: int = 64,
                 output_dim: int = 1, gnn_layers: int = 2,
                 lstm_layers: int = 1, dropout: float = 0.2):
        """
        Initialize Temporal GNN
        
        Args:
            input_features: Number of node features
            hidden_dim: Hidden dimension
            output_dim: Output dimension
            gnn_layers: Number of GNN layers
            lstm_layers: Number of LSTM layers
            dropout: Dropout probability
        """
        super(TemporalGNN, self).__init__()
        
        # GNN for spatial features
        self.gnn_convs = nn.ModuleList([
            GCNConv(input_features if i == 0 else hidden_dim, hidden_dim)
            for i in range(gnn_layers)
        ])
        
        # LSTM for temporal features
        self.lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=lstm_layers,
            batch_first=True,
            dropout=dropout if lstm_layers > 1 else 0
        )
        
        # Output layer
        self.fc_out = nn.Linear(hidden_dim, output_dim)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x_sequence, edge_index_sequence):
        """
        Forward pass for temporal graphs
        
        Args:
            x_sequence: Sequence of node features [batch, seq_len, num_nodes, features]
            edge_index_sequence: Sequence of graph structures [seq_len, 2, num_edges]
        
        Returns:
            Predictions [batch, num_nodes, output_dim]
        """
        batch_size, seq_len, num_nodes, _ = x_sequence.shape
        
        # Process each timestep with GNN
        gnn_outputs = []
        for t in range(seq_len):
            x_t = x_sequence[:, t, :, :]  # [batch, num_nodes, features]
            edge_index_t = edge_index_sequence[t]
            
            # Flatten batch dimension for GNN processing
            x_t_flat = x_t.reshape(-1, x_t.size(-1))
            
            # Apply GNN layers
            for conv in self.gnn_convs:
                x_t_flat = F.relu(conv(x_t_flat, edge_index_t))
            
            # Reshape back
            x_t = x_t_flat.reshape(batch_size, num_nodes, -1)
            gnn_outputs.append(x_t)
        
        # Stack temporal dimension: [batch, seq_len, num_nodes, hidden_dim]
        gnn_sequence = torch.stack(gnn_outputs, dim=1)
        
        # Process each node separately through LSTM
        outputs = []
        for node_idx in range(num_nodes):
            node_sequence = gnn_sequence[:, :, node_idx, :]  # [batch, seq_len, hidden_dim]
            lstm_out, _ = self.lstm(node_sequence)
            last_output = lstm_out[:, -1, :]  # [batch, hidden_dim]
            outputs.append(last_output)
        
        # Stack node outputs: [batch, num_nodes, hidden_dim]
        node_outputs = torch.stack(outputs, dim=1)
        
        # Final prediction
        node_outputs = self.dropout(node_outputs)
        predictions = self.fc_out(node_outputs)
        
        return predictions


class GNNTrainer:
    """Trainer for GNN models"""
    
    def __init__(self, model, learning_rate: float = 0.001, device: str = 'cpu'):
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
    
    def train_epoch(self, data_list: List[Data]) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        for data in data_list:
            data = data.to(self.device)
            
            self.optimizer.zero_grad()
            predictions = self.model(data.x, data.edge_index, data.batch)
            loss = self.criterion(predictions, data.y)
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(data_list)
    
    def validate(self, data_list: List[Data]) -> float:
        """Validate model"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for data in data_list:
                data = data.to(self.device)
                predictions = self.model(data.x, data.edge_index, data.batch)
                loss = self.criterion(predictions, data.y)
                total_loss += loss.item()
        
        return total_loss / len(data_list)
    
    def train(self, train_data_list, val_data_list, epochs: int = 100,
              patience: int = 10, verbose: bool = True):
        """Train with early stopping"""
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_data_list)
            val_loss = self.validate(val_data_list)
            
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
    
    def predict(self, data: Data) -> np.ndarray:
        """Make predictions"""
        self.model.eval()
        
        with torch.no_grad():
            data = data.to(self.device)
            predictions = self.model(data.x, data.edge_index, data.batch)
            return predictions.cpu().numpy()


# ==========================================
# Utility Functions
# ==========================================

def create_river_network_graph(
    node_features: np.ndarray,
    edge_list: List[Tuple[int, int]],
    targets: Optional[np.ndarray] = None
) -> Data:
    """
    Create PyTorch Geometric Data object for river network
    
    Args:
        node_features: Node feature matrix [num_nodes, num_features]
        edge_list: List of edges [(source, target), ...]
        targets: Target values [num_nodes, target_dim]
    
    Returns:
        PyTorch Geometric Data object
    """
    # Convert to tensors
    x = torch.FloatTensor(node_features)
    edge_index = torch.LongTensor(edge_list).t().contiguous()
    
    if targets is not None:
        y = torch.FloatTensor(targets)
        return Data(x=x, edge_index=edge_index, y=y)
    else:
        return Data(x=x, edge_index=edge_index)
