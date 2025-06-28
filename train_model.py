import cv2
import os
import numpy as np

recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

dataset_path = "dataset"
faces = []
labels = []
label_map = {}
current_label = 0

for person in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person)
    label_map[current_label] = person

    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        detected = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in detected:
            faces.append(gray[y:y+h, x:x+w])
            labels.append(current_label)

    current_label += 1

recognizer.train(faces, np.array(labels))
recognizer.save("lbph_model.xml")

with open("label_map.txt", "w") as f:
    for k, v in label_map.items():
        f.write(f"{k},{v}\n")

print("[✓] LBPH training complete.")