from flask import Flask, render_template_string, jsonify, request
import cv2
import numpy as np
import tensorflow as tf
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
import io
from PIL import Image

app = Flask(__name__)

# ADD YOUR MODEL HERE: Update the path to your *.h5 file
try:
    model = tf.keras.models.load_model('C:\Users\DELL\OneDrive\Desktop\mood_song')  # Replace 'model.h5' with your model file name (e.g., 'my_emotion_model.h5')
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']  # Update if your model uses different labels

# ADD SPOTIFY CREDENTIALS HERE: Replace with your Spotify API credentials
SPOTIFY_CLIENT_ID = '9d617a9d9cff4e899dd4e8899c133002'  # Replace with your Spotify Client ID
SPOTIFY_CLIENT_SECRET = '5c01147339404a76893fed4e2a92ba6c'  # Replace with your Spotify Client Secret
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:5500/callback'
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope='playlist-read-private playlist-modify-private'
    ))
except Exception as e:
    print(f"Spotify API setup error: {e}")
    sp = None

# Mood-to-playlist mapping (Spotify playlist IDs)
mood_playlists = {
    'happy': 'spotify:playlist:37i9dQZF1DXdPec7aLTmlC',  # Happy Hits
    'sad': 'spotify:playlist:37i9dQZF1DX7qK8ma5wgG1',    # Sad Songs
    'angry': 'spotify:playlist:37i9dQZF1DWX83C0l3bV2W',  # Angry Mood
    'neutral': 'spotify:playlist:37i9dQZF1DX0XUsuxWHRQd', # Chill Hits
    'surprise': 'spotify:playlist:37i9dQZF1DX0XUsuxWHRQd',# Chill Hits
    'fear': 'spotify:playlist:37i9dQZF1DX7qK8ma5wgG1',   # Sad Songs
    'disgust': 'spotify:playlist:37i9dQZF1DX7qK8ma5wgG1' # Sad Songs
}

