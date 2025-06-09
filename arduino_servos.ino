#include <Servo.h>

Servo servoX;
Servo servoY;

int angleX = 90;
int angleY = 90;

String inputString = "";
bool newData = false;

void setup() {
  Serial.begin(9600);
  servoX.attach(9);
  servoY.attach(10); 
  servoX.write(angleX);
  servoY.write(angleY);
}

void loop() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      newData = true;
      break;
    } else {
      inputString += inChar;
    }
  }

  if (newData) {
    int commaIndex = inputString.indexOf(',');
    if (commaIndex > 0) {
      int cx = inputString.substring(0, commaIndex).toInt();
      int cy = inputString.substring(commaIndex + 1).toInt();

      // Map screen position (e.g., 0–640) to servo angles (30–150)
      angleX = map(cx, 0, 640, 30, 150);
      angleY = map(cy, 0, 480, 30, 150);

      servoX.write(angleX);
      delay(10);
      servoY.write(angleY);
    }
    inputString = "";
    newData = false;
  }
}