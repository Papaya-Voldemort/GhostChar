import os
import sys
import subprocess
from PIL import Image

def make_icns(png_path, icns_path):
    iconset_dir = "icon.iconset"
    os.makedirs(iconset_dir, exist_ok=True)
    
    img = Image.open(png_path)
    
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png")
    ]
    
    print(f"Resizing images for {iconset_dir}...")
    for size, name in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(iconset_dir, name))
        
    print(f"Running iconutil to compile {icns_path}...")
    subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)
    
    # clean up iconset directory
    print("Cleaning up temporary files...")
    for f in os.listdir(iconset_dir):
        os.remove(os.path.join(iconset_dir, f))
    os.rmdir(iconset_dir)
    print(f"Successfully created {icns_path}!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_icns.py <src_png> <dest_icns>")
        sys.exit(1)
    make_icns(sys.argv[1], sys.argv[2])
