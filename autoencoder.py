# install packages
# pip install tensorflow opencv-python
# pip install pyserial
# pip install scikit-learn <- sklearn new name

import tensorflow as tf
from tensorflow.keras import layers, models
import os
import cv2
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Load and preprocess images
def load_images(image_dir, img_size=(224, 224)):
    images = []
    labels = []
    for label in os.listdir(image_dir):
        label_dir = os.path.join(image_dir, label)
        if os.path.isdir(label_dir):
            for img_name in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_name)
                img = cv2.imread(img_path)
                img = cv2.resize(img, img_size)
                images.append(img)
                labels.append(label)  # The label is the folder name
    images = np.array(images)
    labels = np.array(labels)
    return images, labels

# Load training and test images
# train_images, train_labels = load_images('path_to_train_images')
# test_images, test_labels = load_images('path_to_test_images')
train_images, train_labels = load_images('./metal_nut/train')
test_images, test_labels = load_images('./metal_nut/test')

# Normalize images to [0,1] range
train_images = train_images / 255.0
test_images = test_images / 255.0

input_shape = (224, 224, 3)

# Build a simple convolutional autoencoder
input_img = layers.Input(shape=input_shape)

# Encoder
x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
x = layers.MaxPooling2D((2, 2), padding='same')(x)
x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
encoded = layers.MaxPooling2D((2, 2), padding='same')(x)

# Decoder
x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(encoded)
x = layers.UpSampling2D((2, 2))(x)
x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = layers.UpSampling2D((2, 2))(x)
decoded = layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)

autoencoder = models.Model(input_img, decoded)
autoencoder.compile(optimizer='adam', loss='mse')

## TRAIN ONLY ON NORMAL LABEL
autoencoder.fit(train_images, train_images,  # input = output
                epochs=20,
                batch_size=64,
                validation_split=0.1)

## DETECT ANOMALY
reconstructed_train = autoencoder.predict(train_images)
reconstruction_errors_train = np.mean((train_images - reconstructed_train) ** 2, axis=(1,2,3))

reconstructed = autoencoder.predict(test_images)
reconstruction_errors = np.mean((test_images - reconstructed) ** 2, axis=(1,2,3))
print(reconstruction_errors_train)
print(reconstruction_errors)

# You can pick a threshold to classify anomalies
threshold = np.percentile(reconstruction_errors_train, 50)  # top 50% are anomalies

predicted_labels = reconstruction_errors < threshold  # True = anomaly

print(predicted_labels)