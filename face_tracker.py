import cv2 as cv
import time
import serial
import threading
import speech_recognition as sr
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

voice_command = None 
voice_thread_started = False
last_seen_time = time.time()
last_intruder_time = 0

voice_lock = threading.Lock()

def listen_for_voice_command():
    global voice_command, voice_thread_started
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Voice] Listening for 'shoot' or 'stop'...")
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"[Voice] Heard: {command}")
            with voice_lock:
                if "shoot" in command:
                    voice_command = "shoot"
                elif "stop" in command:
                    voice_command = "stop"
        except Exception as e:
            print(f"[Voice] Error: {e}")
        finally:
            voice_thread_started = False

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

            if not voice_thread_started:
                voice_thread_started = True
                threading.Thread(target=listen_for_voice_command, daemon=True).start()

            current_time = time.time()
            if current_time - last_intruder_time > 5:
                os.makedirs("intruders", exist_ok=True)
                filename = f"intruders/intruder_{int(current_time)}.png"
                cv.imwrite(filename, frame)
                print(f"[Photo] Saved: {filename}")
                last_intruder_time = current_time

        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
        cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
        cv.putText(frame, name, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv.putText(frame, f"Pos:({cx},{cy})", (x, y + h + 25), cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


        with voice_lock:
            if voice_command != "shoot":
                ser.write(f"{cx},{cy}\n".encode())
                time.sleep(0.02)

        break 

    with voice_lock:
        if voice_command == "shoot":
            ser.write(b'o')
            cv.putText(frame, "⚠️ LASER ARMED!", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        else:
            ser.write(b'f')

        if voice_command == "stop":
            voice_command = None
            print("[Voice] Tracking resumed.")

    if not unknown_detected and time.time() - last_seen_time > 3:
        voice_command = None
        ser.write(b'f')

    cv.putText(frame, "Press 'q' to quit", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    cv.imshow("Face Tracker", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        ser.write(b'f')
        break

cap.release()
ser.close()
cv.destroyAllWindows()