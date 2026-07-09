import numpy as np
import pyvirtualcam

class VirtualCameraManager:
    def __init__(self):
        self.cam = None
        self.width = None
        self.height = None
        self.fps = None

    def start(self, width, height, fps):
        self.stop()
        try:
            # On macOS, pyvirtualcam automatically detects and links to OBS Virtual Camera
            self.cam = pyvirtualcam.Camera(width=width, height=height, fps=fps)
            self.width = width
            self.height = height
            self.fps = fps
            return True, f"Connected to virtual camera: {self.cam.device}"
        except Exception as e:
            err_msg = str(e)
            # Make the error message cleaner for the user if it's a known error
            if "Virtual camera not found" in err_msg or "No virtual camera found" in err_msg:
                err_msg = "Virtual camera device not found. Please ensure OBS Studio is installed."
            return False, err_msg

    def send_frame(self, rgb_frame):
        if self.cam is None:
            return False

        h, w = rgb_frame.shape[:2]
        if w != self.width or h != self.height:
            # Dimension mismatch (should not happen if CameraWorker output resolution matches)
            return False

        try:
            # pyvirtualcam expects RGB format (0-255 uint8)
            self.cam.send(rgb_frame)
            return True
        except Exception as e:
            print(f"Error sending frame to virtual camera: {e}")
            self.stop()
            return False

    def stop(self):
        if self.cam is not None:
            try:
                self.cam.close()
            except Exception:
                pass
            self.cam = None
            self.width = None
            self.height = None
            self.fps = None
