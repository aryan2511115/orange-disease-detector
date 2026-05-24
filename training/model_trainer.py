"""
Deep Learning Model Training Module
Trains and compares MobileNetV2, ResNet50, and EfficientNetB0 for orange disease detection
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from tensorflow.keras.applications import MobileNetV2, ResNet50, EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import json
from datetime import datetime
import pickle

class OrangeDiseaseModelTrainer:
    """
    Trains and compares multiple deep learning models for orange disease detection.
    Uses transfer learning with pre-trained weights.
    """
    
    def __init__(self, num_classes=5, input_shape=(224, 224, 3)):
        """
        Initialize the model trainer.
        
        Args:
            num_classes (int): Number of disease classes
            input_shape (tuple): Input image shape (height, width, channels)
        """
        self.num_classes = num_classes
        self.input_shape = input_shape
        self.models = {}
        self.histories = {}
        self.predictions = {}
        self.metrics = {}
        self.best_model = None
        self.best_model_name = None
        
    def build_mobilenetv2(self):
        """
        Build MobileNetV2 model with transfer learning.
        
        Returns:
            Model: Compiled MobileNetV2 model
        """
        print("Building MobileNetV2 model...")
        
        # Load pre-trained MobileNetV2
        base_model = MobileNetV2(
            input_shape=self.input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Add custom layers
        x = GlobalAveragePooling2D()(base_model.output)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.models['MobileNetV2'] = model
        print("MobileNetV2 model built successfully!")
        
        return model
    
    def build_resnet50(self):
        """
        Build ResNet50 model with transfer learning.
        
        Returns:
            Model: Compiled ResNet50 model
        """
        print("Building ResNet50 model...")
        
        # Load pre-trained ResNet50
        base_model = ResNet50(
            input_shape=self.input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Add custom layers
        x = GlobalAveragePooling2D()(base_model.output)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.models['ResNet50'] = model
        print("ResNet50 model built successfully!")
        
        return model
    
    def build_efficientnetb0(self):
        """
        Build EfficientNetB0 model with transfer learning.
        
        Returns:
            Model: Compiled EfficientNetB0 model
        """
        print("Building EfficientNetB0 model...")
        
        # Load pre-trained EfficientNetB0
        base_model = EfficientNetB0(
            input_shape=self.input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Add custom layers
        x = GlobalAveragePooling2D()(base_model.output)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.models['EfficientNetB0'] = model
        print("EfficientNetB0 model built successfully!")
        
        return model
    
    def build_all_models(self):
        """
        Build all three models.
        """
        print("\n=== Building All Models ===\n")
        self.build_mobilenetv2()
        self.build_resnet50()
        self.build_efficientnetb0()
        print("\nAll models built successfully!")
    
    def train_model(self, model_name, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """
        Train a single model.
        
        Args:
            model_name (str): Name of the model to train
            X_train (np.array): Training images
            y_train (np.array): Training labels
            X_val (np.array): Validation images
            y_val (np.array): Validation labels
            epochs (int): Number of epochs
            batch_size (int): Batch size
            
        Returns:
            History: Training history
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Build it first using build_all_models()")
        
        print(f"\n{'='*50}")
        print(f"Training {model_name}")
        print(f"{'='*50}\n")
        
        model = self.models[model_name]
        
        # Define callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                f'../models/{model_name}_best.h5',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Data augmentation
        train_datagen = ImageDataGenerator(
            rotation_range=40,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            fill_mode='nearest',
            brightness_range=[0.8, 1.2]
        )
        
        # Train model
        history = model.fit(
            train_datagen.flow(X_train, y_train, batch_size=batch_size),
            steps_per_epoch=len(X_train) // batch_size,
            epochs=epochs,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        self.histories[model_name] = history
        
        # Save model
        model.save(f'../models/{model_name}_final.h5')
        
        print(f"\n{model_name} training completed!")
        
        return history
    
    def train_all_models(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        """
        Train all three models.
        
        Args:
            X_train (np.array): Training images
            y_train (np.array): Training labels
            X_val (np.array): Validation images
            y_val (np.array): Validation labels
            epochs (int): Number of epochs
            batch_size (int): Batch size
        """
        for model_name in self.models.keys():
            self.train_model(model_name, X_train, y_train, X_val, y_val, epochs, batch_size)
    
    def evaluate_model(self, model_name, X_test, y_test):
        """
        Evaluate a model on test set.
        
        Args:
            model_name (str): Name of the model
            X_test (np.array): Test images
            y_test (np.array): Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        print(f"\nEvaluating {model_name}...")
        
        model = self.models[model_name]
        
        # Make predictions
        y_pred_proba = model.predict(X_test, verbose=0)
        y_pred = np.argmax(y_pred_proba, axis=1)
        y_true = np.argmax(y_test, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        metrics = {
            'model_name': model_name,
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }
        
        self.metrics[model_name] = metrics
        self.predictions[model_name] = {
            'y_true': y_true,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
        
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")
        
        return metrics
    
    def evaluate_all_models(self, X_test, y_test):
        """
        Evaluate all models.
        
        Args:
            X_test (np.array): Test images
            y_test (np.array): Test labels
        """
        print("\n" + "="*50)
        print("EVALUATING ALL MODELS")
        print("="*50)
        
        for model_name in self.models.keys():
            self.evaluate_model(model_name, X_test, y_test)
    
    def compare_models(self):
        """
        Compare metrics of all models and select the best one.
        
        Returns:
            str: Name of the best model
        """
        print("\n" + "="*50)
        print("MODEL COMPARISON")
        print("="*50 + "\n")
        
        # Create comparison dataframe
        comparison_data = []
        for model_name, metrics in self.metrics.items():
            comparison_data.append({
                'Model': model_name,
                'Accuracy': f"{metrics['accuracy']:.4f}",
                'Precision': f"{metrics['precision']:.4f}",
                'Recall': f"{metrics['recall']:.4f}",
                'F1-Score': f"{metrics['f1_score']:.4f}"
            })
        
        # Print comparison
        print(f"{'Model':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
        print("-" * 68)
        for row in comparison_data:
            print(f"{row['Model']:<20} {row['Accuracy']:<12} {row['Precision']:<12} {row['Recall']:<12} {row['F1-Score']:<12}")
        
        # Find best model based on F1-score
        best_model = max(self.metrics.items(), key=lambda x: x[1]['f1_score'])
        self.best_model_name = best_model[0]
        self.best_model = self.models[self.best_model_name]
        
        print(f"\n🏆 Best Model: {self.best_model_name} (F1-Score: {best_model[1]['f1_score']:.4f})")
        
        return self.best_model_name
    
    def plot_training_history(self, model_name=None):
        """
        Plot training history for a model.
        
        Args:
            model_name (str): Name of the model (if None, plots all)
        """
        if model_name:
            models_to_plot = [model_name]
        else:
            models_to_plot = list(self.histories.keys())
        
        for model_name in models_to_plot:
            if model_name not in self.histories:
                continue
            
            history = self.histories[model_name]
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            fig.suptitle(f'{model_name} Training History', fontsize=16)
            
            # Plot accuracy
            axes[0].plot(history.history['accuracy'], label='Train Accuracy', linewidth=2)
            axes[0].plot(history.history['val_accuracy'], label='Val Accuracy', linewidth=2)
            axes[0].set_xlabel('Epoch')
            axes[0].set_ylabel('Accuracy')
            axes[0].set_title('Model Accuracy')
            axes[0].legend()
            axes[0].grid(True)
            
            # Plot loss
            axes[1].plot(history.history['loss'], label='Train Loss', linewidth=2)
            axes[1].plot(history.history['val_loss'], label='Val Loss', linewidth=2)
            axes[1].set_xlabel('Epoch')
            axes[1].set_ylabel('Loss')
            axes[1].set_title('Model Loss')
            axes[1].legend()
            axes[1].grid(True)
            
            plt.tight_layout()
            plt.savefig(f'../reports/{model_name}_training_history.png', dpi=150, bbox_inches='tight')
            plt.show()
    
    def plot_confusion_matrices(self, class_names=None):
        """
        Plot confusion matrices for all models.
        
        Args:
            class_names (list): Disease class names
        """
        if not class_names:
            class_names = [f'Class {i}' for i in range(self.num_classes)]
        
        num_models = len(self.metrics)
        fig, axes = plt.subplots(1, num_models, figsize=(6*num_models, 5))
        
        if num_models == 1:
            axes = [axes]
        
        for idx, (model_name, metrics) in enumerate(self.metrics.items()):
            cm = np.array(metrics['confusion_matrix'])
            
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                       xticklabels=class_names, yticklabels=class_names,
                       cbar_kws={'label': 'Count'})
            
            axes[idx].set_title(f'{model_name}\nConfusion Matrix', fontsize=12, fontweight='bold')
            axes[idx].set_ylabel('True Label')
            axes[idx].set_xlabel('Predicted Label')
        
        plt.tight_layout()
        plt.savefig('../reports/confusion_matrices_comparison.png', dpi=150, bbox_inches='tight')
        plt.show()
    
    def generate_model_comparison_report(self, save_path='../reports/model_comparison.json'):
        """
        Generate comprehensive model comparison report.
        
        Args:
            save_path (str): Path to save the report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'num_classes': self.num_classes,
            'input_shape': self.input_shape,
            'models': self.metrics,
            'best_model': self.best_model_name,
            'best_model_metrics': self.metrics[self.best_model_name] if self.best_model_name else None
        }
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nModel comparison report saved to {save_path}")
    
    def save_best_model(self, model_path='../models/best_model.h5'):
        """
        Save the best model.
        
        Args:
            model_path (str): Path to save the model
        """
        if self.best_model:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            self.best_model.save(model_path)
            print(f"Best model ({self.best_model_name}) saved to {model_path}")


def main():
    """
    Example training pipeline.
    """
    print("\n" + "="*60)
    print("ORANGE DISEASE DETECTION - MODEL TRAINING PIPELINE")
    print("="*60 + "\n")
    
    # Initialize trainer
    trainer = OrangeDiseaseModelTrainer(num_classes=5, input_shape=(224, 224, 3))
    
    # Build all models
    trainer.build_all_models()
    
    # Load data (assuming preprocessed data exists)
    # X_train, y_train = load_data('train')
    # X_val, y_val = load_data('val')
    # X_test, y_test = load_data('test')
    
    # Train all models
    # trainer.train_all_models(X_train, y_train, X_val, y_val, epochs=50, batch_size=32)
    
    # Evaluate all models
    # trainer.evaluate_all_models(X_test, y_test)
    
    # Compare models and select best
    # best_model_name = trainer.compare_models()
    
    # Plot training history
    # trainer.plot_training_history()
    
    # Plot confusion matrices
    # disease_names = ['Citrus Canker', 'Black Spot', 'Citrus Greening', 'Leaf Miner', 'Healthy']
    # trainer.plot_confusion_matrices(disease_names)
    
    # Generate report
    # trainer.generate_model_comparison_report()
    
    # Save best model
    # trainer.save_best_model()
    
    print("\nTraining pipeline structure ready!")


if __name__ == '__main__':
    main()
