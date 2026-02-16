"""
GIMAT - LIME Explainer
Local Interpretable Model-agnostic Explanations
"""

from lime import lime_tabular
import numpy as np
from typing import List, Dict, Optional
import torch


class LIMEExplainer:
    """
    LIME (Local Interpretable Model-agnostic Explanations) wrapper
    
    Explains individual predictions by approximating the model locally
    with an interpretable model
    """
    
    def __init__(self, training_data: np.ndarray, 
                 feature_names: Optional[List[str]] = None,
                 class_names: Optional[List[str]] = None,
                 mode: str = 'regression'):
        """
        Initialize LIME explainer
        
        Args:
            training_data: Training dataset for LIME
            feature_names: Names of features
            class_names: Names of classes (for classification)
            mode: 'regression' or 'classification'
        """
        self.training_data = training_data
        self.feature_names = feature_names or [f"Feature_{i}" for i in range(training_data.shape[1])]
        self.mode = mode
        
        self.explainer = lime_tabular.LimeTabularExplainer(
            training_data,
            feature_names=self.feature_names,
            class_names=class_names,
            mode=mode,
            random_state=42
        )
    
    def explain_instance(self, model, instance: np.ndarray,
                        num_features: int = 10) -> Dict:
        """
        Explain a single prediction
        
        Args:
            model: Model to explain (should have predict method)
            instance: Instance to explain
            num_features: Number of features to show
        
        Returns:
            Explanation dictionary
        """
        # Wrap PyTorch model if needed
        if isinstance(model, torch.nn.Module):
            def predict_fn(x):
                model.eval()
                with torch.no_grad():
                    x_tensor = torch.FloatTensor(x)
                    if x_tensor.ndim == 2:
                        x_tensor = x_tensor.unsqueeze(1)  # Add sequence dim if needed
                    predictions = model(x_tensor)
                    return predictions.numpy()
        else:
            predict_fn = model.predict
        
        # Generate explanation
        if instance.ndim == 1:
            instance_1d = instance
        else:
            instance_1d = instance.flatten()
        
        exp = self.explainer.explain_instance(
            instance_1d,
            predict_fn,
            num_features=num_features
        )
        
        # Extract feature weights
        feature_weights = exp.as_list()
        
        # Get prediction and score
        if self.mode == 'regression':
            prediction = predict_fn(instance.reshape(1, -1))[0][0]
            score = exp.score
        else:
            prediction = np.argmax(predict_fn(instance.reshape(1, -1)))
            score = exp.score
        
        return {
            'prediction': float(prediction),
            'score': float(score),
            'feature_weights': feature_weights,
            'explanation': self._generate_text_explanation(feature_weights),
            'local_model_r2': float(score)
        }
    
    def _generate_text_explanation(self, feature_weights: List[tuple]) -> str:
        """Generate human-readable explanation"""
        explanation = "Local model explanation:\n"
        
        for feature_desc, weight in feature_weights:
            impact = "positively" if weight > 0 else "negatively"
            explanation += f"• {feature_desc}: {impact} impacts prediction (weight: {weight:.4f})\n"
        
        return explanation
    
    def plot_explanation(self, model, instance: np.ndarray,
                        num_features: int = 10,
                        save_path: Optional[str] = None):
        """
        Create visualization of LIME explanation
        
        Args:
            model: Model to explain
            instance: Instance to explain
            num_features: Number of features to show
            save_path: Path to save plot
        """
        import matplotlib.pyplot as plt
        
        # Get explanation
        exp_dict = self.explain_instance(model, instance, num_features)
        feature_weights = exp_dict['feature_weights']
        
        # Extract features and weights
        features = [fw[0] for fw in feature_weights]
        weights = [fw[1] for fw in feature_weights]
        
        # Create horizontal bar plot
        plt.figure(figsize=(10, 6))
        colors = ['green' if w > 0 else 'red' for w in weights]
        plt.barh(range(len(features)), weights, color=colors, alpha=0.7)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Feature Weight (impact on prediction)')
        plt.title(f'LIME Explanation (R²: {exp_dict["local_model_r2"]:.3f})')
        plt.axvline(x=0, color='black', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return plt


# ==========================================
# Utility Functions
# ==========================================

def compare_lime_shap(model, instance: np.ndarray,
                     training_data: np.ndarray,
                     feature_names: List[str]) -> Dict:
    """
    Compare LIME and SHAP explanations
    
    Args:
        model: Trained model
        instance: Instance to explain
        training_data: Training data
        feature_names: Feature names
    
    Returns:
        Dictionary with both explanations
    """
    # LIME explanation
    lime_exp = LIMEExplainer(training_data, feature_names)
    lime_result = lime_exp.explain_instance(model, instance)
    
    # SHAP explanation
    from explainability.shap_explainer import SHAPExplainer
    shap_exp = SHAPExplainer(model, training_data[:100], model_type='pytorch')
    shap_result = shap_exp.explain_instance(instance, feature_names)
    
    return {
        'lime': lime_result,
        'shap': shap_result,
        'agreement': _calculate_agreement(lime_result, shap_result)
    }


def _calculate_agreement(lime_result: Dict, shap_result: Dict) -> float:
    """Calculate agreement between LIME and SHAP"""
    # Simple correlation of feature importances
    lime_weights = dict(lime_result['feature_weights'])
    shap_values = dict(zip(shap_result['feature_names'], shap_result['shap_values']))
    
    common_features = set(lime_weights.keys()) & set(shap_values.keys())
    
    if not common_features:
        return 0.0
    
    lime_arr = np.array([lime_weights[f] for f in common_features])
    shap_arr = np.array([shap_values[f] for f in common_features])
    
    correlation = np.corrcoef(lime_arr, shap_arr)[0, 1]
    
    return float(correlation)
