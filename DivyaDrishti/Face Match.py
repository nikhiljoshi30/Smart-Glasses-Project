Face Match



import face_recognition
import os

# Load known faces and their encodings
known_faces_dir = "known_faces"
known_encodings = []
known_names = []

print("Loading known faces...")
for filename in os.listdir(known_faces_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        path = os.path.join(known_faces_dir, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])
print("Known faces loaded:", known_names)

# Load the unknown image to compare
unknown_image_path = "/home/shree/Desktop/abc.jpg"
unknown_image = face_recognition.load_image_file(unknown_image_path)
unknown_encodings = face_recognition.face_encodings(unknown_image)

if len(unknown_encodings) == 0:
    print("No faces found in unknown image.")
else:
    unknown_encoding = unknown_encodings[0]

    # Compare unknown face encoding with known faces
    results = face_recognition.compare_faces(known_encodings, unknown_encoding)
    face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)

    best_match_index = None
    if len(face_distances) > 0:
        best_match_index = face_distances.argmin()

    if best_match_index is not None and results[best_match_index]:
        print(f"Face matched with: {known_names[best_match_index]}")
    else:
        print("Face not recognized.")






