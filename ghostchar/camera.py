import os
import sys
import time
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from ghostchar.virtual import VirtualCameraManager

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

# Fallback character ramp
DEFAULT_CHARS = [" ", ".", ",", "-", "~", ":", "i", "r", "s", "t", "l", "C", "O", "Z", "w", "m", "#", "8", "%", "@"]

# Color Themes mapping (Background, Text) in RGB
THEMES = {
    "Matrix Green": ((0, 10, 0), (0, 255, 0)),
    "Classic B&W": ((0, 0, 0), (255, 255, 255)),
    "Amber Terminal": ((15, 10, 0), (255, 170, 0)),
    "Cyberpunk Pink": ((20, 0, 30), (255, 0, 128)),
    "Ice Blue": ((0, 10, 20), (0, 191, 255)),
}

def list_video_devices():
    devices_list = []
    try:
        import AVFoundation
        device_types = []
        for name in [
            "AVCaptureDeviceTypeBuiltInWideAngleCamera",
            "AVCaptureDeviceTypeBuiltInTelephotoCamera",
            "AVCaptureDeviceTypeBuiltInUltraWideCamera",
            "AVCaptureDeviceTypeBuiltInDualCamera",
            "AVCaptureDeviceTypeBuiltInDualWideCamera",
            "AVCaptureDeviceTypeBuiltInTripleCamera",
            "AVCaptureDeviceTypeBuiltInTrueDepthCamera",
            "AVCaptureDeviceTypeContinuityCamera",
            "AVCaptureDeviceTypeDeskViewCamera",
            "AVCaptureDeviceTypeExternal",
            "AVCaptureDeviceTypeExternalUnknown"
        ]:
            if hasattr(AVFoundation, name):
                device_types.append(getattr(AVFoundation, name))
        
        session = AVFoundation.AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
            device_types,
            AVFoundation.AVMediaTypeVideo,
            AVFoundation.AVCaptureDevicePositionUnspecified
        )
        devices = session.devices()
        for idx, device in enumerate(devices):
            devices_list.append({
                'index': idx,
                'name': device.localizedName(),
                'unique_id': device.uniqueID()
            })
    except Exception as e:
        print(f"Error listing camera devices with AVFoundation discovery session: {e}")
        # Try deprecated fallback
        try:
            import AVFoundation
            devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo)
            for idx, device in enumerate(devices):
                devices_list.append({
                    'index': idx,
                    'name': device.localizedName(),
                    'unique_id': device.uniqueID()
                })
        except Exception as e2:
            print(f"Error listing camera devices with AVFoundation deprecated API: {e2}")

    # Fallback to OpenCV if AVFoundation returned nothing
    if not devices_list:
        for idx in range(5):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                devices_list.append({
                    'index': idx,
                    'name': f"Camera {idx}",
                    'unique_id': str(idx)
                })
                cap.release()
                
    return devices_list

class CameraConfig:
    def __init__(self):
        self.camera_index = 0
        self.cols = 100
        self.brightness = 1.0  # 0.1 to 3.0
        self.contrast = 1.0    # 0.1 to 3.0
        self.grayscale_mode = "Luminosity"  # Luminosity, Average, Desaturate
        self.engine = "ONNX ML Model"       # ONNX ML Model, Pixel Intensity
        
        # Determine base directory (handles running from source and PyInstaller bundle)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(script_dir)
            
        candidate = os.path.join(base_dir, "ascii_cam_model", "model.onnx")
        if os.path.exists(candidate):
            self.onnx_path = candidate
        else:
            self.onnx_path = os.path.join(base_dir, "ascii_cam_model", "model_quant.onnx")
            
        self.invert = False
        self.mirror = False
        self.theme = "Matrix Green"
        self.fps_limit = 30
        self.virtual_cam_active = False
        self.output_resolution = "1280x720"

    def copy(self):
        c = CameraConfig()
        c.camera_index = self.camera_index
        c.cols = self.cols
        c.brightness = self.brightness
        c.contrast = self.contrast
        c.grayscale_mode = self.grayscale_mode
        c.engine = self.engine
        c.onnx_path = self.onnx_path
        c.invert = self.invert
        c.mirror = self.mirror
        c.theme = self.theme
        c.fps_limit = self.fps_limit
        c.virtual_cam_active = self.virtual_cam_active
        c.output_resolution = self.output_resolution
        return c

