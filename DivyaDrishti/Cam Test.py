CAMERA TEST



import cv2
import os
import time

# Load Haar cascade
face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')

# Open webcam using V4L2
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Camera opened successfully.")

# Path to save photos
desktop_path = os.path.expanduser("~/Desktop")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Camera Feed', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') and len(faces) > 0:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        photo_path = os.path.join(desktop_path, f"manual_face_{timestamp}.jpg")
        cv2.imwrite(photo_path, frame)
        print(f"?? Manual photo saved at: {photo_path}")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()