import cv2
import os
import numpy as np

data_dir = 'dataset'

faces = []
labels = []
label_map = {}
current_label = 0

for person_id in os.listdir(data_dir):
    if person_id.startswith('.'):
        continue
    
    person_path = os.path.join(data_dir, person_id)
    if not os.path.isdir(person_path):
        continue 

    label_map[current_label] = person_id

    for img_name in os.listdir(person_path):
        if img_name.startswith('.'):
            continue 

        img_path = os.path.join(person_path, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Warning: Could not read image {img_path}, skipping.")
            continue

        faces.append(img)
        labels.append(current_label)

    current_label += 1

labels = np.array(labels)

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.train(faces, labels)

recognizer.save('trained_face.yml')


print("Training complete. Model and labels saved.")