def load_monospace_font(size):
    font_paths = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Monaco.ttf",
        "Courier",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def get_font_metrics(font):
    try:
        ascent, descent = font.getmetrics()
        char_h = ascent + descent
    except Exception:
        char_h = font.size
        
    try:
        char_w = font.getlength("A")
    except Exception:
        try:
            bbox = font.getbbox("A")
            char_w = bbox[2] - bbox[0]
        except Exception:
            char_w = font.size * 0.5
            
    return char_w, char_h

def get_font_aspect():
    font = load_monospace_font(20)
    char_w, char_h = get_font_metrics(font)
    return char_w / char_h

def get_best_font(cols, rows, target_w, target_h):
    # Estimate height of cell based on target height and row count
    cell_h = target_h / rows
    font_size = max(6, int(cell_h))
    
    font = load_monospace_font(font_size)
    char_w, char_h = get_font_metrics(font)
        
    # Scale down if the grid exceeds the target width
    total_w = char_w * cols
    if total_w > target_w:
        scale = target_w / total_w
        font_size = max(6, int(font_size * scale))
        font = load_monospace_font(font_size)
        char_w, char_h = get_font_metrics(font)
            
    return font, char_w, char_h

class CameraWorker(QThread):
    # Emits (preview_rgb_array, stats_dict)
    frame_ready = pyqtSignal(object, dict)
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mutex = QMutex()
        self.running = False
        self.config = CameraConfig()
        
        # ONNX session cache
        self.ort_session = None
        self.loaded_onnx_path = ""
        self.input_name = ""
        self.output_name = ""
        
        # Character vocab setup
        self.ascii_chars = DEFAULT_CHARS
        self.ascii_chars_arr = np.array([ord(c) for c in self.ascii_chars], dtype=np.uint8)

    def update_config(self, new_config):
        with QMutexLocker(self.mutex):
            # Check if camera index changed
            cam_changed = (self.config.camera_index != new_config.camera_index)
            self.config = new_config.copy()
            
            # Re-map ASCII chars if invert changes
            chars = list(DEFAULT_CHARS)
            if self.config.invert:
                chars = chars[::-1]
            self.ascii_chars = chars
            self.ascii_chars_arr = np.array([ord(c) for c in chars], dtype=np.uint8)
            
        return cam_changed

    def stop(self):
        with QMutexLocker(self.mutex):
            self.running = False
        self.wait()

    def run(self):
        self.running = True
        
        cap = None
        vcam = VirtualCameraManager()
        current_camera_index = -1
        
        # Find default model if not configured
        with QMutexLocker(self.mutex):
            if not self.config.onnx_path:
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                    base_dir = sys._MEIPASS
                else:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    base_dir = os.path.dirname(script_dir)
                candidate = os.path.join(base_dir, "ascii_cam_model", "model.onnx")
                if os.path.exists(candidate):
                    self.config.onnx_path = candidate
                else:
                    self.config.onnx_path = os.path.join(base_dir, "ascii_cam_model", "model_quant.onnx")
        
        while True:
            # Check if we should quit
            with QMutexLocker(self.mutex):
                if not self.running:
                    break
                cfg = self.config.copy()
            
            # (Re)open video capture if camera index changed
            if cap is None or current_camera_index != cfg.camera_index:
                if cap is not None:
                    cap.release()
                self.status_message.emit(f"Opening Camera {cfg.camera_index}...")
                cap = cv2.VideoCapture(cfg.camera_index)
                if not cap.isOpened():
                    self.status_message.emit(f"Error: Could not open Camera {cfg.camera_index}.")
                    time.sleep(1.0)
                    continue
                current_camera_index = cfg.camera_index
                self.status_message.emit("Camera initialized successfully.")
                
            # Read frame
            ret, bgr_frame = cap.read()
            if not ret:
                self.status_message.emit("Failed to capture frame from webcam.")
                time.sleep(0.1)
                continue
                
            if cfg.mirror:
                bgr_frame = cv2.flip(bgr_frame, 1)
                
            start_time = time.time()
            
            # 1. Grayscale Conversion
            h_orig, w_orig = bgr_frame.shape[:2]
            aspect_ratio = w_orig / h_orig
            
            # Calculate rows dynamically based on the measured monospace font aspect ratio and webcam aspect ratio
            cols = cfg.cols
            font_aspect = get_font_aspect()
            rows = int(round(cols * font_aspect / aspect_ratio))
            rows = max(4, rows)
            
            # Pre-conversion to grayscale
            if cfg.grayscale_mode == "Luminosity":
                # Rec. 601 luminosity vector
                gray = np.dot(bgr_frame[..., :3], [0.114, 0.587, 0.299])
            elif cfg.grayscale_mode == "Average":
                gray = bgr_frame.mean(axis=2)
            elif cfg.grayscale_mode == "Desaturate":
                mx = bgr_frame.max(axis=2)
                mn = bgr_frame.min(axis=2)
                gray = (mx + mn) / 2.0
            else:
                gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
                
            # Normalize to 0.0 - 1.0 float32
            gray = gray.astype(np.float32) / 255.0
            
            # 2. Apply Brightness & Contrast
            if cfg.brightness != 1.0:
                gray = np.clip(gray * cfg.brightness, 0.0, 1.0)
            if cfg.contrast != 1.0:
                gray = np.clip((gray - 0.5) * cfg.contrast + 0.5, 0.0, 1.0)
                
            preprocess_time = (time.time() - start_time) * 1000.0
            
            # 3. Model Inference or Intensity Mapping
            inference_start = time.time()
            
            # Target width/height for character cells
            target_w = cols * 8
            target_h = rows * 16
            
            # Resize image to match character patches
            gray_resized = cv2.resize(gray, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            
            # Slice into patches: (rows * cols, 16, 8, 1) in 0.05ms
            patches = gray_resized.reshape(rows, 16, cols, 8).transpose(0, 2, 1, 3).reshape(rows * cols, 16, 8, 1)
            
            # Run inference
            if cfg.engine == "ONNX ML Model" and ONNX_AVAILABLE:
                # Lazy load session
                if self.ort_session is None or self.loaded_onnx_path != cfg.onnx_path:
                    if os.path.exists(cfg.onnx_path):
                        try:
                            self.status_message.emit(f"Loading ONNX Model from {os.path.basename(cfg.onnx_path)}...")
                            # Use CPU provider for absolute compatibility, threads=4 for high speed
                            opts = ort.SessionOptions()
                            opts.intra_op_num_threads = 4
                            self.ort_session = ort.InferenceSession(cfg.onnx_path, sess_options=opts, providers=['CPUExecutionProvider'])
                            self.input_name = self.ort_session.get_inputs()[0].name
                            self.output_name = self.ort_session.get_outputs()[0].name
                            self.loaded_onnx_path = cfg.onnx_path
                            self.status_message.emit("ONNX model loaded successfully.")
                        except Exception as e:
                            self.status_message.emit(f"Error loading ONNX model: {e}. Falling back to Intensity mode.")
                            self.ort_session = None
                    else:
                        self.status_message.emit("ONNX model file not found. Falling back to Intensity mode.")
                        self.ort_session = None
                
                if self.ort_session is not None:
                    # Run session
                    outputs = self.ort_session.run([self.output_name], {self.input_name: patches})[0]
                    predicted_classes = np.argmax(outputs, axis=1)
                else:
                    # Fallback to Intensity
                    patch_averages = patches.mean(axis=(1, 2, 3))
                    predicted_classes = (patch_averages * (len(self.ascii_chars) - 1)).astype(np.int32)
            else:
                # Intensity Mapping
                patch_averages = patches.mean(axis=(1, 2, 3))
                predicted_classes = (patch_averages * (len(self.ascii_chars) - 1)).astype(np.int32)
                
            inference_time = (time.time() - inference_start) * 1000.0
            
            # 4. Map and Render to Pillow
            render_start = time.time()
            
            # Map predictions to characters
            predicted_classes = np.clip(predicted_classes, 0, len(self.ascii_chars) - 1)
            mapped_chars = self.ascii_chars_arr[predicted_classes]
            
            # Decode into lines of string
            lines = []
            for r in range(rows):
                start = r * cols
                line_bytes = mapped_chars[start : start + cols]
                lines.append(line_bytes.tobytes().decode('ascii'))
                
            # Parse output resolution
            try:
                res_w, res_h = map(int, cfg.output_resolution.split("x"))
            except Exception:
                res_w, res_h = 1280, 720
                
            # Theme Colors
            bg_color, text_color = THEMES.get(cfg.theme, ((0, 0, 0), (255, 255, 255)))
            
            # Create output canvas
            out_img = Image.new("RGB", (res_w, res_h), bg_color)
            draw = ImageDraw.Draw(out_img)
            
            # Find best font size and metrics
            font, char_w, char_h = get_best_font(cols, rows, res_w, res_h)
            
            # Render lines to canvas (vectorized line-by-line drawing)
            # Center vertically if there is extra space
            total_text_h = char_h * rows
            y_offset = max(0, (res_h - total_text_h) // 2)
            
            # Center horizontally if needed
            total_text_w = char_w * cols
            x_offset = max(0, (res_w - total_text_w) // 2)
            
            for r in range(rows):
                draw.text((x_offset, y_offset + r * char_h), lines[r], font=font, fill=text_color)
                
            # Convert to numpy RGB for display and transmission
            rgb_output = np.array(out_img, dtype=np.uint8)
            
            # Handle streaming to Virtual Camera asynchronously
            if cfg.virtual_cam_active:
                if vcam.cam is None or vcam.width != res_w or vcam.height != res_h or vcam.fps != cfg.fps_limit:
                    self.status_message.emit("Opening virtual camera stream...")
                    ok, msg = vcam.start(res_w, res_h, cfg.fps_limit)
                    self.status_message.emit(msg)
                    if not ok:
                        # Turn off flag on error to prevent infinite restart loop
                        with QMutexLocker(self.mutex):
                            self.config.virtual_cam_active = False
                if vcam.cam is not None:
                    vcam.send_frame(rgb_output)
            else:
                if vcam.cam is not None:
                    self.status_message.emit("Stopping virtual camera stream.")
                    vcam.stop()
            
            render_time = (time.time() - render_start) * 1000.0
            total_time = (time.time() - start_time) * 1000.0
            
            fps = 1000.0 / total_time if total_time > 0 else 0
            
            stats = {
                "preprocess": preprocess_time,
                "inference": inference_time,
                "render": render_time,
                "total": total_time,
                "fps": fps,
                "rows": rows,
                "cols": cols,
            }
            
            # Emit output
            self.frame_ready.emit(rgb_output, stats)
            
            # Sleep to match target FPS
            delay = 1.0 / cfg.fps_limit
            elapsed = time.time() - start_time
            if elapsed < delay:
                time.sleep(delay - elapsed)
                
        # Cleanup
        if cap is not None:
            cap.release()
        vcam.stop()
        self.status_message.emit("Camera thread stopped.")
