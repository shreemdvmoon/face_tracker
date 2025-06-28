#include <Servo.h>

Servo servoX;
Servo servoY;

int angleX = 90;
int angleY = 90;

String inputString = "";
bool newData = false;

const int laserPin = 7;  // Laser now on pin 7

void setup() {
  Serial.begin(9600);

  servoX.attach(8);
  servoY.attach(9);
  servoX.write(angleX);
  servoY.write(angleY);

  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, LOW);  // Laser OFF by default
}

void loop() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    if (inChar == 'o') {
      digitalWrite(laserPin, HIGH);  // 🔫 Laser ON
      Serial.println("Laser ON");
      inputString = "";
    }
    else if (inChar == 'f') {
      digitalWrite(laserPin, LOW);   // 🚫 Laser OFF
      Serial.println("Laser OFF");
      inputString = "";
    }
    else if (inChar == '\n') {
      newData = true;
      break;
    }
    else {
      inputString += inChar;
    }
  }

  if (newData) {
    int commaIndex = inputString.indexOf(',');
    if (commaIndex > 0) {
      int cx = inputString.substring(0, commaIndex).toInt();
      int cy = inputString.substring(commaIndex + 1).toInt();

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