Object
Detection

from ultralytics import YOLO
import cv2
import os
import time

# Load YOLOv8 nano model
model = YOLO('yolov8n.pt')

# Start webcam
cap = cv2.VideoCapture(0)

# Prevent repeating same object too often
last_spoken = {}
SPEAK_INTERVAL = 5  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8
    results = model(frame)
    annotated_frame = results[0].plot()
    cv2.imshow("Object Detection", annotated_frame)

    # Speak detected object names
    if results[0].boxes is not None:
        for box in results[0].boxes:
            cls_id = int(box.cls[0]) if box.cls is not None else -1

            # Skip if class ID is invalid
            if cls_id < 0 or cls_id >= len(model.names):
                continue

            class_name = model.names[cls_id]
            if not class_name.strip():
                continue  # skip empty names

            print(f"?? Detected: {class_name}")
            current_time = time.time()

            # Avoid repeating too often
            if class_name not in last_spoken or (current_time - last_spoken[class_name]) > SPEAK_INTERVAL:
                print(f"?? Speaking: {class_name}")
                os.system(f'espeak "{class_name}"')  # Make sure espeak is installed
                last_spoken[class_name] = current_time

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release
cap.release()
cv2.destroyAllWindows()


