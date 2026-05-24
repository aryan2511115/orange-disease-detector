"""
Grad-CAM Explainability Module
Generates visual explanations for model predictions using Gradient-weighted Class Activation Maps
"""

import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import Model
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
import os

class GradCAMExplainer:
    """
    Generates Grad-CAM visualizations for neural network predictions.
    Helps understand which regions of the image influenced the model's decision.
    """
    
    def __init__(self, model, layer_name=None):
        """
        Initialize Grad-CAM explainer.
        
        Args:
            model: Trained Keras/TensorFlow model
            layer_name (str): Name of the layer to use for activation maps.
                             If None, uses the last convolutional layer.
        """
        self.model = model
        self.layer_name = layer_name or self._get_last_conv_layer()
        
        # Create a model that maps input to the output of the target layer
        self.conv_outputs = Model(
            inputs=self.model.input,
            outputs=[self.model.get_layer(self.layer_name).output, self.model.output]
        )
        
        print(f"Grad-CAM initialized with layer: {self.layer_name}")
    
    def _get_last_conv_layer(self):
        """
        Get the name of the last convolutional layer in the model.
        
        Returns:
            str: Layer name
        """
        for layer in self.model.layers[::-1]:
            if 'conv' in layer.name.lower():
                return layer.name
        raise ValueError("No convolutional layer found in model")
    
    def generate_gradcam(self, img_array, class_idx):
        """
        Generate Grad-CAM heatmap for an image.
        
        Args:
            img_array (np.array): Input image (1, 224, 224, 3)
            class_idx (int): Class index to generate CAM for
            
        Returns:
            np.array: Heatmap (224, 224)
        """
        img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
        
        with tf.GradientTape() as tape:
            tape.watch(img_tensor)
            conv_outputs, predictions = self.conv_outputs(img_tensor, training=False)
            class_channel = predictions[:, class_idx]
        
        # Compute gradients
        grads = tape.gradient(class_channel, conv_outputs)
        
        # Compute weights
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Generate CAM
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # Normalize heatmap
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        heatmap = heatmap.numpy()
        
        # Resize to original image size
        heatmap_resized = cv2.resize(heatmap, (img_array.shape[2], img_array.shape[1]))
        
        return heatmap_resized
    
    def overlay_gradcam(self, img_array, heatmap, alpha=0.4):
        """
        Overlay Grad-CAM heatmap on original image.
        
        Args:
            img_array (np.array): Original image (denormalized, 0-255)
            heatmap (np.array): Grad-CAM heatmap
            alpha (float): Overlay transparency
            
        Returns:
            np.array: Image with overlaid heatmap
        """
        # Ensure image is in correct format
        if img_array.max() <= 1:
            img_array = (img_array * 255).astype(np.uint8)
        else:
            img_array = img_array.astype(np.uint8)
        
        # Convert to RGB if needed
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            if img_array.shape[0] == 3:
                img_array = np.transpose(img_array, (1, 2, 0))
        
        # Normalize heatmap to 0-255
        heatmap_colored = cv2.applyColorMap(
            (heatmap * 255).astype(np.uint8),
            cv2.COLORMAP_JET
        )
        
        # Overlay
        overlaid = cv2.addWeighted(img_array, 1 - alpha, heatmap_colored, alpha, 0)
        
        return overlaid
    
    def visualize_prediction(self, img_array, true_class=None, pred_class=None, 
                            pred_confidence=None, class_names=None, 
                            save_path=None):
        """
        Create comprehensive visualization of prediction with Grad-CAM.
        
        Args:
            img_array (np.array): Input image (224, 224, 3) normalized 0-1
            true_class (int): True class index
            pred_class (int): Predicted class index
            pred_confidence (float): Prediction confidence
            class_names (list): List of class names
            save_path (str): Path to save visualization
        """
        # Denormalize image for display
        display_img = (img_array.squeeze() * 255).astype(np.uint8)
        if display_img.shape[0] == 3:
            display_img = np.transpose(display_img, (1, 2, 0))
        
        # Generate Grad-CAM
        heatmap = self.generate_gradcam(img_array if len(img_array.shape) == 4 else np.expand_dims(img_array, 0), pred_class)
        
        # Overlay heatmap
        overlaid = self.overlay_gradcam(display_img, heatmap)
        
        # Create visualization
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Grad-CAM Visualization', fontsize=16, fontweight='bold')
        
        # Original image
        axes[0].imshow(display_img)
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # Heatmap
        im = axes[1].imshow(heatmap, cmap='hot')
        axes[1].set_title('Grad-CAM Heatmap')
        axes[1].axis('off')
        plt.colorbar(im, ax=axes[1])
        
        # Overlaid
        axes[2].imshow(overlaid)
        if class_names and pred_class is not None:
            title = f'Prediction: {class_names[pred_class]}'
            if pred_confidence:
                title += f'\nConfidence: {pred_confidence:.2%}'
            if true_class is not None and true_class != pred_class:
                title += f'\nTrue: {class_names[true_class]}'
            axes[2].set_title(title, color='red' if true_class != pred_class else 'green')
        axes[2].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        plt.show()
        
        return {
            'original': display_img,
            'heatmap': heatmap,
            'overlaid': overlaid,
            'figure': fig
        }
    
    def generate_batch_visualizations(self, images, predictions, true_labels=None,
                                     class_names=None, save_dir=None):
        """
        Generate Grad-CAM visualizations for a batch of images.
        
        Args:
            images (np.array): Batch of images
            predictions (np.array): Model predictions
            true_labels (np.array): True labels
            class_names (list): Class names
            save_dir (str): Directory to save visualizations
        """
        for idx in range(min(5, len(images))):  # Limit to 5 for visualization
            img = images[idx:idx+1]
            pred_class = np.argmax(predictions[idx])
            pred_confidence = predictions[idx][pred_class]
            true_class = true_labels[idx] if true_labels is not None else None
            
            save_path = None
            if save_dir:
                save_path = os.path.join(save_dir, f'gradcam_{idx}.png')
            
            self.visualize_prediction(
                img,
                true_class=true_class,
                pred_class=pred_class,
                pred_confidence=pred_confidence,
                class_names=class_names,
                save_path=save_path
            )


def create_gradcam_explainer(model, layer_name=None):
    """
    Factory function to create Grad-CAM explainer.
    
    Args:
        model: Trained Keras/TensorFlow model
        layer_name (str): Target layer name
        
    Returns:
        GradCAMExplainer: Configured explainer instance
    """
    return GradCAMExplainer(model, layer_name)


if __name__ == '__main__':
    print("Grad-CAM Explainability module loaded successfully!")
