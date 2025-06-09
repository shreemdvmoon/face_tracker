import cv2
import os

cap = cv2.VideoCapture(0)

name = "akhil"
save_path = f"dataset/{name}"
os.makedirs(save_path, exist_ok=True)

count = 0
max_images = 100

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if count < max_images:
        img_path = os.path.join(save_path, f"{count}.jpg")
        cv2.imwrite(img_path, gray)
        count += 1

    cv2.putText(frame, f"Capturing image {count}/{max_images}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Capturing Your Face", frame)

    if cv2.waitKey(1000) & 0xFF == ord('q') or count >= max_images:
        break

cap.release()
cv2.destroyAllWindows()