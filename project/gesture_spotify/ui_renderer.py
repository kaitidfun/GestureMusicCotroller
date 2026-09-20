"""
UI Renderer - จัดการการแสดงผล
"""
import cv2
from gesture import Gesture


class UIRenderer:
    """จัดการการแสดงผล UI"""
    
    @staticmethod
    def draw_landmarks(frame, hand_landmarks, mp_hands, mp_draw) -> None:
        """วาด landmarks บนภาพ"""
        for handLms in hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
    
    @staticmethod
    def draw_status(frame, is_ready: bool, gesture: Gesture, pending_volume=None, pending_seek=None) -> None:
        """วาดสถานะและท่าทาง"""
        status = "🟢 READY" if is_ready else "⚪ Waiting..."
        color = (0, 255, 0) if is_ready else (200, 200, 200)
        
        cv2.putText(frame, f"Status: {status}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"Gesture: {gesture.value}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # แสดงค่า preview ของ volume และ seek
        if pending_volume is not None:
            cv2.putText(frame, f"Volume: {pending_volume}%", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        if pending_seek is not None:
            seek_seconds = pending_seek // 1000
            minutes = seek_seconds // 60
            seconds = seek_seconds % 60
            cv2.putText(frame, f"Seek: {minutes}:{seconds:02d}", (10, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
