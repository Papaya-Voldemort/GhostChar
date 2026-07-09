import os
import sys
import numpy as np
import cv2
from PyQt6.QtCore import Qt, QSize, pyqtSlot, QTimer
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont, QAction
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider,
    QCheckBox, QPushButton, QScrollArea, QFrame, QApplication, QProgressBar,
    QGraphicsDropShadowEffect
)
from ghostchar.camera import CameraConfig, CameraWorker, THEMES, list_video_devices
from ghostchar.audio import AudioMonitor

class SettingsWindow(QWidget):
    def __init__(self, camera_worker: CameraWorker, audio_monitor: AudioMonitor, parent=None):
        super().__init__(parent)
        self.worker = camera_worker
        self.audio_monitor = audio_monitor
        self.pinned = False
        self.viewport_window = None
        
        # Window Configuration
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(440, 700)
        
        # UI Styling Setup
        self.setup_ui()
        
        # Soft Drop Shadow for floating menu-bar look
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(self.shadow)
        
        # Connect worker signals
        self.worker.frame_ready.connect(self.on_frame_ready)
        self.worker.status_message.connect(self.on_status_message)
        self.audio_monitor.level_changed.connect(self.on_audio_level_changed)
        self.audio_monitor.status_message.connect(self.on_status_message)
        
        # Populate inputs
        self.populate_devices()
        self.apply_config_to_ui()
        
        # Audio monitoring auto-start
        self.audio_monitor.start_monitoring(self.audio_combo.currentData())

    def setup_ui(self):
        # Master Layout (Transparent background wrapper)
        master_layout = QVBoxLayout(self)
        master_layout.setContentsMargins(10, 10, 10, 10)
        
        # Main Glassmorphic Container
        self.container = QFrame(self)
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
            QFrame#Container {
                background-color: rgba(28, 28, 32, 245);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
            QLabel {
                color: #e2e8f0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 13px;
            }
            QComboBox {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #f1f5f9;
                padding: 5px 10px;
                font-size: 12px;
                min-height: 28px;
                max-width: 180px;
            }
            QComboBox:hover {
                background-color: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.2);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 0px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox::down-arrow {
                image: url("data:image/svg+xml;utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='white'%3E%3Cpath%20d='M7%2010l5%205%205-5z'/%3E%3C/svg%3E");
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1e;
                color: #f1f5f9;
                selection-background-color: #3b82f6;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 4px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #60a5fa);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 14px;
                height: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #f1f5f9;
            }
            QCheckBox {
                color: #e2e8f0;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
            QCheckBox::indicator:hover {
                background-color: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.2);
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
                image: url("data:image/svg+xml;utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='white'%3E%3Cpath%20d='M9%2016.17L4.83%2012l-1.42%201.41L9%2019%2021%207l-1.41-1.41z'/%3E%3C/svg%3E");
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #f1f5f9;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.12);
                border-color: #3b82f6;
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.04);
            }
            QPushButton#CloseBtn {
                background: transparent;
                border: none;
                color: #9ca3af;
                font-size: 16px;
                font-weight: bold;
                padding: 4px;
            }
            QPushButton#CloseBtn:hover {
                color: #f3f4f6;
            }
            QPushButton#QuitBtn {
                background-color: rgba(239, 68, 68, 0.12);
                border-color: rgba(239, 68, 68, 0.25);
                color: #f87171;
            }
            QPushButton#QuitBtn:hover {
                background-color: rgba(239, 68, 68, 0.22);
                border-color: #ef4444;
            }
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 3px;
                height: 6px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #34d399);
                border-radius: 3px;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        
        # 1. HEADER
        header_layout = QHBoxLayout()
        
        title_label = QLabel("GhostChar 👻", self)
        title_font = QFont("-apple-system", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        
        # Pinned State Button
        self.pin_btn = QPushButton("Pin 📌", self)
        self.pin_btn.setCheckable(True)
        self.pin_btn.setFixedSize(65, 26)
        self.pin_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 2px 6px;
                border-radius: 6px;
            }
            QPushButton:checked {
                background-color: rgba(59, 130, 246, 0.2);
                border-color: #3b82f6;
                color: #60a5fa;
            }
        """)
        self.pin_btn.clicked.connect(self.toggle_pinned)
        
        close_btn = QPushButton("✕", self)
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(26, 26)
        close_btn.clicked.connect(self.hide)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.pin_btn)
        header_layout.addWidget(close_btn)
        container_layout.addLayout(header_layout)
        
        # 2. LIVE PREVIEW CANVAS
        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(388, 218)
        self.preview_label.setStyleSheet("""
            background-color: #000000;
            border: 1px solid rgba(80, 80, 100, 100);
            border-radius: 8px;
        """)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.preview_label)
        
        # Performance overlay log
        self.stats_label = QLabel("Initializing camera stream...", self)
        self.stats_label.setStyleSheet("color: #888896; font-size: 11px;")
        container_layout.addWidget(self.stats_label)

        # Viewport Button
        self.viewport_btn = QPushButton("📺 Open Standalone Viewport", self)
        self.viewport_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(59, 130, 246, 0.15);
                border: 1px solid rgba(59, 130, 246, 0.3);
                color: #60a5fa;
                font-weight: bold;
                padding: 8px;
                border-radius: 8px;
                font-size: 12px;
                margin-top: 6px;
                margin-bottom: 6px;
            }
            QPushButton:hover {
                background-color: rgba(59, 130, 246, 0.25);
                border-color: #3b82f6;
            }
        """)
        self.viewport_btn.clicked.connect(self.open_viewport)
        container_layout.addWidget(self.viewport_btn)
        
        # Virtual Camera Help Banner (collapsible warning)
        self.vcam_banner = QFrame(self)
        self.vcam_banner.setObjectName("VCamBanner")
        self.vcam_banner.setStyleSheet("""
            QFrame#VCamBanner {
                background-color: rgba(245, 158, 11, 0.12);
                border: 1px solid rgba(245, 158, 11, 0.3);
                border-radius: 10px;
            }
            QLabel {
                color: #fbbf24;
                font-size: 11px;
                background: transparent;
            }
        """)
        vcam_banner_layout = QVBoxLayout(self.vcam_banner)
        vcam_banner_layout.setContentsMargins(10, 10, 10, 10)
        
        self.vcam_banner_text = QLabel(
            "⚠️ Virtual camera driver not active or in-use.\n\n"
            "1. Ensure the OBS Virtual Camera driver is registered on your system. You can install OBS Studio to get this driver.\n"
            "2. The OBS application does NOT need to be open. If OBS is open, make sure 'Start Virtual Camera' is turned OFF in OBS so GhostChar can control it.\n"
            "3. If you still see this, try toggling 'Stream to Virtual Camera' off and on.", self
        )
        self.vcam_banner_text.setWordWrap(True)
        vcam_banner_layout.addWidget(self.vcam_banner_text)
        self.vcam_banner.hide() # Hidden by default
        container_layout.addWidget(self.vcam_banner)
        
        # 3. SCROLL AREA FOR SETTINGS
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(80, 80, 100, 100);
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 8, 0, 8)
        scroll_layout.setSpacing(14)
        
        # SECTION: INPUT DEVICES
        devices_group = self.create_section("INPUT DEVICES", scroll_layout)
        
        self.cam_combo = QComboBox(self)
        self.cam_combo.currentIndexChanged.connect(self.on_cam_changed)
        devices_group.addRow("Input Camera", self.cam_combo)
        
        self.audio_combo = QComboBox(self)
        self.audio_combo.currentIndexChanged.connect(self.on_audio_changed)
        devices_group.addRow("Input Microphone", self.audio_combo)
        
        self.audio_level_bar = QProgressBar(self)
        self.audio_level_bar.setRange(0, 100)
        self.audio_level_bar.setValue(0)
        self.audio_level_bar.setTextVisible(False)
        devices_group.addRow("Mic Level", self.audio_level_bar)
        
        # SECTION: ASCII PROCESSING
        ascii_group = self.create_section("ASCII PREPROCESSING", scroll_layout)
        
        # Resolution Cols
        self.cols_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.cols_slider.setRange(40, 160)
        self.cols_slider.setValue(100)
        self.cols_val = QLabel("100 cols", self)
        self.cols_val.setFixedWidth(60)
        self.cols_slider.valueChanged.connect(self.on_cols_changed)
        ascii_group.addRowWidget("Grid Resolution", self.cols_slider, self.cols_val)
        
        # Brightness
        self.bright_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.bright_slider.setRange(10, 300) # Mapping 0.1 to 3.0
        self.bright_slider.setValue(100)
        self.bright_val = QLabel("1.0x", self)
        self.bright_val.setFixedWidth(60)
        self.bright_slider.valueChanged.connect(self.on_bright_changed)
        ascii_group.addRowWidget("Brightness", self.bright_slider, self.bright_val)
        
        # Contrast
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.contrast_slider.setRange(10, 300) # Mapping 0.1 to 3.0
        self.contrast_slider.setValue(100)
        self.contrast_val = QLabel("1.0x", self)
        self.contrast_val.setFixedWidth(60)
        self.contrast_slider.valueChanged.connect(self.on_contrast_changed)
        ascii_group.addRowWidget("Contrast", self.contrast_slider, self.contrast_val)
        
        # Grayscale mode
        self.gray_combo = QComboBox(self)
        self.gray_combo.addItems(["Luminosity", "Average", "Desaturate"])
        self.gray_combo.currentIndexChanged.connect(self.on_gray_mode_changed)
        ascii_group.addRow("Grayscale Formula", self.gray_combo)
        
        # SECTION: ENGINE & RENDERING
        engine_group = self.create_section("ENGINE & THEME", scroll_layout)
        
        # Processing engine
        self.engine_combo = QComboBox(self)
        self.engine_combo.addItems(["ONNX ML Model", "Pixel Intensity"])
        self.engine_combo.currentIndexChanged.connect(self.on_engine_changed)
        engine_group.addRow("ASCII Engine", self.engine_combo)
        
        # Theme dropdown
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        engine_group.addRow("Color Theme", self.theme_combo)
        
        # Checkboxes
        self.invert_check = QCheckBox("Invert Character Density", self)
        self.invert_check.stateChanged.connect(self.on_invert_changed)
        engine_group.addRow("", self.invert_check)
        
        self.mirror_check = QCheckBox("Mirror Camera Feed", self)
        self.mirror_check.stateChanged.connect(self.on_mirror_changed)
        engine_group.addRow("", self.mirror_check)
        
        # SECTION: VIRTUAL CAMERA
        vcam_group = self.create_section("VIRTUAL CAMERA OUTPUT", scroll_layout)
        
        # Output Resolution
        self.res_combo = QComboBox(self)
        self.res_combo.addItems(["640x480", "1280x720", "1920x1080"])
        self.res_combo.setCurrentText("1280x720")
        self.res_combo.currentIndexChanged.connect(self.on_res_changed)
        vcam_group.addRow("V-Cam Resolution", self.res_combo)
        
        # FPS Limit
        self.fps_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.fps_slider.setRange(5, 60)
        self.fps_slider.setValue(30)
        self.fps_val = QLabel("30 FPS", self)
        self.fps_val.setFixedWidth(60)
        self.fps_slider.valueChanged.connect(self.on_fps_changed)
        vcam_group.addRowWidget("FPS Target", self.fps_slider, self.fps_val)
        
        # Virtual Camera active checkbox
        self.vcam_active_check = QCheckBox("Stream to Virtual Camera", self)
        self.vcam_active_check.stateChanged.connect(self.on_vcam_active_changed)
        vcam_group.addRow("", self.vcam_active_check)
        
        scroll.setWidget(scroll_widget)
        container_layout.addWidget(scroll)
        
        # 4. FOOTER LOG & EXIT
        footer_layout = QHBoxLayout()
        
        self.status_bar = QLabel("System idle", self)
        self.status_bar.setStyleSheet("color: #6b7280; font-size: 11px;")
        
        quit_btn = QPushButton("Quit App", self)
        quit_btn.setObjectName("QuitBtn")
        quit_btn.clicked.connect(self.quit_application)
        
        footer_layout.addWidget(self.status_bar)
        footer_layout.addStretch()
        footer_layout.addWidget(quit_btn)
        container_layout.addLayout(footer_layout)
        
        master_layout.addWidget(self.container)

    def create_section(self, title, parent_layout):
        sect = SettingsSection(title)
        parent_layout.addWidget(sect)
        return sect

    def toggle_pinned(self):
        self.pinned = self.pin_btn.isChecked()
        if self.pinned:
            self.pin_btn.setText("Pinned 📌")
        else:
            self.pin_btn.setText("Pin 📌")
        # Regain focus
        self.setFocus()

    def open_viewport(self):
        if self.viewport_window is None:
            self.viewport_window = ViewportWindow()
        self.viewport_window.show()
        self.viewport_window.raise_()
        self.viewport_window.activateWindow()

    def focusOutEvent(self, event):
        # Auto-hide if not pinned and we lost focus to outside our app window
        if not self.pinned:
            # We delay check slightly to avoid closing on combo box dropdown interactions
            QTimer.singleShot(150, self.check_focus_loss)

    def check_focus_loss(self):
        if self.pinned or not self.isVisible():
            return
        # If the active window isn't this settings panel, hide it
        if not self.isActiveWindow():
            focused_widget = QApplication.focusWidget()
            if focused_widget and self.isAncestorOf(focused_widget):
                # Gained focus on child component, don't hide
                return
            self.hide()

    def populate_devices(self):
        # Scan cameras
        self.cam_combo.clear()
        cams = list_video_devices()
        for cam in cams:
            self.cam_combo.addItem(cam['name'], cam['index'])
                
        # Scan microphones
        self.audio_combo.clear()
        microphones = self.audio_monitor.get_input_devices()
        if not microphones:
            self.audio_combo.addItem("No microphones found", -1)
        else:
            for mic in microphones:
                suffix = " (Default)" if mic['is_default'] else ""
                self.audio_combo.addItem(f"{mic['name']}{suffix}", mic['index'])
                if mic['is_default']:
                    self.audio_combo.setCurrentIndex(self.audio_combo.count() - 1)

    def apply_config_to_ui(self):
        # Reads configuration from worker and initializes sliders/toggles
        cfg = self.worker.config
        
        # Camera selection
        cam_idx = self.cam_combo.findData(cfg.camera_index)
        if cam_idx != -1:
            self.cam_combo.setCurrentIndex(cam_idx)
            
        self.cols_slider.setValue(cfg.cols)
        self.cols_val.setText(f"{cfg.cols} cols")
        
        self.bright_slider.setValue(int(cfg.brightness * 100))
        self.bright_val.setText(f"{cfg.brightness:.2f}x")
        
        self.contrast_slider.setValue(int(cfg.contrast * 100))
        self.contrast_val.setText(f"{cfg.contrast:.2f}x")
        
        self.gray_combo.setCurrentText(cfg.grayscale_mode)
        self.engine_combo.setCurrentText(cfg.engine)
        self.theme_combo.setCurrentText(cfg.theme)
        self.invert_check.setChecked(cfg.invert)
        self.mirror_check.setChecked(cfg.mirror)
        
        self.res_combo.setCurrentText(cfg.output_resolution)
        self.fps_slider.setValue(cfg.fps_limit)
        self.fps_val.setText(f"{cfg.fps_limit} FPS")
        self.vcam_active_check.setChecked(cfg.virtual_cam_active)

    def get_current_ui_config(self) -> CameraConfig:
        cfg = self.worker.config.copy()
        cfg.camera_index = self.cam_combo.currentData() if self.cam_combo.currentData() is not None else 0
        cfg.cols = self.cols_slider.value()
        cfg.brightness = self.bright_slider.value() / 100.0
        cfg.contrast = self.contrast_slider.value() / 100.0
        cfg.grayscale_mode = self.gray_combo.currentText()
        cfg.engine = self.engine_combo.currentText()
        cfg.theme = self.theme_combo.currentText()
        cfg.invert = self.invert_check.isChecked()
        cfg.mirror = self.mirror_check.isChecked()
        cfg.output_resolution = self.res_combo.currentText()
        cfg.fps_limit = self.fps_slider.value()
        cfg.virtual_cam_active = self.vcam_active_check.isChecked()
        return cfg

    def push_config_to_worker(self):
        new_cfg = self.get_current_ui_config()
        cam_changed = self.worker.update_config(new_cfg)
        if cam_changed:
            self.status_bar.setText("Re-initializing camera...")

    # UI SLOT CALLBACKS
    def on_cam_changed(self):
        self.push_config_to_worker()

    def on_audio_changed(self):
        mic_idx = self.audio_combo.currentData()
        if mic_idx is not None and mic_idx != -1:
            self.audio_monitor.start_monitoring(mic_idx)

    def on_cols_changed(self, val):
        self.cols_val.setText(f"{val} cols")
        self.push_config_to_worker()

    def on_bright_changed(self, val):
        self.bright_val.setText(f"{val/100.0:.2f}x")
        self.push_config_to_worker()

    def on_contrast_changed(self, val):
        self.contrast_val.setText(f"{val/100.0:.2f}x")
        self.push_config_to_worker()

    def on_gray_mode_changed(self):
        self.push_config_to_worker()

    def on_engine_changed(self):
        self.push_config_to_worker()

    def on_theme_changed(self):
        self.push_config_to_worker()

    def on_invert_changed(self):
        self.push_config_to_worker()

    def on_mirror_changed(self):
        self.push_config_to_worker()

    def on_res_changed(self):
        self.push_config_to_worker()

    def on_fps_changed(self, val):
        self.fps_val.setText(f"{val} FPS")
        self.push_config_to_worker()

    def on_vcam_active_changed(self, state):
        self.push_config_to_worker()

    # CORE SYSTEM EVENT HANDLERS
    @pyqtSlot(object, dict)
    def on_frame_ready(self, frame_np, stats):
        # Display the live preview of ASCII canvas
        h, w, c = frame_np.shape
        q_img = QImage(frame_np.data, w, h, w * c, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        # Scale to fit layout box
        scaled = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        self.preview_label.setPixmap(scaled)
        
        # Also update standalone viewport if visible
        if self.viewport_window and self.viewport_window.isVisible():
            self.viewport_window.update_frame(frame_np)
        
        # Update Stats HUD labels
        stats_text = (
            f"Resolution: {stats['cols']}x{stats['rows']} | "
            f"Pre: {stats['preprocess']:.1f}ms | "
            f"Model: {stats['inference']:.1f}ms | "
            f"Render: {stats['render']:.1f}ms | "
            f"FPS: {stats['fps']:.1f}"
        )
        self.stats_label.setText(stats_text)
        
        # Sync virtual camera active checkbox in case the worker turned it off on error
        # (e.g. driver not installed)
        if not self.worker.config.virtual_cam_active and self.vcam_active_check.isChecked():
            self.vcam_active_check.setChecked(False)

    @pyqtSlot(str)
    def on_status_message(self, msg):
        self.status_bar.setText(msg)
        
        # Display/hide the help banner based on errors
        if "Virtual camera device not found" in msg or "Virtual Cam Error" in msg:
            self.vcam_banner.show()
        elif "Connected to virtual camera" in msg:
            self.vcam_banner.hide()

    @pyqtSlot(float)
    def on_audio_level_changed(self, val):
        self.audio_level_bar.setValue(int(val))

    def quit_application(self):
        self.audio_monitor.stop_monitoring()
        self.worker.stop()
        if self.viewport_window:
            self.viewport_window.close()
        QApplication.quit()
        sys.exit(0)

class SettingsSection(QWidget):
    # Dynamic settings accordion collapsible row container
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        
        # Section title divider
        title_lbl = QLabel(title.upper(), self)
        title_lbl.setStyleSheet("""
            color: #3b82f6;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.5px;
            margin-top: 10px;
            margin-left: 2px;
        """)
        self.layout.addWidget(title_lbl)
        
        # Section container for items
        self.content_frame = QFrame(self)
        self.content_frame.setObjectName("ContentFrame")
        self.content_frame.setStyleSheet("""
            QFrame#ContentFrame {
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(12)
        
        self.layout.addWidget(self.content_frame)

    def addRow(self, label_text, widget):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        if label_text:
            lbl = QLabel(label_text, self)
            lbl.setStyleSheet("color: #9ca3af; font-weight: 500;")
            row.addWidget(lbl)
        row.addWidget(widget)
        self.content_layout.addLayout(row)

    def addRowWidget(self, label_text, widget, val_widget):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        lbl = QLabel(label_text, self)
        lbl.setStyleSheet("color: #9ca3af; font-weight: 500;")
        row.addWidget(lbl)
        row.addWidget(widget)
        row.addWidget(val_widget)
        self.content_layout.addLayout(row)

class ViewportWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GhostChar Viewport 👻")
        self.resize(800, 450)
        self.setMinimumSize(400, 225)
        
        # Dark styling
        self.setStyleSheet("background-color: #0d0e0f;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: #0d0e0f;")
        layout.addWidget(self.label)
        
    def update_frame(self, frame_np):
        h, w, c = frame_np.shape
        q_img = QImage(frame_np.data, w, h, w * c, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        scaled = pixmap.scaled(
            self.label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label.setPixmap(scaled)
