import cv2 as cv
import time
import serial
import os

face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv.face.LBPHFaceRecognizer_create()
recognizer.read("lbph_model.xml")

label_map = {}
with open("label_map.txt", "r") as f:
    for line in f:
        label, name = line.strip().split(",")
        label_map[int(label)] = name

ser = serial.Serial('/dev/cu.usbserial-A5069RR4', 9600)
time.sleep(2)

laser_on = False
last_seen_time = time.time()
photo_taken_stage = {"before": False, "during": False, "after": False}
last_state = "off"

cap = cv.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv.flip(frame, 1)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    unknown_detected = False

    for (x, y, w, h) in faces:
        cx, cy = x + w // 2, y + h // 2
        face_roi = gray[y:y+h, x:x+w]
        label, confidence = recognizer.predict(face_roi)
        name = label_map[label] if confidence < 10 else "Unknown"

        if name == "Unknown":
            unknown_detected = True
            last_seen_time = time.time()

            os.makedirs("intruders", exist_ok=True)

            if not laser_on and not photo_taken_stage["before"]:
                filename = f"intruders/before_laser.png"
                cv.imwrite(filename, frame)
                print(f"[Photo] Saved BEFORE laser: {filename}")
                photo_taken_stage["before"] = True

            if laser_on and not photo_taken_stage["during"]:
                filename = f"intruders/during_laser.png"
                cv.imwrite(filename, frame)
                print(f"[Photo] Saved DURING laser: {filename}")
                photo_taken_stage["during"] = True

            color = (0, 0, 255)
        else:
            color = (0, 255, 0)

        cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
        cv.putText(frame, name, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv.putText(frame, f"Pos:({cx},{cy})", (x, y + h + 25), cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        ser.write(f"{cx},{cy}\n".encode())
        time.sleep(0.02)

        break

    if laser_on:
        ser.write(b'o')
        cv.putText(frame, "LASER ARMED", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
    else:
        ser.write(b'f')

    if last_state == "on" and not laser_on and unknown_detected and not photo_taken_stage["after"]:
        filename = f"intruders/after_laser.png"
        cv.imwrite(filename, frame)
        print(f"[Photo] Saved AFTER laser: {filename}")
        photo_taken_stage["after"] = True

    last_state = "on" if laser_on else "off"

    if not unknown_detected and time.time() - last_seen_time > 3:
        ser.write(b'f')
        photo_taken_stage = {"before": False, "during": False, "after": False}

    cv.putText(frame, "Press 's'=ON, 'o'=OFF, 'q'=QUIT", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    cv.imshow("Face Tracker", frame)

    key = cv.waitKey(1) & 0xFF
    if key == ord('q'):
        ser.write(b'f')
        break
    elif key == ord('s'):
        laser_on = True
        print("Laser ON")
    elif key == ord('o'):
        laser_on = False
        print("Laser OFF")

cap.release()
ser.close()
cv.destroyAllWindows()