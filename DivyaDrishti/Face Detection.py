Face Detection



import cv2
import face_recognition
import os
import time
import numpy as np

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')

# Load known face encodings
known_faces_dir = "known_faces"
known_encodings = []
known_names = []

print("?? Loading known faces...")
for filename in os.listdir(known_faces_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        path = os.path.join(known_faces_dir, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
print("? Known faces loaded:", known_names)

# Initialize webcam
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    print("? Error: Could not open webcam.")
    exit()
print("?? Camera opened successfully.")

# Desktop path to save temporary face
desktop_path = os.path.expanduser("~/Desktop")
abc_image_path = os.path.join(desktop_path, "abc.jpg")

while True:
    ret, frame = cap.read()
    if not ret:
        print("? Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    face_names = []
    face_positions = []

    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        rgb_face = face_img[:, :, ::-1]
        name = "Unknown"

        # Save detected face as abc.jpg
        cv2.imwrite(abc_image_path, face_img)

        # Compare with known faces
        try:
            abc_image = face_recognition.load_image_file(abc_image_path)
            encodings = face_recognition.face_encodings(abc_image)
            if encodings:
                abc_encoding = encodings[0]
                matches = face_recognition.compare_faces(known_encodings, abc_encoding, tolerance=0.5)
                face_distances = face_recognition.face_distance(known_encodings, abc_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_names[best_match_index]
        except Exception as e:
            print(f"?? Error processing abc.jpg: {e}")

        face_names.append(name)
        face_positions.append((x, y, w, h))

        # Draw rectangle and name
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, name, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    # Display result
    cv2.imshow('Camera Feed', frame)

    # Press 'q' to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


