#!/bin/bash
set -e

echo "=== Packaging GhostChar Desktop App ==="

# 1. Compile Icon
echo "Creating macOS icns file..."
uv run python create_icns.py /Users/elinelson/.gemini/antigravity-ide/brain/e552268b-127b-4fe3-bcc3-8f0d216fc7f6/ghostchar_app_icon_1781719263722.png GhostChar.icns

# 2. Clean build folders
echo "Cleaning old build directories..."
rm -rf build dist

# 3. Build executable with PyInstaller spec file
echo "Running PyInstaller..."
uv run pyinstaller GhostChar.spec

# 4. Verify build
if [ ! -d "dist/GhostChar.app" ]; then
    echo "Error: dist/GhostChar.app was not created!"
    exit 1
fi
echo "Successfully compiled dist/GhostChar.app!"

# 5. Create DMG package
echo "Packaging into DMG..."
mkdir -p dist/dmg_stage
cp -R dist/GhostChar.app dist/dmg_stage/
ln -s /Applications dist/dmg_stage/Applications

# Ensure downloads directory exists in web app
mkdir -p web-app/static/downloads

# Create the DMG using hdiutil
hdiutil create -volname "GhostChar" -srcfolder dist/dmg_stage -ov -format UDZO web-app/static/downloads/GhostChar.dmg

# Clean up build staging folder
rm -rf dist/dmg_stage
echo "=== Desktop app packaged successfully at web-app/static/downloads/GhostChar.dmg! ==="
