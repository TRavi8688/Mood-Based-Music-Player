import cv2
import numpy as np
from tensorflow.keras.models import load_model # Make sure this import is correct for your model

# --- 1. Load your trained model ---
# Your model is in the same directory, so you can reference it directly by its name.
# If your model file has an extension (e.g., .h5, .keras), ensure it's included:
# model = load_model('mood_song.h5')
# model = load_model('mood_song.keras')
# If 'mood_song' itself is a folder containing the saved model structure (e.g., Keras SavedModel format),
# then 'mood_song' is the correct path.
try:
    model = load_model('mood_song') # Assuming 'mood_song' refers to the model file/folder in this directory
    print("Model loaded successfully from:", 'mood_song')
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please ensure your model file/folder 'mood_song' is directly in this directory and its name is correct.")
    print("If it has an extension (e.g., .h5, .keras), update the 'load_model' path accordingly.")
    exit()

# --- 2. Define expression labels (ensure order matches your model's output) ---
# IMPORTANT: Adjust these labels to exactly match the order of classes your model was trained on!
expression_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
# Example if your model has different labels or order:
# expression_labels = ['neutral', 'happy', 'sad', 'angry']

# --- 3. Load Haar Cascade for face detection ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- 4. Initialize Webcam ---
cap = cv2.VideoCapture(0) # 0 for default webcam

if not cap.isOpened():
    print("Error: Could not open webcam. Make sure no other application is using it.")
    exit()

print("\nWebcam initialized. Looking for faces...")
print("Press 'q' to quit the program.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam.")
        break

    # Flip the frame horizontally to display it like a mirror (optional, but common)
    frame = cv2.flip(frame, 1)

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- 5. Detect Faces ---
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2) # Draw a blue bounding box

        # --- 6. Preprocess Face ROI for model input ---
        roi_gray = gray_frame[y:y+h, x:x+w]
        # Adjust this to your model's expected input size (e.g., 48x48, 64x64)
        model_input_size = (48, 48) # <<< ADJUST THIS TO YOUR MODEL'S EXPECTED INPUT SIZE
        roi_resized = cv2.resize(roi_gray, model_input_size, interpolation=cv2.INTER_AREA)

        # Preprocessing: Normalize pixel values (0-1 or -1 to 1) and add dimensions
        roi = roi_resized.astype("float") / 255.0
        roi = np.expand_dims(roi, axis=0)  # Add batch dimension (1, H, W)
        roi = np.expand_dims(roi, axis=-1) # Add channel dimension (1, H, W, 1 for grayscale input)

        # --- 7. Predict Expression ---
        predictions = model.predict(roi)[0] # Get probabilities for the single face
        predicted_expression_index = np.argmax(predictions)
        predicted_expression = expression_labels[predicted_expression_index]
        confidence = predictions[predicted_expression_index] * 100

        # --- 8. Display Prediction ---
        text = f"{predicted_expression} ({confidence:.2f}%)"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2) # Green text

    # --- 9. Show the frame ---
    cv2.imshow('Face Expression Recognition (Press Q to Quit)', frame)

    # --- 10. Quit on 'q' press ---
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 11. Release resources ---
cap.release()
cv2.destroyAllWindows()
print("\nProgram terminated. Webcam released.")