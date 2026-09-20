"""
Gesture types enumeration
"""
from enum import Enum


class Gesture(Enum):
    """ประเภทของท่าทาง"""
    OPEN = "open"
    FIST = "fist"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    NONE = "none"
    WAITING = "waiting"
