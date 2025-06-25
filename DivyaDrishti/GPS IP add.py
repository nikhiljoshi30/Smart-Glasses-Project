GPS/ipproject


import os
import serial
import pynmea2
import cv2
import face_recognition
import time
import numpy as np
from threading import Thread
import requests

# -------------------- GLOBALS --------------------
gps_data = {"latitude": None, "longitude": None}
last_spoken_name = ""
last_spoken_time = 0
ip_location_fetched = False

# -------------------- IP FALLBACK FUNCTION --------------------
def get_ip_location():
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        response.raise_for_status()
        data = response.json()
        loc = data.get('loc')
        if loc:
            lat, lon = loc.split(',')
            print(f"ðŸŒ Approximate Location (via IP): {lat}, {lon}")
            print(f"ðŸŒ Google Maps: https://www.google.com/maps?q={lat},{lon}")
            return True
        else:
            print("âŒ Location not found in IP response.")
            return False
    except Exception as e:
        print(f"âŒ Error fetching IP-based location: {e}")
        return False

# -------------------- GPS READER --------------------
def read_gps():
    try:
        ser = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
        while True:
            line = ser.readline().decode('ascii', errors='replace').strip()
            if line.startswith('$'):
                try:
                    msg = pynmea2.parse(line)
                    if isinstance(msg, (pynmea2.types.talker.GGA, pynmea2.types.talker.RMC)):
                        if msg.latitude and msg.longitude:
                            gps_data["latitude"] = msg.latitude
                            gps_data["longitude"] = msg.longitude
                except pynmea2.ParseError:
                    continue
    except serial.SerialException as e:
        print(f"âŒ GPS error: {e}")

# Start GPS thread
gps_thread = Thread(target=read_gps, daemon=True)
gps_thread.start()

# -------------------- FACE RECOGNITION SETUP --------------------
face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')
known_faces_dir = "known_faces"
known_encodings = []
known_names = []
known_filenames = []

print("ðŸ“¸ Loading known faces...")
for filename in os.listdir(known_faces_dir):
    if filename.lower().endswith(('.jpg', '.png')):
        path = os.path.join(known_faces_dir, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
            known_filenames.append(filename)
print("âœ… Known faces loaded:", known_names)

# Initialize camera
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    print("âŒ Error: Could not open webcam.")
    exit()
print("âœ… Camera opened successfully.")

desktop_path = os.path.expanduser("~/Desktop")
abc_image_path = os.path.join(desktop_path, "abc.jpg")

# -------------------- MAIN LOOP --------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("âš ï¸ Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        rgb_face = face_img[:, :, ::-1]
        name = "Unknown"
        matched_filename = None

        cv2.imwrite(abc_image_path, face_img)

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
                        matched_filename = known_filenames[best_match_index]
        except Exception as e:
            print(f"âš ï¸ Error processing face: {e}")

        current_time = time.time()
        if name == last_spoken_name:
            if current_time - last_spoken_time >= 2:
                os.system(f'espeak "Hello {name}"' if name != "Unknown" else 'espeak "Unknown person"')
                last_spoken_time = current_time
        else:
            os.system(f'espeak "Hello {name}"' if name != "Unknown" else 'espeak "Unknown person"')
            last_spoken_name = name
            last_spoken_time = current_time

        if matched_filename:
            print(f"ðŸ–¼ï¸ Matched image file: {matched_filename}")

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, name, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        if gps_data["latitude"] and gps_data["longitude"]:
            lat = gps_data["latitude"]
            lon = gps_data["longitude"]
            link = f"https://www.google.com/maps?q={lat},{lon}"
            print(f"ðŸ§‘ Face Detected: {name}")
            print(f"ðŸ“ Location: Latitude {lat}, Longitude {lon}")
            print(f"ðŸŒ Google Maps: {link}")
            print("-" * 50)
        else:
            if not ip_location_fetched:
                print("ðŸ“¡ Waiting for GPS fix... Trying IP-based location.")
                success = get_ip_location()
                ip_location_fetched = True
                if not success:
                    print("âŒ Could not determine location. Exiting.")
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

    cv2.imshow('Camera Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -------------------- CLEANUP --------------------
cap.release()
cv2.destroyAllWindows()



