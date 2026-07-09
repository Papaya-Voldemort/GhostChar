import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QObject, pyqtSignal

class AudioMonitor(QObject):
    # Emits volume levels scaled from 0.0 to 100.0
    level_changed = pyqtSignal(float)
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.stream = None
        self.current_device_index = None
        self.active = False

    def get_input_devices(self):
        try:
            devices = sd.query_devices()
            # sd.default.device returns (input_device_index, output_device_index)
            default_input_idx = sd.default.device[0]
            
            input_devices = []
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0:
                    name = d['name']
                    # Some device names might contain non-ascii characters or encoding issues
                    if isinstance(name, bytes):
                        name = name.decode('utf-8', errors='ignore')
                    is_default = (i == default_input_idx)
                    input_devices.append({
                        'index': i,
                        'name': name,
                        'is_default': is_default
                    })
            return input_devices
        except Exception as e:
            self.status_message.emit(f"Error querying audio devices: {e}")
            return []

    def start_monitoring(self, device_index=None):
        self.stop_monitoring()
        
        devices = self.get_input_devices()
        if not devices:
            self.status_message.emit("No audio input devices found.")
            return
            
        if device_index is None:
            # Try to find default device
            for d in devices:
                if d['is_default']:
                    device_index = d['index']
                    break
            if device_index is None and len(devices) > 0:
                device_index = devices[0]['index']
                
        if device_index is None:
            self.status_message.emit("Could not select an audio input device.")
            return
            
        self.current_device_index = device_index
        self.active = True
        
        def callback(indata, frames, time, status):
            if not self.active:
                return
            if status:
                # PortAudio status flag (e.g. input overflow/underflow)
                pass
            
            if len(indata) > 0:
                # Compute RMS (Root Mean Square) volume level
                rms = np.sqrt(np.mean(indata**2))
                # Map typical RMS values (0.0 to ~0.15 for voice) to 0.0 - 100.0 scale
                level = min(100.0, rms * 700.0)
                self.level_changed.emit(level)
            else:
                self.level_changed.emit(0.0)
                
        try:
            self.stream = sd.InputStream(
                device=device_index,
                channels=1,
                callback=callback,
                blocksize=1024,
                latency='low'
            )
            self.stream.start()
            self.status_message.emit(f"Audio monitoring started on device {device_index}.")
        except Exception as e:
            self.status_message.emit(f"Failed to start audio stream on device {device_index}: {e}")
            self.stream = None
            self.level_changed.emit(0.0)

    def stop_monitoring(self):
        self.active = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        self.level_changed.emit(0.0)
