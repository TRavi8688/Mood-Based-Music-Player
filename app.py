from flask import Flask, request
import numpy as np
import cv2
import os
from tensorflow.keras.models import load_model
from werkzeug.utils import secure_filename

app = Flask(__name__)
model = load_model("my_model.h5")

# Define emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Load face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Home Page
@app.route("/", methods=["GET"])
def home():
    return '''
        <html>
            <head>
                <title>Moodify - Upload Mood</title>
                <style>
                    body {
                        background-color: black;
                        color: white;
                        font-family: sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                    }
                    h1 { color: #32CD32; }
                    form {
                        background-color: #111;
                        padding: 30px;
                        border-radius: 12px;
                        box-shadow: 0 0 10px #32CD32;
                    }
                    input[type="file"], button {
                        margin-top: 10px;
                        padding: 10px;
                        border-radius: 5px;
                        border: none;
                    }
                    button {
                        background-color: #32CD32;
                        color: black;
                        font-weight: bold;
                    }
                </style>
            </head>
            <body>
                <h1>🎵 Moodify</h1>
                <p>Upload your image to detect your mood</p>
                <form method="POST" enctype="multipart/form-data" action="/predict">
                    <input type="file" name="image" accept="image/*" required /><br>
                    <button type="submit">Detect Mood</button>
                </form>
            </body>
        </html>
    '''

# Prediction Endpoint
@app.route("/predict", methods=["POST"])
def predict():
    if 'image' not in request.files:
        return "No image file provided."

    file = request.files['image']
    filename = secure_filename(file.filename)
    file_path = os.path.join("temp.jpg")
    file.save(file_path)

    try:
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        emotion = "No Face Detected"

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (48, 48))
            face = face / 255.0
            face = np.reshape(face, (1, 48, 48, 1))

            predictions = model.predict(face)
            emotion = emotion_labels[np.argmax(predictions)]
            break

        os.remove(file_path)
        return f"<h2>🎭 Detected Mood: {emotion}</h2><a href='/'>Try Again</a>"

    except Exception as e:
        return f"Error processing image: {str(e)}"

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