# Face detection setup
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/')
def index():
    # Embedded HTML with unique theme
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MoodVibe Music</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(135deg, #06b6d4, #a855f7);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #ffffff;
            }
            .card {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(12px);
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .card:hover {
                transform: translateY(-8px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
            }
            .glow-button {
                background: linear-gradient(45deg, #ec4899, #22d3ee);
                padding: 0.75rem 2rem;
                border-radius: 30px;
                color: white;
                font-weight: 600;
                box-shadow: 0 0 20px rgba(236, 72, 153, 0.6), 0 0 20px rgba(34, 211, 238, 0.6);
                transition: box-shadow 0.3s ease;
            }
            .glow-button:hover {
                box-shadow: 0 0 30px rgba(236, 72, 153, 0.8), 0 0 30px rgba(34, 211, 238, 0.8);
            }
            .song-card {
                animation: fadeIn 0.6s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(15px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .webcam-container {
                border-radius: 50%;
                overflow: hidden;
                border: 6px solid rgba(255, 255, 255, 0.3);
                box-shadow: 0 0 25px rgba(255, 255, 255, 0.4);
            }
        </style>
    </head>
    <body>
        <div class="container mx-auto p-6 max-w-6xl">
            <h1 class="text-5xl font-bold text-center mb-10 text-white drop-shadow-2xl">MoodVibe Music</h1>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="card flex flex-col items-center">
                    <h2 class="text-3xl font-semibold mb-6">Mood Scanner</h2>
                    <div class="webcam-container">
                        <video id="video" width="320" height="320" autoplay></video>
                        <canvas id="canvas" width="320" height="320" style="display:none;"></canvas>
                    </div>
                    <p class="mt-6 text-xl">Detected Mood: <span id="emotion" class="font-semibold text-pink-300">None</span></p>
                    <button id="scanButton" class="glow-button mt-8" onclick="startScanning()">Start Mood Scan</button>
                </div>
                <div class="card">
                    <h2 class="text-3xl font-semibold mb-6">Your Mood Playlist</h2>
                    <ul id="playlist" class="space-y-4">
                        <li class="song-card p-4 bg-gray-900 bg-opacity-60 rounded-lg text-center">Click "Start Mood Scan" to get song recommendations!</li>
                    </ul>
                </div>
            </div>
        </div>
        <script>
            const video = document.getElementById('video');
            const canvas = document.getElementById('canvas');
            const context = canvas.getContext('2d');
            let scanning = false;

            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    video.srcObject = stream;
                })
                .catch(err => {
                    console.error("Webcam error:", err);
                    document.getElementById('emotion').textContent = 'Webcam not accessible';
                });

            async function fetchEmotion() {
                if (!scanning) return;
                context.drawImage(video, 0, 0, 320, 320);
                const imageData = canvas.toDataURL('image/jpeg');
                try {
                    const response = await fetch('/get_emotion', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: imageData })
                    });
                    const data = await response.json();
                    document.getElementById('emotion').textContent = data.emotion;
                    if (data.emotion !== 'No face detected' && !data.emotion.startsWith('Error')) {
                        fetchPlaylist(data.emotion);
                    }
                } catch (err) {
                    console.error("Fetch error:", err);
                    document.getElementById('emotion').textContent = 'Error detecting mood';
                }
            }

            async function fetchPlaylist(emotion) {
                try {
                    const response = await fetch(`/get_playlist/${emotion}`);
                    const data = await response.json();
                    if (data.error) {
                        document.getElementById('playlist').innerHTML = `<li class="song-card p-4 bg-gray-900 bg-opacity-60 rounded-lg text-center">${data.error}</li>`;
                        return;
                    }
                    const playlist = document.getElementById('playlist');
                    playlist.innerHTML = '';
                    data.forEach(song => {
                        const li = document.createElement('li');
                        li.className = 'song-card p-4 bg-gray-900 bg-opacity-60 rounded-lg';
                        li.innerHTML = `<a href="${song.uri}" target="_blank" class="text-pink-300 hover:text-cyan-300">${song.name}</a> by ${song.artist}`;
                        playlist.appendChild(li);
                    });
                } catch (err) {
                    console.error("Playlist fetch error:", err);
                    document.getElementById('playlist').innerHTML = '<li class="song-card p-4 bg-gray-900 bg-opacity-60 rounded-lg text-center">Error loading playlist</li>';
                }
            }

            function startScanning() {
                scanning = !scanning;
                const button = document.getElementById('scanButton');
                button.textContent = scanning ? 'Stop Scanning' : 'Start Mood Scan';
                if (scanning) {
                    fetchEmotion();
                    setInterval(fetchEmotion, 5000);
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

@app.route('/get_emotion', methods=['POST'])
def get_emotion():
    if not model:
        return jsonify({'emotion': 'Model not loaded'})
    try:
        data = request.json['image']
        img_data = base64.b64decode(data.split(',')[1])
        img = Image.open(io.BytesIO(img_data)).convert('L')
        img = np.array(img)
        faces = face_cascade.detectMultiScale(img, 1.3, 5)
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face = img[y:y+h, x:x+w]
            face = cv2.resize(face, (48, 48))  # Adjust if your model requires a different input size
            face = np.expand_dims(face, axis=0) / 255.0
            face = np.expand_dims(face, axis=-1)
            prediction = model.predict(face)
            emotion = emotions[np.argmax(prediction)]
            return jsonify({'emotion': emotion})
        return jsonify({'emotion': 'No face detected'})
    except Exception as e:
        return jsonify({'emotion': f'Error: {str(e)}'})

@app.route('/get_playlist/<emotion>')
def get_playlist(emotion):
    if not sp:
        return jsonify({'error': 'Spotify API not initialized'})
    try:
        playlist_id = mood_playlists.get(emotion, mood_playlists['neutral'])
        tracks = sp.playlist_tracks(playlist_id)
        songs = [{'name': item['track']['name'], 'artist': item['track']['artists'][0]['name'],
                  'uri': item['track']['uri']} for item in tracks['items']]
        return jsonify(songs[:10])
    except Exception as e:
        return jsonify({'error': f'Spotify error: {str(e)}'})

@app.route('/callback')
def callback():
    return "Spotify authentication complete. Return to the app."

if __name__ == '__main__':
    app.run(debug=True)