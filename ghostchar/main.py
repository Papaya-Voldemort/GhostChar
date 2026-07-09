import os
import sys
import AppKit  # Cocoa library via pyobjc
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPainter, QColor, QAction
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

# Setup macOS Activation Policy to hide dock icon BEFORE creating QApplication
# NSApplicationActivationPolicyAccessory = 1 (runs in background, menu bar only)
app_inst = AppKit.NSApplication.sharedApplication()
app_inst.setActivationPolicy_(1)

from ghostchar.camera import CameraWorker
from ghostchar.audio import AudioMonitor
from ghostchar.gui import SettingsWindow

def create_ghost_tray_icon():
    """Programmatically draw a custom white ghost icon for the macOS menu bar."""
    pixmap = QPixmap(22, 22)
    pixmap.fill(QColor(0, 0, 0, 0)) # Transparent background
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 1. Draw Ghost Body
    # We use a white brush for the ghost body (works well in macOS Dark Mode menu bar)
    painter.setBrush(QColor(230, 230, 240))
    painter.setPen(Qt.PenStyle.NoPen)
    
    # Head (top circle)
    painter.drawEllipse(3, 2, 16, 15)
    # Body (bottom rect)
    painter.drawRect(3, 9, 16, 8)
    
    # Bottom wavy feet (draw 3 small circles)
    painter.drawEllipse(3, 14, 6, 6)
    painter.drawEllipse(8, 14, 6, 6)
    painter.drawEllipse(13, 14, 6, 6)
    
    # 2. Draw Eyes
    # Dark grey eyes
    painter.setBrush(QColor(26, 26, 30))
    painter.drawEllipse(7, 7, 2, 3)
    painter.drawEllipse(13, 7, 2, 3)
    
    painter.end()
    return QIcon(pixmap)

# We need QPixmap in create_ghost_tray_icon, so we import it here
from PyQt6.QtGui import QPixmap

class GhostCharApp:
    def __init__(self, qt_app):
        self.app = qt_app
        
        # 1. Initialize Worker Threads & Managers
        self.camera_worker = CameraWorker()
        self.audio_monitor = AudioMonitor()
        
        # Start camera worker immediately (idle state, starts stream when default camera opens)
        self.camera_worker.start()
        
        # 2. Create the Settings GUI Window (hidden initially)
        self.settings_window = SettingsWindow(self.camera_worker, self.audio_monitor)
        
        # 3. Create Tray Icon
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(create_ghost_tray_icon())
        self.tray_icon.setToolTip("GhostChar ASCII Camera")
        
        # 4. Setup Context Menu for Right-Click
        self.setup_menu()
        
        # Connect click event
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show tray icon in the system menu bar
        self.tray_icon.show()
        
        # Send initial status message
        self.camera_worker.status_message.emit("App started. Click icon to configure.")

    def setup_menu(self):
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e24;
                color: #e0e0e6;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
        """)
        
        # Actions
        open_action = QAction("Open Settings", self.app)
        open_action.triggered.connect(self.show_settings)
        
        self.pin_action = QAction("Pin Settings Panel", self.app)
        self.pin_action.setCheckable(True)
        self.pin_action.triggered.connect(self.toggle_pin_from_menu)
        
        status_action = QAction("Status: Running 👻", self.app)
        status_action.setEnabled(False)
        
        quit_action = QAction("Quit GhostChar", self.app)
        quit_action.triggered.connect(self.quit_app)
        
        self.menu.addAction(open_action)
        self.menu.addAction(self.pin_action)
        self.menu.addSeparator()
        self.menu.addAction(status_action)
        self.menu.addSeparator()
        self.menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.menu)

    def on_tray_activated(self, reason):
        # Click (Trigger) or Double-Click toggle window
        # Context (Right Click) shows the context menu automatically via Qt
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            if self.settings_window.isVisible():
                self.settings_window.hide()
            else:
                self.show_settings()

    def show_settings(self):
        # Position the window directly below the tray icon
        icon_geom = self.tray_icon.geometry()
        if icon_geom.isValid():
            win_w = self.settings_window.width()
            win_h = self.settings_window.height()
            
            # Center the window under the icon
            x = icon_geom.x() + icon_geom.width() // 2 - win_w // 2
            y = icon_geom.y() + icon_geom.height() + 4
            
            # Bound check to keep on screen
            screen = self.app.primaryScreen().geometry()
            if x < 4:
                x = 4
            elif x + win_w > screen.width() - 4:
                x = screen.width() - win_w - 4
                
            self.settings_window.move(x, y)
            
        # Display the settings panel and bring it to front
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
        self.settings_window.setFocus()

    def toggle_pin_from_menu(self):
        pinned = self.pin_action.isChecked()
        self.settings_window.pin_btn.setChecked(pinned)
        self.settings_window.toggle_pinned()

    def quit_app(self):
        self.settings_window.quit_application()

def main():
    # Force platform plugin to cocoa for macOS execution
    os.environ["QT_QPA_PLATFORM"] = "cocoa"
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Initialize App Context and prevent Python garbage collection
    app.runner = GhostCharApp(app)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
