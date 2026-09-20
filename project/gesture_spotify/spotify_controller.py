"""
Spotify Controller - จัดการการควบคุม Spotify API
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config


class SpotifyController:
    """จัดการการควบคุม Spotify"""
    
    def __init__(self, config: Config):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            redirect_uri=config.REDIRECT_URI,
            scope=config.SCOPE
        ))
    
    def play_pause(self) -> None:
        """เล่น/หยุดเพลง"""
        try:
            playback = self.sp.current_playback()
            if playback and playback['is_playing']:
                self.sp.pause_playback()
                print("⏸ Pause")
            else:
                self.sp.start_playback()
                print("▶ Play")
        except Exception as e:
            if "No active device" in str(e):
                print("💡 ไม่พบ active device - กำลังเปิดเพลงให้...")
                if self._activate_device():
                    # ลองเล่นอีกครั้งหลัง activate
                    try:
                        self.sp.start_playback()
                        print("▶ Play")
                    except:
                        print("❌ ไม่สามารถเล่นเพลงได้")
                else:
                    print("❌ ไม่พบ Spotify device ใดๆ - กรุณาเปิด Spotify ก่อน")
                    self._show_available_devices()
            else:
                print(f"❌ Error play/pause: {e}")
    
    def _activate_device(self) -> bool:
        """เปิด device ที่มีให้ active"""
        try:
            devices = self.sp.devices()
            if devices and devices['devices']:
                # หา device แรกที่พบ
                device_id = devices['devices'][0]['id']
                device_name = devices['devices'][0]['name']
                
                # Transfer playback ไปที่ device นั้น
                self.sp.transfer_playback(device_id, force_play=False)
                print(f"🔄 เปลี่ยนไปใช้ device: {device_name}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error activating device: {e}")
            return False
    
    def _show_available_devices(self) -> None:
        """แสดง devices ที่มี"""
        try:
            devices = self.sp.devices()
            if devices and devices['devices']:
                print("\n📱 Devices ที่พบ:")
                for device in devices['devices']:
                    status = "🟢 Active" if device['is_active'] else "⚪ Inactive"
                    print(f"  {status} - {device['name']} ({device['type']})")
            else:
                print("📱 ไม่พบ device ใดๆ - กรุณาเปิด Spotify")
        except:
            pass
    
    def next_track(self) -> None:
        """เพลงถัดไป"""
        try:
            self.sp.next_track()
            print("⏭ Next Track")
        except Exception as e:
            if "No active device" in str(e):
                print("💡 กำลัง activate device...")
                if self._activate_device():
                    try:
                        self.sp.next_track()
                        print("⏭ Next Track")
                    except:
                        pass
            else:
                print(f"❌ Error next: {e}")
    
    def previous_track(self) -> None:
        """เพลงก่อนหน้า"""
        try:
            self.sp.previous_track()
            print("⏮ Previous Track")
        except Exception as e:
            if "No active device" in str(e):
                print("💡 กำลัง activate device...")
                if self._activate_device():
                    try:
                        self.sp.previous_track()
                        print("⏮ Previous Track")
                    except:
                        pass
            else:
                print(f"❌ Error previous: {e}")

