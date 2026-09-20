# Gesture Spotify Control

Control Spotify with hand gestures via an ESP32-CAM.

## 🏗️ Project Structure

```
gesture_spotify/
├── main.py                # Entry point — run this file
├── config.py               # Loads settings/secrets from .env
├── gesture.py               # Enum of supported gestures (Gesture)
├── gesture_detector.py       # Detects hands with MediaPipe and maps them to a gesture
├── spotify_controller.py     # Calls the Spotify Web API via spotipy
├── ui_renderer.py            # Draws overlays/status on the video window
├── requirements.txt
├── .env                      # Real secrets (not committed to git)
└── .env.example               # Template to copy into .env
```

## 🎯 Supported Gestures

| Gesture | Command |
|--------|--------|
| 🖐️🖐️ Both hands open | Enter Ready mode |
| 🖐️✊ Left open + right fist | Next track |
| ✊🖐️ Left fist + right open | Previous track |
| ✊✊ Both hands fist (hold ~0.3s) | Play / Pause |
| ✊ One fist + move up/down | Preview volume level |
| ✊ One fist + move left/right | Preview seek position |
| 🖐️ Open hand (after preview) | Commit the value to Spotify |

## 🚀 How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure** — copy `.env.example` to `.env` and fill in your real values:
   ```
   ESP32_URL=http://YOUR_ESP32_IP:81/stream
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```
   The `.env` file is not committed to git (already in `.gitignore`)

3. **Run the app**:
   ```bash
   python main.py
   ```

4. **Control with gestures** — perform gestures in front of the camera
5. **Quit** — press `q`

## ➕ Adding a New Gesture

1. Add a new value to the enum in [`gesture.py`](gesture.py), e.g. `PEACE = "peace"`
2. Write detection logic for that gesture in [`gesture_detector.py`](gesture_detector.py) — use `is_hand_open()` / `is_hand_closed()` / `detect_two_hand_gesture()` as a reference, and have `detect_gesture()` return the new enum value under the right condition
3. Handle the command when that gesture is detected in `handle_gesture()` inside [`main.py`](main.py), calling the method you need from [`spotify_controller.py`](spotify_controller.py)

## 📦 Dependencies

See the full list in [`requirements.txt`](requirements.txt):

- opencv-python
- mediapipe
- spotipy
- python-dotenv

## ✨ Highlights

✅ Files are split cleanly by responsibility (detection / control / UI / config)
✅ Secrets are kept out of the source code — safe to push to git
✅ Readable, straightforward code
