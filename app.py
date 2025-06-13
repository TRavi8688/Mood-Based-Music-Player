import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Set page config for a polished look
st.set_page_config(page_title="Moodify ", layout="centered", page_icon="")

# Custom CSS for better styling
st.markdown("""
    <style>
   .main { background-color: #121212; color: white; }
   .stButton>button { background-color: #1DB954; color: white; border-radius: 20px; }
   .stFileUploader { border: 2px dashed #1DB954; padding: 10px; border-radius: 10px; }
   .stSpinner { color: #1DB954; }
    </style>
""", unsafe_allow_html=True)

# Spotify API Auth
try:
    SPOTIFY_CLIENT_ID = os.environ.get("9d617a9d9cff4e899dd4e8899c133002")
    SPOTIFY_CLIENT_SECRET = os.environ.get("5c01147339404a76893fed4e2a92ba6c")
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        st.error("Spotify credentials not configured. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in Space settings.")
        st.stop()
    auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception as e:
    st.error(f"Failed to initialize Spotify API: {e}")
    st.stop()

# Load model
@st.cache_resource
def load_emotion_model():
    try:
        # Ensure model file exists in the root directory
        if not os.path.exists("my_model.h5"):
            st.error("Model file 'y_model.h5' not found in the Space repository.")
            st.stop()
        model = load_model("my_model.h5")
        return model
    except Exception as e:
        st.error(f"Failed to load emotion detection model: {e}")
        st.stop()

try:
    model = load_emotion_model()
except Exception:
    st.stop()  # Error already displayed in load_emotion_model

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Header
st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #1DB954;"> Moodify</h1>
        <p style="color: #B3B3B3;">Upload a face image to detect your mood and get personalized Spotify music recommendations!</p>
    </div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader(
    "Choose an image (JPG, JPEG, PNG)",
    type=["jpg", "jpeg", "png"],
    help="Upload a clear face image (at least 48x48 pixels) for best results."
)

if uploaded_file is not None:
    try:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", width=200)

        # Process image
        image = Image.open(uploaded_file).convert('L')  # Convert to grayscale
        image = ImageOps.fit(image, (48, 48), Image.Resampling.LANCZOS)
        img_array = np.array(image).astype("float32") / 255.0
        img_array = np.expand_dims(img_array, axis=(0, -1))

        # Predict emotion
        with st.spinner("Analyzing mood..."):
            prediction = model.predict(img_array)
            emotion_idx = np.argmax(prediction)
            emotion = emotion_labels[emotion_idx]
            confidence = np.max(prediction) * 100

        # Display result
        st.markdown(f"""
            <div style="text-align: center;">
                <h3 style="color: #1DB954;">Detected Mood: {emotion} ({confidence:.2f}%)</h3>
            </div>
        """, unsafe_allow_html=True)

        # Spotify Recommendations
        st.markdown("###  Spotify Recommendations")
        with st.spinner("Fetching songs..."):
            try:
                # Map emotions to Spotify search terms for better recommendations
                emotion_to_query = {
                    'Angry': 'angry rock',
                    'Disgust': 'calm instrumental',
                    'Fear': 'ambient chill',
                    'Happy': 'happy pop',
                    'Sad': 'ad acoustic',
                    'Surprise': 'upbeat electronic',
                    'Neutral': 'lofi chill'
                }
                query = emotion_to_query.get(emotion, f"{emotion} music")
                results = sp.search(q=query, type="track", limit=5)
                tracks = results['tracks']['items']
                if not tracks:
                    st.warning(f"No tracks found for '{query}'. Try a different mood.")
                else:
                    for idx, track in enumerate(tracks):
                        song_name = track['name']
                        artist = track['artists'][0]['name']
                        url = track['external_urls']['spotify']
                        preview = track['preview_url']
                        st.markdown(f"**{idx+1}. {song_name}** by *{artist}*")
                        st.markdown(f"[ Listen on Spotify]({url})", unsafe_allow_html=True)
                        if preview:
                            st.audio(preview, format="audio/mp3")
                        else:
                            st.write("(No preview available)")
            except Exception as e:
                st.error(f"Failed to fetch Spotify recommendations: {e}")

    except Exception as e:
        st.error(f"Error processing image: {e}")
else:
    st.markdown(
        "<p style='color: #B3B3B3; text-align: center;'>Please upload an image to detect your mood.</p>",
        unsafe_allow_html=True
    )

# Footer
st.markdown("""
    <div style="text-align: center; padding: 20px; color: #B3B3B3;">
        <p>Powered by TensorFlow, Streamlit, and Spotify API</p>
        <p> 2025 Moodify</p>
    </div>
""", unsafe_allow_html=True)
