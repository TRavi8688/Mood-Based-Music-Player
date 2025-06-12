import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model
from urllib.request import urlretrieve
import zipfile

# 1. Download and extract your GitHub repository (if not already present)
REPO_URL = "import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model
from urllib.request import urlretrieve
import zipfile

# --- 1. Download and extract model from GitHub if not present ---
REPO_ZIP_URL = "https://github.com/TRavi8688/Mood-Based-Music-Player/edit/main/app.py"
MODEL_PATH = "my_model.h5"

if not os.path.exists(MODEL_PATH):
    print("Downloading model from GitHub...")
    urlretrieve(REPO_ZIP_URL, "repo.zip")
    with zipfile.ZipFile("repo.zip", 'r') as zip_ref:
        zip_ref.extractall()
    os.remove("repo.zip")
    # Move model file if needed from subfolder
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".h5") and not os.path.exists(MODEL_PATH):
                os.rename(os.path.join(root, file), MODEL_PATH)

# --- 2. Load model ---
try:
    model = load_model(MODEL_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# --- 3. Define emotion labels ---
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# --- 4. Load Haar Cascade face detector ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- 5. Emotion detection loop ---
def detect_emotions():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    print("🎥 Webcam started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]

            # Preprocess
            resized = cv2.resize(face_roi, (48, 48))
            normalized = resized / 255.0
            reshaped = np.reshape(normalized, (1, 48, 48, 1))

            # Predict
            predictions = model.predict(reshaped, verbose=0)
            emotion_index = np.argmax(predictions)
            emotion = emotion_labels[emotion_index]
            confidence = np.max(predictions) * 100

            # Display
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            label = f"{emotion} ({confidence:.1f}%)"
            cv2.putText(frame, label, (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Moodify - Emotion Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 Program ended. Webcam released.")

# --- Run if this script is the main program ---
if __name__ == "__main__":
    detect_emotions()
"  # Replace with your actual GitHub repo URL
MODEL_PATH = "my_model.h5"  # Path to your model in the repo

if not os.path.exists(MODEL_PATH):
    print("Downloading model from GitHub...")
    urlretrieve(REPO_URL, "repo.zip")
    with zipfile.ZipFile("repo.zip", 'r') as zip_ref:
        zip_ref.extractall()
    os.remove("repo.zip")

# 2. Load your pre-trained model
try:
    model = load_model(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# 3. Define emotion labels (modify according to your model)
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# 4. Initialize face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 5. Real-time detection function
def detect_emotions():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            
            # Preprocess for your model
            resized = cv2.resize(face_roi, (48, 48))  # Adjust size if needed
            normalized = resized / 255.0
            reshaped = np.reshape(normalized, (1, 48, 48, 1))  # Adjust dimensions
            
            # Predict emotion
            predictions = model.predict(reshaped)
            emotion_index = np.argmax(predictions)
            emotion = emotion_labels[emotion_index]
            confidence = np.max(predictions)
            
            # Display results
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, f"{emotion} ({confidence:.2f})", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        
        cv2.imshow('Facial Expression Recognition', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Run the detection
if __name__ == "__main__":
    detect_emotions()
