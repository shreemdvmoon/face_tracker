import cv2
import time
import serial
import torch 

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#ser = serial.Serial('/dev/cu.usbserial-A5069RR4', 9600)
time.sleep(2)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        cx = x + w // 2
        cy = y + h // 2

        msg = f"{cx},{cy}\n"
#        ser.write(msg.encode())
        print(f"Sending: {msg.strip()}")

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        cv2.putText(frame, "Face", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Pos: ({cx}, {cy})", (x, y+h+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        break

    cv2.putText(frame, "Press 'q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    cv2.imshow("Face Tracker - Detection Mode", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
#ser.close()
cv2.destroyAllWindows()