# install packages
# pip install tensorflow opencv-python
# pip install pyserial
# pip install scikit-learn

import tensorflow as tf
from tensorflow.keras import layers, models
import os
import cv2
import numpy as np
from sklearn.preprocessing import LabelEncoder

import servo_move as sm # to move servo via USB Serial


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
train_images, train_labels = load_images('./metal_nut/train_mix')
#train_images, train_labels = load_images('./metal_nut/train') # classifier not good at identifying anomalies without data
test_images, test_labels = load_images('./metal_nut/test')

# Normalize images to [0,1] range
train_images = train_images / 255.0
test_images = test_images / 255.0

# Convert labels to one-hot encoding
label_encoder = LabelEncoder()
train_labels = label_encoder.fit_transform(train_labels)
test_labels = label_encoder.transform(test_labels)

train_labels = tf.keras.utils.to_categorical(train_labels)
test_labels = tf.keras.utils.to_categorical(test_labels)

# Define a simple CNN model
model = models.Sequential([
    layers.InputLayer(input_shape=(224, 224, 3)),
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    #layers.Dense(len(np.unique(train_labels)), activation='softmax')  # Output layer size = number of classes
    layers.Dense(5, activation='softmax')  # Output layer size = number of classes
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(train_images, train_labels, epochs=15, batch_size=32, validation_data=(test_images, test_labels)) # epo 10

# Save the trained model
model.save('classifier.h5')

# Load the trained model
model = tf.keras.models.load_model('classifier.h5')

# Function to make predictions
def predict_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))  # Resize to match input size
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    img = img / 255.0  # Normalize
    predictions = model.predict(img)
    predicted_class = np.argmax(predictions)  # Get the class with highest probability
    return predicted_class

# Test all images in test set
for label in os.listdir('./metal_nut/test'):
        label_dir = os.path.join('./metal_nut/test', label)
        if os.path.isdir(label_dir):
            for img_name in os.listdir(label_dir):
                image_path = os.path.join(label_dir, img_name)
                predicted_class = predict_image(image_path)
                print(f"Predicted class of {image_path}: {predicted_class}")
                if predicted_class != 3: # anomaly detected, move servo
                    sm.send_signal_to_esp32("MOVE_SERVO")
