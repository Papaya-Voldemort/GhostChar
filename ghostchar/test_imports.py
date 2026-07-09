import os
import sys

print("=== GhostChar Diagnostic & Validation ===")

# 1. Check Python version
print(f"Python Version: {sys.version}")

# 2. Check imports
modules_to_test = [
    ("AppKit", "pyobjc-framework-Cocoa"),
    ("PyQt6", "PyQt6"),
    ("cv2", "opencv-python"),
    ("numpy", "numpy"),
    ("onnxruntime", "onnxruntime"),
    ("pyvirtualcam", "pyvirtualcam"),
    ("sounddevice", "sounddevice"),
    ("PIL", "pillow"),
]

failed = False
for mod_name, pkg_name in modules_to_test:
    try:
        __import__(mod_name)
        print(f"✅ Import succeeded: {mod_name} ({pkg_name})")
    except ImportError as e:
        print(f"❌ Import failed: {mod_name} ({pkg_name}). Error: {e}")
        failed = True

# 3. Check ONNX Model file
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
model_path = os.path.join(parent_dir, "ascii_cam_model", "model.onnx")
if os.path.exists(model_path):
    print(f"✅ Found ASCII ONNX Model at: {model_path} ({os.path.getsize(model_path)} bytes)")
else:
    print(f"❌ Could not find ASCII ONNX Model at: {model_path}")
    failed = True

# 4. Try loading custom modules
custom_modules = [
    "ghostchar.camera",
    "ghostchar.audio",
    "ghostchar.virtual",
    "ghostchar.gui",
    "ghostchar.main",
]

for mod in custom_modules:
    try:
        __import__(mod)
        print(f"✅ Module load succeeded: {mod}")
    except Exception as e:
        print(f"❌ Module load failed: {mod}. Error: {e}")
        import traceback
        traceback.print_exc()
        failed = True

if failed:
    print("\n❌ Diagnostics failed. Please fix the errors above.")
    sys.exit(1)
else:
    print("\n🎉 All checks passed! GhostChar modules are clean and ready to run.")
    sys.exit(0)
