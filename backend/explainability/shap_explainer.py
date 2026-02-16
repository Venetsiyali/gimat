"""
GIMAT - SHAP Explainer
SHapley Additive exPlanations for model interpretability
"""

import shap
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional
import torch


class SHAPExplainer:
    """
    SHAP (SHapley Additive exPlanations) wrapper for model explanation
    
    Explains which features contribute most to predictions
    """
    
    def __init__(self, model, background_data: np.ndarray, model_type: str = 'pytorch'):
        """
        Initialize SHAP explainer
        
        Args:
            model: Trained model (PyTorch or sklearn)
            background_data: Background dataset for SHAP
            model_type: 'pytorch', 'sklearn', or 'tree'
        """
        self.model = model
        self.model_type = model_type
        self.background_data = background_data
        
        # Initialize appropriate explainer
        if model_type == 'pytorch':
            # Wrap PyTorch model for SHAP
            def model_predict(x):
                self.model.eval()
                with torch.no_grad():
                    x_tensor = torch.FloatTensor(x)
                    predictions = self.model(x_tensor)
                    return predictions.numpy()
            
            self.explainer = shap.KernelExplainer(
                model_predict, 
                background_data
            )
        
        elif model_type == 'sklearn':
            self.explainer = shap.Explainer(model, background_data)
        
        elif model_type == 'tree':
            self.explainer = shap.TreeExplainer(model)
        
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def explain_instance(self, instance: np.ndarray, 
                        feature_names: Optional[List[str]] = None) -> Dict:
        """
        Explain a single prediction instance
        
        Args:
            instance: Input instance to explain
            feature_names: Names of features
        
        Returns:
            Dictionary with SHAP values and explanation
        """
        if instance.ndim == 1:
            instance = instance.reshape(1, -1)
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(instance)
        
        # Get base value (expected value)
        if hasattr(self.explainer, 'expected_value'):
            base_value = self.explainer.expected_value
        else:
            base_value = np.mean(self.background_data)
        
        # If shap_values is a list (multi-class), take first class
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        if shap_values.ndim > 1:
            shap_values = shap_values[0]
        
        # Create feature importance ranking
        if feature_names is None:
            feature_names = [f"Feature_{i}" for i in range(len(shap_values))]
        
        feature_importance = list(zip(feature_names, shap_values))
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return {
            'shap_values': shap_values.tolist(),
            'base_value': float(base_value) if not isinstance(base_value, list) else float(base_value[0]),
            'feature_names': feature_names,
            'feature_importance': feature_importance,
            'explanation': self._generate_text_explanation(feature_importance)
        }
    
    def _generate_text_explanation(self, feature_importance: List[tuple], 
                                   top_n: int = 5) -> str:
        """Generate human-readable explanation"""
        explanation = "Top contributing factors:\n"
        
        for i, (feature, value) in enumerate(feature_importance[:top_n]):
            impact = "increases" if value > 0 else "decreases"
            explanation += f"{i+1}. {feature}: {impact} prediction by {abs(value):.4f}\n"
        
        return explanation
    
    def plot_waterfall(self, instance: np.ndarray, 
                      feature_names: Optional[List[str]] = None,
                      save_path: Optional[str] = None):
        """
        Create waterfall plot showing feature contributions
        
        Args:
            instance: Instance to explain
            feature_names: Feature names
            save_path: Path to save plot
        """
        if instance.ndim == 1:
            instance = instance.reshape(1, -1)
        
        shap_values = self.explainer.shap_values(instance)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        if shap_values.ndim > 1:
            shap_values = shap_values[0]
        
        # Create waterfall plot
        plt.figure(figsize=(10, 6))
        
        base_value = self.explainer.expected_value
        if isinstance(base_value, list):
            base_value = base_value[0]
        
        if feature_names is None:
            feature_names = [f"F{i}" for i in range(len(shap_values))]
        
        # Sort by absolute value
        indices = np.argsort(np.abs(shap_values))[::-1][:10]  # Top 10
        
        cumulative = base_value
        positions = [cumulative]
        
        for idx in indices:
            cumulative += shap_values[idx]
            positions.append(cumulative)
        
        # Plot
        for i, idx in enumerate(indices):
            color = 'green' if shap_values[idx] > 0 else 'red'
            plt.barh(i, shap_values[idx], left=positions[i], color=color, alpha=0.7)
            plt.text(positions[i] + shap_values[idx]/2, i, 
                    feature_names[idx], va='center', ha='center')
        
        plt.xlabel('SHAP Value (impact on model output)')
        plt.ylabel('Features')
        plt.title('SHAP Waterfall Plot - Feature Contributions')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return plt
    
    def plot_summary(self, test_data: np.ndarray,
                    feature_names: Optional[List[str]] = None,
                    save_path: Optional[str] = None):
        """
        Create summary plot showing feature importance across dataset
        
        Args:
            test_data: Test dataset
            feature_names: Feature names
            save_path: Path to save plot
        """
        shap_values = self.explainer.shap_values(test_data)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, test_data, 
                         feature_names=feature_names,
                         show=False)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return plt


# ==========================================
# Hydrological-Specific SHAP Functions
# ==========================================

def explain_hydrological_prediction(
    model,
    instance: np.ndarray,
    background_data: np.ndarray,
    feature_names: List[str] = None
) -> Dict:
    """
    Explain hydrological prediction with domain-specific context
    
    Args:
        model: Trained model
        instance: Input to explain
        background_data: Background dataset
        feature_names: Hydrological feature names
    
    Returns:
        Explanation dictionary
    """
    if feature_names is None:
        feature_names = [
            'Precipitation', 'Temperature', 'Previous_Discharge',
            'Soil_Moisture', 'Snow_Cover', 'Upstream_Flow'
        ]
    
    explainer = SHAPExplainer(model, background_data, model_type='pytorch')
    explanation = explainer.explain_instance(instance, feature_names)
    
    # Add hydrological interpretation
    interpretation = []
    for feature, value in explanation['feature_importance'][:5]:
        if 'Precipitation' in feature and value > 0:
            interpretation.append(f"Higher precipitation increases runoff risk")
        elif 'Temperature' in feature and value > 0:
            interpretation.append(f"Higher temperature affects snowmelt")
        elif 'Discharge' in feature:
            interpretation.append(f"Historical flow patterns are influential")
    
    explanation['hydrological_interpretation'] = interpretation
    
    return explanation
