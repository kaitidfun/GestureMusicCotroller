# Gesture Music Controller

A touchless Spotify controller driven by hand gestures, detected through an ESP32-CAM. OpenCV and MediaPipe read the hand gestures in real time and translate them into Spotify Web API commands.

Full project report: [`iot project.pdf`](iot%20project.pdf)

## 🏗️ Architecture

```
ESP32-CAM  --(MJPEG stream over Wi-Fi)-->  Python (OpenCV + MediaPipe)  --(Spotify Web API)-->  Spotify
     ^
     | (distance, via Serial)
Arduino Uno + Ultrasonic Sensor (u100)
```

## 📂 Repo Structure

| Folder | Description |
|---|---|
| [`project/gesture_spotify/`](project/gesture_spotify) | Main Python app — detects hand gestures and controls Spotify. See its own [README](project/gesture_spotify/README.md) for setup/run instructions |
| [`project/esp32cam/`](project/esp32cam) | Firmware (Arduino/.ino) for the ESP32-CAM — streams video over Wi-Fi for the Python app to read |
| [`project/u100/`](project/u100) | Sketch for the Arduino Uno + ultrasonic distance sensor |

## 🚀 Getting Started

1. **ESP32-CAM**: Open `project/esp32cam/esp32cam.ino` in the Arduino IDE, copy `secrets.h.example` to `secrets.h` and fill in your Wi-Fi SSID/password, then upload it to the board
2. **Arduino Uno (optional)**: Upload `project/u100/u100.ino` if you want to use the ultrasonic distance sensor as well
3. **Python**: Go to [`project/gesture_spotify/`](project/gesture_spotify) and follow its [README](project/gesture_spotify/README.md) — install dependencies, set up `.env`, then run `python main.py`

## 🎥 Demo

See it in action in the report [`iot project.pdf`](iot%20project.pdf) (Photos & Evidence and App page sections)

## ✨ Results

~19–20 FPS, ~340 ms median latency, ~94% accuracy under normal lighting

## 👤 Author

Chanagun Khunphet — [github.com/kaitidfun](https://github.com/kaitidfun)
