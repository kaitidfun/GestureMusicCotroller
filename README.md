# Gesture Music Controller

ควบคุม Spotify แบบไม่ต้องแตะเครื่อง ด้วยท่ามือที่ตรวจจับผ่านกล้อง ESP32-CAM — ใช้ OpenCV และ MediaPipe อ่านท่าทางมือ แล้วส่งคำสั่งไปที่ Spotify Web API แบบเรียลไทม์

รายงานฉบับเต็ม: [`iot project.pdf`](iot%20project.pdf)

## 🏗️ Architecture

```
ESP32-CAM  --(MJPEG stream over Wi-Fi)-->  Python (OpenCV + MediaPipe)  --(Spotify Web API)-->  Spotify
     ^
     | (distance, via Serial)
Arduino Uno + Ultrasonic Sensor (u100)
```

## 📂 โครงสร้าง Repo

| โฟลเดอร์ | รายละเอียด |
|---|---|
| [`project/gesture_spotify/`](project/gesture_spotify) | แอป Python หลัก — ตรวจจับท่ามือและควบคุม Spotify ดูวิธีติดตั้ง/รันได้ที่ [README ของโฟลเดอร์นี้](project/gesture_spotify/README.md) |
| [`project/esp32cam/`](project/esp32cam) | Firmware (Arduino/.ino) สำหรับ ESP32-CAM — สตรีมวิดีโอผ่าน Wi-Fi ให้ฝั่ง Python อ่าน |
| [`project/u100/`](project/u100) | Sketch สำหรับ Arduino Uno + เซนเซอร์วัดระยะอัลตราโซนิก |

## 🚀 เริ่มต้นใช้งาน

1. **ESP32-CAM**: เปิด `project/esp32cam/esp32cam.ino` ด้วย Arduino IDE, คัดลอก `secrets.h.example` เป็น `secrets.h` แล้วใส่ WiFi SSID/Password ของคุณ, อัปโหลดขึ้นบอร์ด
2. **Arduino Uno (ไม่บังคับ)**: อัปโหลด `project/u100/u100.ino` ถ้าต้องการใช้เซนเซอร์วัดระยะร่วมด้วย
3. **Python**: เข้าไปที่ [`project/gesture_spotify/`](project/gesture_spotify) แล้วทำตาม [README](project/gesture_spotify/README.md) — ติดตั้ง dependencies, ตั้งค่า `.env`, แล้วรัน `python main.py`

## 🎥 Demo

ดูตัวอย่างการทำงานได้ในรายงาน [`iot project.pdf`](iot%20project.pdf) (หน้า Photos & Evidence และ App page)

## ✨ ผลทดสอบ

~19–20 FPS, ~340 ms median latency, ~94% accuracy ภายใต้แสงปกติ

## 👤 ผู้จัดทำ

Chanagun Khunphet — [github.com/kaitidfun](https://github.com/kaitidfun)
