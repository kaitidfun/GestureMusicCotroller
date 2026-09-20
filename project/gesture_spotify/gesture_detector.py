"""
Gesture Detector - ตรวจจับและจัดการท่าทาง
"""
import cv2
import mediapipe as mp
import time
from typing import Optional, Tuple
from config import Config
from gesture import Gesture


class GestureDetector:
    """ตรวจจับและจัดการท่าทาง"""
    
    def __init__(self, config: Config):
        self.config = config
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        # เปลี่ยนเป็นตรวจจับได้ 2 มือ
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
            max_num_hands=2  # ตรวจจับได้ 2 มือ
        )
        
        # State
        self.is_ready = False
        self.last_time = 0
        
        # State สำหรับการตรวจจับกำมือ 2 ข้าง
        self.last_fist_count = 0
        self.fist_delay_timer = 0
        
        # State สำหรับ Volume/Seek Preview
        self.pending_volume: Optional[int] = None
        self.pending_seek: Optional[int] = None
        
        # ตำแหน่งเริ่มต้นเมื่อกำมือ
        self.fist_start_x: Optional[float] = None
        self.fist_start_y: Optional[float] = None
        
        # ล็อคโหมดควบคุม (volume หรือ seek)
        self.locked_control_mode: Optional[str] = None
        
        # Threshold
        self.movement_threshold = 0.05  # 5% ของหน้าจอ
    
    def is_hand_open(self, hand) -> bool:
        """เช็คว่ามือแบหรือไม่ (ใช้ระยะห่างระหว่างข้อมือกับปลายนิ้ว)"""
        wrist = hand.landmark[0]
        middle_tip = hand.landmark[12]  # ปลายนิ้วกลาง
        
        # คำนวณระยะห่าง
        distance = ((middle_tip.x - wrist.x)**2 + (middle_tip.y - wrist.y)**2)**0.5
        
        # ถ้าระยะห่างมาก = แบมือ, ถ้าน้อย = กำมือ
        return distance > 0.2  # threshold สำหรับแบมือ
    
    def is_hand_closed(self, hand) -> bool:
        """เช็คว่ามือกำหรือไม่"""
        wrist = hand.landmark[0]
        middle_tip = hand.landmark[12]
        
        distance = ((middle_tip.x - wrist.x)**2 + (middle_tip.y - wrist.y)**2)**0.5
        
        return distance < 0.15  # threshold สำหรับกำมือ
    
    def is_left_hand(self, hand, handedness) -> bool:
        """เช็คว่าเป็นมือซ้ายหรือไม่"""
        # MediaPipe ให้ label เป็น "Left" หรือ "Right" (จากมุมมองของกล้อง)
        return handedness.classification[0].label == "Left"
    
    def get_hand_position(self, hand) -> Tuple[float, float]:
        """ดึงตำแหน่ง x, y ของมือ (ใช้ข้อมือเป็นจุดอ้างอิง)"""
        wrist = hand.landmark[0]
        return wrist.x, wrist.y
    
    def detect_two_hand_gesture(self, hands_data) -> Optional[Gesture]:
        """ตรวจจับท่าทาง 2 มือ (เพิ่มดีเลย์สำหรับกำมือ)"""
        if len(hands_data) != 2:
            self.last_fist_count = 0
            self.fist_delay_timer = 0
            return None
        
        # แยกมือซ้าย/ขวา
        left_hand = None
        right_hand = None
        
        for hand, handedness in hands_data:
            if self.is_left_hand(hand, handedness):
                left_hand = hand
            else:
                right_hand = hand
        
        if left_hand is None or right_hand is None:
            return None
        
        # เช็คสถานะมือ
        left_open = self.is_hand_open(left_hand)
        left_closed = self.is_hand_closed(left_hand)
        right_open = self.is_hand_open(right_hand)
        right_closed = self.is_hand_closed(right_hand)
        
        # ทั้ง 2 มือแบ → Ready
        if left_open and right_open:
            self.last_fist_count = 0
            self.fist_delay_timer = 0
            return Gesture.OPEN
        
        # ซ้ายแบ + ขวากำ → เพลงถัดไป
        if left_open and right_closed:
            return Gesture.SWIPE_RIGHT
        
        # ซ้ายกำ + ขวาแบ → เพลงก่อนหน้า
        if left_closed and right_open:
            return Gesture.SWIPE_LEFT
        
        # ทั้ง 2 มือกำ → Play/Pause (มีดีเลย์)
        if left_closed and right_closed:
            import time
            now = time.time()
            
            if self.last_fist_count == 0:
                # เริ่มนับดีเลย์
                self.fist_delay_timer = now
                self.last_fist_count = 2
            elif now - self.fist_delay_timer > 0.3:  # ดีเลย์ 0.3 วินาที
                return Gesture.FIST
        else:
            self.last_fist_count = 0
            self.fist_delay_timer = 0
        
        return None
    
    def calculate_volume_from_position(self, current_y: float) -> int:
        """คำนวณเสียงจากตำแหน่ง Y (0.0-1.0 → 100-0%)"""
        # Y = 0.0 (บน) → Volume 100%
        # Y = 1.0 (ล่าง) → Volume 0%
        volume = int((1.0 - current_y) * 100)
        return max(0, min(100, volume))
    
    def calculate_seek_from_position(self, current_x: float, duration_ms: int) -> int:
        """คำนวณตำแหน่งเพลงจากตำแหน่ง X (0.0-1.0)"""
        # X = 0.0 (ซ้าย) → 0%
        # X = 1.0 (ขวา) → 100%
        position_ms = int(current_x * duration_ms)
        return max(0, min(duration_ms, position_ms))
    
    def get_pending_volume(self) -> Optional[int]:
        """ดึงค่าเสียงที่รอส่ง"""
        return self.pending_volume
    
    def get_pending_seek(self) -> Optional[int]:
        """ดึงค่าการกรอที่รอส่ง"""
        return self.pending_seek
    
    def reset_pending_controls(self) -> None:
        """รีเซ็ตค่าที่รอส่ง"""
        self.pending_volume = None
        self.pending_seek = None
        self.fist_start_x = None
        self.fist_start_y = None
        self.locked_control_mode = None
    
    def detect_primary_movement(self, start_x: float, start_y: float, current_x: float, current_y: float) -> str:
        """ตรวจจับว่าขยับไปทิศทางไหนเป็นหลัก (แนวนอนหรือแนวตั้ง)"""
        dx = abs(current_x - start_x)
        dy = abs(current_y - start_y)
        
        # ถ้าขยับน้อยเกินไป ไม่นับ
        if dx < self.movement_threshold and dy < self.movement_threshold:
            return "none"
        
        # เปรียบเทียบว่าขยับแนวไหนมากกว่า
        if dx > dy:
            return "horizontal"  # ซ้าย-ขวา → Seek
        else:
            return "vertical"    # บน-ล่าง → Volume
    
    def detect_gesture(self, frame) -> Tuple[Gesture, any]:
        """ตรวจจับท่าทางจากภาพ"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        
        gesture = Gesture.NONE
        
        if result.multi_hand_landmarks and result.multi_handedness:
            num_hands = len(result.multi_hand_landmarks)
            
            # กรณีมี 2 มือ
            if num_hands == 2:
                hands_data = list(zip(result.multi_hand_landmarks, result.multi_handedness))
                two_hand_gesture = self.detect_two_hand_gesture(hands_data)
                
                if two_hand_gesture == Gesture.OPEN:
                    gesture = Gesture.OPEN
                    self.is_ready = True
                elif two_hand_gesture and self.is_ready:
                    gesture = two_hand_gesture
                else:
                    gesture = Gesture.WAITING if not self.is_ready else Gesture.NONE
            
            # กรณีมี 1 มือ - ควบคุม Volume/Seek
            elif num_hands == 1:
                hand = result.multi_hand_landmarks[0]
                
                if self.is_hand_open(hand):
                    gesture = Gesture.OPEN
                    self.is_ready = True
                elif self.is_ready and self.is_hand_closed(hand):
                    gesture = Gesture.NONE
                else:
                    gesture = Gesture.WAITING if not self.is_ready else Gesture.NONE
                    self.reset_pending_controls()
        else:
            self.is_ready = False
            self.reset_pending_controls()
        
        return gesture, result
    
    def should_execute(self, gesture: Gesture) -> bool:
        """เช็คว่าควรทำงานหรือไม่ (cooldown)"""
        now = time.time()
        if gesture in [Gesture.NONE, Gesture.WAITING, Gesture.OPEN]:
            return False
        
        if now - self.last_time > self.config.COOLDOWN:
            self.last_time = now
            return True
        
        return False
    
    def reset_state(self) -> None:
        """รีเซ็ตสถานะหลังใช้งาน"""
        self.is_ready = False
