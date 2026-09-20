"""
Gesture Spotify Control - Main Application
ควบคุม Spotify ด้วยท่ามือผ่าน ESP32-CAM

Gestures:
- 🖐️🖐️ แบมือ 2 ข้าง → Ready
- ✊🖐️ ซ้ายกำ + ขวาแบ → เพลงก่อนหน้า
- 🖐️✊ ซ้ายแบ + ขวากำ → เพลงถัดไป
- ✊✊ กำมือ 2 ข้าง (0.3s) → Play/Pause
- ✊ กำมือ + เลื่อนขึ้น-ลง → ปรับเสียง (preview)
- ✊ กำมือ + เลื่อนซ้าย-ขวา → Seek เพลง (preview)
- 🖐️ แบมือ → ส่งค่าไป Spotify
"""
import cv2
import time
from typing import Optional

from config import Config
from gesture import Gesture
from spotify_controller import SpotifyController
from gesture_detector import GestureDetector
from ui_renderer import UIRenderer


class GestureSpotifyApp:
    """แอปพลิเคชันหลัก"""
    
    def __init__(self):
        self.config = Config()
        self.spotify = SpotifyController(self.config)
        self.detector = GestureDetector(self.config)
        self.ui = UIRenderer()
        self.cap = cv2.VideoCapture(self.config.ESP32_URL)
        
        # Cache สำหรับความยาวเพลง (อัพเดททุก 5 วินาที)
        self.cached_duration_ms = None
        self.last_playback_check = 0
    
    def update_playback_cache(self):
        """อัพเดท cache ของความยาวเพลง (ทุก 5 วินาที เพื่อลด API calls)"""
        now = time.time()
        
        if now - self.last_playback_check > 5:
            try:
                playback = self.spotify.sp.current_playback()
                if playback and playback['item']:
                    self.cached_duration_ms = playback['item']['duration_ms']
                self.last_playback_check = now
            except:
                pass
    
    def process_frame(self):
        """อ่านและประมวลผลภาพจาก ESP32-CAM"""
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # พลิกและขยายภาพ
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        frame = cv2.resize(frame, (width * self.config.RESIZE_SCALE, 
                                   height * self.config.RESIZE_SCALE))
        
        return frame
    
    def handle_gesture(self, gesture: Gesture, hand_result) -> None:
        """จัดการท่าทางที่ตรวจจับได้"""
        
        # แบมือ → ส่งค่า Volume/Seek ไป Spotify
        if gesture == Gesture.OPEN:
            if self.detector.get_pending_volume() is not None:
                volume = self.detector.get_pending_volume()
                self.spotify.sp.volume(volume)
                print(f"🔊 Volume → {volume}%")
            
            if self.detector.get_pending_seek() is not None:
                seek_ms = self.detector.get_pending_seek()
                self.spotify.sp.seek_track(seek_ms)
                print(f"⏩ Seek → {seek_ms // 1000}s")
            
            self.detector.reset_pending_controls()
            return
        
        # กำมือ 2 ข้าง → Play/Pause
        if gesture == Gesture.FIST and self.detector.should_execute(gesture):
            self.spotify.play_pause()
            self.detector.reset_state()
            return
        
        # ซ้ายแบ + ขวากำ → เพลงถัดไป
        if gesture == Gesture.SWIPE_RIGHT and self.detector.should_execute(gesture):
            self.spotify.next_track()
            self.detector.reset_state()
            return
        
        # ซ้ายกำ + ขวาแบ → เพลงก่อนหน้า
        if gesture == Gesture.SWIPE_LEFT and self.detector.should_execute(gesture):
            self.spotify.previous_track()
            self.detector.reset_state()
            return
        
        # กำมือข้างเดียว → คำนวณ Volume/Seek (preview mode)
        if self.detector.is_ready and hand_result and hand_result.multi_hand_landmarks:
            if len(hand_result.multi_hand_landmarks) == 1:
                hand = hand_result.multi_hand_landmarks[0]
                
                if self.detector.is_hand_closed(hand):
                    x, y = self.detector.get_hand_position(hand)
                    
                    # บันทึกจุดเริ่มต้น
                    if self.detector.fist_start_x is None:
                        self.detector.fist_start_x = x
                        self.detector.fist_start_y = y
                    
                    # ล็อคโหมดตามทิศทางที่เลื่อน
                    if self.detector.locked_control_mode is None:
                        movement = self.detector.detect_primary_movement(
                            self.detector.fist_start_x, 
                            self.detector.fist_start_y,
                            x, y
                        )
                        
                        if movement == "vertical":
                            self.detector.locked_control_mode = "volume"
                        elif movement == "horizontal":
                            self.detector.locked_control_mode = "seek"
                    
                    # คำนวณค่าตามโหมด
                    if self.detector.locked_control_mode == "volume":
                        self.detector.pending_volume = self.detector.calculate_volume_from_position(y)
                        self.detector.pending_seek = None
                    elif self.detector.locked_control_mode == "seek":
                        if self.cached_duration_ms:
                            self.detector.pending_seek = self.detector.calculate_seek_from_position(x, self.cached_duration_ms)
                        self.detector.pending_volume = None
    
    def run(self) -> None:
        """รันแอปพลิเคชัน"""
        print("🎵 Starting Gesture Spotify Control...")
        print("👋 แบมือ 2 ข้างเพื่อเริ่มต้น | กด 'q' เพื่อออก")
        
        while True:
            # อัพเดท cache ทุก 5 วินาที
            self.update_playback_cache()
            
            # อ่านภาพจากกล้อง
            frame = self.process_frame()
            if frame is None:
                continue
            
            # ตรวจจับท่าทาง
            gesture, hand_result = self.detector.detect_gesture(frame)
            
            # วาด landmarks
            if hand_result and hand_result.multi_hand_landmarks:
                self.ui.draw_landmarks(
                    frame, 
                    hand_result.multi_hand_landmarks,
                    self.detector.mp_hands,
                    self.detector.mp_draw
                )
            
            # จัดการท่าทาง
            self.handle_gesture(gesture, hand_result)
            
            # แสดงผล UI
            self.ui.draw_status(
                frame, 
                self.detector.is_ready, 
                gesture,
                self.detector.get_pending_volume(),
                self.detector.get_pending_seek()
            )
            
            cv2.imshow(self.config.WINDOW_NAME, frame)
            
            # ออกจากโปรแกรม
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
    
    def cleanup(self) -> None:
        """ทำความสะอาดทรัพยากร"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("👋 Goodbye!")


if __name__ == "__main__":
    app = GestureSpotifyApp()
    app.run()

