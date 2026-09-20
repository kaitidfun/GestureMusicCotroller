# Gesture Spotify Control

ควบคุม Spotify ด้วยท่ามือผ่านกล้อง ESP32-CAM

## 🏗️ โครงสร้างโปรเจกต์

```
gesture_spotify/
├── main.py                # Entry point — รันไฟล์นี้
├── config.py               # โหลดค่าตั้งค่า/secret จาก .env
├── gesture.py               # enum ของท่ามือที่รองรับ (Gesture)
├── gesture_detector.py       # ตรวจจับมือด้วย MediaPipe และแปลงเป็นท่ามือ
├── spotify_controller.py     # เรียก Spotify Web API ผ่าน spotipy
├── ui_renderer.py            # วาด overlay/สถานะบนหน้าต่างวิดีโอ
├── requirements.txt
├── .env                      # ค่าจริง (ไม่ commit ขึ้น git)
└── .env.example               # เทมเพลตให้ก็อปไปทำ .env
```

## 🎯 ท่ามือที่รองรับ

| ท่ามือ | คำสั่ง |
|--------|--------|
| 🖐️🖐️ แบมือ 2 ข้าง | เข้าสู่โหมด Ready |
| 🖐️✊ ซ้ายแบ + ขวากำ | เพลงถัดไป |
| ✊🖐️ ซ้ายกำ + ขวาแบ | เพลงก่อนหน้า |
| ✊✊ กำมือ 2 ข้าง (ค้าง ~0.3 วิ) | Play / Pause |
| ✊ กำมือข้างเดียว + เลื่อนขึ้น-ลง | พรีวิวปรับระดับเสียง |
| ✊ กำมือข้างเดียว + เลื่อนซ้าย-ขวา | พรีวิว seek ตำแหน่งเพลง |
| 🖐️ แบมือ (หลังพรีวิว) | ยืนยันส่งค่าไป Spotify |

## 🚀 วิธีใช้งาน

1. **ติดตั้ง dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **ตั้งค่า** - คัดลอก `.env.example` เป็น `.env` แล้วใส่ค่าจริงของคุณ:
   ```
   ESP32_URL=http://YOUR_ESP32_IP:81/stream
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```
   ไฟล์ `.env` จะไม่ถูก commit ขึ้น git (อยู่ใน `.gitignore` แล้ว)

3. **รันโปรแกรม**:
   ```bash
   python main.py
   ```

4. **ควบคุมด้วยท่ามือ** - ทำท่ามือหน้ากล้อง
5. **ออกจากโปรแกรม** - กด `q`

## ➕ วิธีเพิ่มท่ามือใหม่

1. เพิ่มค่าใหม่ใน enum ที่ [`gesture.py`](gesture.py) เช่น `PEACE = "peace"`
2. เขียน logic ตรวจจับท่าทางนั้นใน [`gesture_detector.py`](gesture_detector.py) — ดูตัวอย่างจาก `is_hand_open()` / `is_hand_closed()` / `detect_two_hand_gesture()` เป็นแนวทาง แล้วให้ `detect_gesture()` คืนค่า enum ใหม่ตามเงื่อนไข
3. จัดการคำสั่งเมื่อเจอท่านั้นใน `handle_gesture()` ที่ [`main.py`](main.py) โดยเรียกเมธอดที่ต้องการจาก [`spotify_controller.py`](spotify_controller.py)

## 📦 Dependencies

ดูรายการเต็มได้ที่ [`requirements.txt`](requirements.txt):

- opencv-python
- mediapipe
- spotipy
- python-dotenv

## ✨ ข้อดี

✅ แยกไฟล์ตามหน้าที่ชัดเจน (detection / control / UI / config)  
✅ Secret แยกออกจากโค้ด ปลอดภัยเวลา push ขึ้น git  
✅ Code อ่านง่าย เข้าใจง่าย
