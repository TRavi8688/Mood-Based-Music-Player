import streamlit as st
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from PIL import Image

# Load the model
model = load_model("my_model.h5")

# Emotion labels (adjust if needed)
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Title
st.markdown("<h1 style='text-align: center; color: green;'>🎵 Moodify - Mood Detection App</h1>", unsafe_allow_html=True)
st.write("Upload a selfie to detect your mood using deep learning.")

# File uploader
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('L')  # Convert to grayscale
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Preprocess image
    image = image.resize((48, 48))
    image_array = np.array(image) / 255.0
    image_array = np.reshape(image_array, (1, 48, 48, 1))

    # Predict
    prediction = model.predict(image_array)[0]
    predicted_index = np.argmax(prediction)
    predicted_emotion = emotion_labels[predicted_index]
    confidence = prediction[predicted_index] * 100

    # Display results
    st.markdown(f"### 😃 Detected Mood: `{predicted_emotion}`")
    st.markdown(f"**Confidence:** `{confidence:.2f}%`")
