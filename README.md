# ClimberBot

ClimberBot is a DIY robot project that combines movement control with a real-time camera streaming system. It is designed using an Arduino Uno for movement and an ESP32-CAM for visual feedback.

## Features

- *Bluetooth-Controlled Movement*: Control the robot wirelessly using commands via a Bluetooth module (HC-05).
- *Ultrasonic Obstacle Detection*: The robot stops or alters its behavior based on proximity to obstacles.
- *ESC Motor Integration*: Includes motor speed control via Electronic Speed Controller (ESC).
- *ESP32-CAM Streaming*: Live camera feed via Wi-Fi using the ESP32-CAM module.
- *Simple Web Interface*: Access camera stream through a browser on the same Wi-Fi network.

---

## Hardware Components

- Arduino Uno
- ESP32-CAM (AI Thinker model)
- HC-05 Bluetooth Module
- Motor Driver (L298N or similar)
- Servo Motor / ESC
- Ultrasonic Sensor (HC-SR04)
- Power Supply (Battery or Adapter)
- Jumper wires, breadboard, and chassis

---

## Software Requirements

- Arduino IDE
- ESP32 board support in Arduino IDE
- Required libraries:
  - Servo.h
  - esp_camera.h
  - WiFi.h

---

## Movement Code (Arduino Uno)

- Accepts commands via Bluetooth:
  - F – Forward (if distance > 10 cm)
  - B – Backward
  - L – Turn Left
  - R – Turn Right
  - A – Accelerate (ESC signal)
  - P – Stop ESC

Includes ultrasonic sensor logic for obstacle avoidance.

*Location*: climberbot-movement.ino

---

## Camera Code (ESP32-CAM)

- Connects to Wi-Fi (Update ssid and password).
- Initializes the camera with optimized settings for UXGA or QVGA.
- Hosts a camera stream accessible through a browser.

*Location*: climberbot-camera.ino

---

## Usage Instructions

1. *Upload* the Arduino sketch to the Arduino Uno.
2. *Upload* the ESP32-CAM sketch using ESP32 board in Arduino IDE.
3. *Connect hardware* as per pin definitions in code.
4. Power both modules and connect to ESP32-CAM’s IP address shown in the Serial Monitor.
5. Use a Bluetooth terminal app to send movement commands.

---

## Future Improvements

- Add voice control
- Integrate a mobile app UI
- Enable autonomous navigation with AI

---

## License

This project is open-source and available under the MIT License.
