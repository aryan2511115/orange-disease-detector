"""
Orange Disease Dataset Preprocessing Module
Handles image loading, resizing, augmentation, and normalization
"""

import os
import numpy as np
import cv2
from pathlib import Path
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
from tqdm import tqdm
import json

class OrangeDiseaseDataPreprocessor:
    """
    Preprocesses orange disease dataset for model training.
    Includes image resizing, augmentation, and normalization.
    """
    
    def __init__(self, dataset_path, img_size=(224, 224), test_size=0.2, val_size=0.1):
        """
        Initialize the preprocessor.
        
        Args:
            dataset_path (str): Path to the dataset directory
            img_size (tuple): Target image size (height, width)
            test_size (float): Proportion of data for testing
            val_size (float): Proportion of data for validation
        """
        self.dataset_path = dataset_path
        self.img_size = img_size
        self.test_size = test_size
        self.val_size = val_size
        self.disease_classes = None
        self.class_to_idx = None
        self.idx_to_class = None
        self.images = []
        self.labels = []
        
    def load_images_from_directory(self):
        """
        Load all images from the dataset directory.
        Directory structure: dataset/disease_class/image1.jpg
        
        Returns:
            tuple: (images array, labels array)
        """
        print("Loading images from directory...")
        images = []
        labels = []
        
        # Get all disease classes from directory names
        disease_classes = sorted([d for d in os.listdir(self.dataset_path) 
                                  if os.path.isdir(os.path.join(self.dataset_path, d))])
        
        self.disease_classes = disease_classes
        self.class_to_idx = {cls: idx for idx, cls in enumerate(disease_classes)}
        self.idx_to_class = {idx: cls for idx, cls in enumerate(disease_classes)}
        
        print(f"Found disease classes: {disease_classes}")
        
        # Load images from each disease class
        for disease_idx, disease_class in enumerate(disease_classes):
            disease_path = os.path.join(self.dataset_path, disease_class)
            image_files = [f for f in os.listdir(disease_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            
            print(f"Loading {disease_class}: {len(image_files)} images")
            
            for img_file in tqdm(image_files, desc=f"Loading {disease_class}"):
                try:
                    img_path = os.path.join(disease_path, img_file)
                    img = load_img(img_path, target_size=self.img_size)
                    img_array = img_to_array(img)
                    images.append(img_array)
                    labels.append(disease_idx)
                except Exception as e:
                    print(f"Error loading {img_path}: {str(e)}")
                    continue
        
        self.images = np.array(images, dtype=np.float32)
        self.labels = np.array(labels)
        
        print(f"Total images loaded: {len(self.images)}")
        print(f"Images shape: {self.images.shape}")
        print(f"Labels shape: {self.labels.shape}")
        
        return self.images, self.labels
    
    def normalize_images(self):
        """
        Normalize images to [0, 1] range.
        
        Returns:
            np.array: Normalized images
        """
        print("Normalizing images...")
        self.images = self.images / 255.0
        print("Images normalized to [0, 1] range")
        return self.images
    
    def split_dataset(self):
        """
        Split dataset into train, validation, and test sets.
        Default: 70% train, 15% validation, 15% test
        
        Returns:
            tuple: (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        print("Splitting dataset...")
        
        # First split: separate test set
        X_temp, X_test, y_temp, y_test = train_test_split(
            self.images, self.labels,
            test_size=self.test_size,
            random_state=42,
            stratify=self.labels
        )
        
        # Second split: separate validation from training
        val_ratio = self.val_size / (1 - self.test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_ratio,
            random_state=42,
            stratify=y_temp
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Validation set size: {len(X_val)}")
        print(f"Test set size: {len(X_test)}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def create_data_augmentation(self):
        """
        Create data augmentation generator for training.
        
        Returns:
            ImageDataGenerator: Configured augmentation generator
        """
        print("Creating data augmentation generator...")
        
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
        
        print("Data augmentation generator created")
        return train_datagen
    
    def visualize_samples(self, num_samples=10, save_path=None):
        """
        Visualize sample images from each disease class.
        
        Args:
            num_samples (int): Number of samples to display per class
            save_path (str): Path to save the visualization
        """
        print("Creating sample visualization...")
        
        fig, axes = plt.subplots(len(self.disease_classes), num_samples, figsize=(15, 10))
        fig.suptitle('Sample Images from Each Disease Class', fontsize=16)
        
        # Denormalize for visualization
        display_images = self.images * 255.0
        
        for class_idx, disease_class in enumerate(self.disease_classes):
            class_mask = self.labels == class_idx
            class_indices = np.where(class_mask)[0]
            
            for sample_idx in range(min(num_samples, len(class_indices))):
                img_idx = class_indices[sample_idx]
                ax = axes[class_idx, sample_idx]
                ax.imshow(display_images[img_idx].astype(np.uint8))
                ax.set_title(disease_class if sample_idx == 0 else '')
                ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        
        plt.show()
    
    def get_class_distribution(self):
        """
        Get and visualize class distribution.
        
        Returns:
            dict: Class distribution counts
        """
        print("Calculating class distribution...")
        
        distribution = {}
        for class_idx, disease_class in enumerate(self.disease_classes):
            count = np.sum(self.labels == class_idx)
            distribution[disease_class] = count
            print(f"{disease_class}: {count} images")
        
        # Visualize distribution
        plt.figure(figsize=(10, 6))
        plt.bar(distribution.keys(), distribution.values())
        plt.xlabel('Disease Class')
        plt.ylabel('Number of Images')
        plt.title('Dataset Class Distribution')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        return distribution
    
    def save_preprocessed_data(self, save_dir):
        """
        Save preprocessed data for later use.
        
        Args:
            save_dir (str): Directory to save preprocessed data
        """
        print("Saving preprocessed data...")
        
        os.makedirs(save_dir, exist_ok=True)
        
        np.save(os.path.join(save_dir, 'images.npy'), self.images)
        np.save(os.path.join(save_dir, 'labels.npy'), self.labels)
        
        # Save class mapping
        class_mapping = {
            'class_to_idx': self.class_to_idx,
            'idx_to_class': self.idx_to_class,
            'disease_classes': self.disease_classes
        }
        with open(os.path.join(save_dir, 'class_mapping.json'), 'w') as f:
            json.dump(class_mapping, f, indent=2)
        
        print(f"Preprocessed data saved to {save_dir}")
    
    def load_preprocessed_data(self, data_dir):
        """
        Load previously preprocessed data.
        
        Args:
            data_dir (str): Directory containing preprocessed data
        """
        print("Loading preprocessed data...")
        
        self.images = np.load(os.path.join(data_dir, 'images.npy'))
        self.labels = np.load(os.path.join(data_dir, 'labels.npy'))
        
        with open(os.path.join(data_dir, 'class_mapping.json'), 'r') as f:
            class_mapping = json.load(f)
            self.class_to_idx = class_mapping['class_to_idx']
            self.idx_to_class = class_mapping['idx_to_class']
            self.disease_classes = class_mapping['disease_classes']
        
        print(f"Loaded {len(self.images)} images")
        
    def preprocess_pipeline(self, dataset_path=None):
        """
        Complete preprocessing pipeline.
        
        Args:
            dataset_path (str): Dataset path (overrides initialization path)
            
        Returns:
            tuple: (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        if dataset_path:
            self.dataset_path = dataset_path
        
        # Load images
        self.load_images_from_directory()
        
        # Get class distribution
        self.get_class_distribution()
        
        # Normalize images
        self.normalize_images()
        
        # Visualize samples
        self.visualize_samples()
        
        # Split dataset
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_dataset()
        
        # Convert labels to categorical
        num_classes = len(self.disease_classes)
        y_train_cat = to_categorical(y_train, num_classes)
        y_val_cat = to_categorical(y_val, num_classes)
        y_test_cat = to_categorical(y_test, num_classes)
        
        print("Preprocessing pipeline completed!")
        
        return X_train, X_val, X_test, y_train_cat, y_val_cat, y_test_cat


def main():
    """
    Example usage of the preprocessor.
    """
    # Initialize preprocessor
    dataset_path = '../dataset'  # Update with actual dataset path
    preprocessor = OrangeDiseaseDataPreprocessor(dataset_path)
    
    # Run preprocessing pipeline
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.preprocess_pipeline()
    
    # Save preprocessed data
    preprocessor.save_preprocessed_data('../dataset/preprocessed')
    
    print("Data preprocessing completed successfully!")


if __name__ == '__main__':
    main()
