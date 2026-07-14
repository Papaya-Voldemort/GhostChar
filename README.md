# ASCII-Camera

> A quick note on AI usage: AI was used in the making of this project. It helped me learn the ML needed but was not too involved in the final training just the learning before hand. AI was used to make most of the web UI and some of the desktop app to keep things running at high FPS. AI Auto complete was not used as I don't really like it and find it quite annouing. Gemini Web and some Antigravity Agent work was used. Please check out the other README's inside each of the folders for more info!

Welcome to **ASCII-Camera**! This project is a neural-network and pixel-intensity powered real-time ASCII video filter. It enables converting webcam streams, images, and videos into stylized ASCII art.

The project is structured into three main components:

---

## Repository Structure

> Sorry its such a mess this project was NOT meant to get this big

### 1. [Model & Training Pipeline](file:///Users/elinelson/Documents/Development/Learn_ML/model-training)
- **Folder:** [`model-training/`](file:///Users/elinelson/Documents/Development/Learn_ML/model-training)
- **Role:** Python scripts to generate synthetic character variations, pre-train a CNN classifier, fine-tune using smart sampling against `jp2a` outputs on COCO dataset images, export to ONNX, and upload to the Hugging Face Hub.
- **Weights output:** Saves directly to the root [`ascii_cam_model/`](file:///Users/elinelson/Documents/Development/Learn_ML/ascii_cam_model) folder.

### 2. [Web Application](file:///Users/elinelson/Documents/Development/Learn_ML/web-app)
- **Folder:** [`web-app/`](file:///Users/elinelson/Documents/Development/Learn_ML/web-app)
- **Role:** The Svelte-based static webpage. It loads the ONNX model from the root directory and runs real-time camera-to-ASCII classification completely client-side in the browser using ONNX Runtime Web.
- **Server:** A custom python server (`server.py`) is provided to inject CORS and COOP/COEP headers for high-performance WASM execution.

### 3. [Desktop Application (Spec & Template)](file:///Users/elinelson/Documents/Development/Learn_ML/desktop-app)
- **Folder:** [`desktop-app/`](file:///Users/elinelson/Documents/Development/Learn_ML/desktop-app)
- **Role:** A full python dekstop app for streaming a ASCII virtual web cam. Built with PyQt6 and needs OBS installed for the virtual camera.

### 4. [Active Model Weights](file:///Users/elinelson/Documents/Development/Learn_ML/ascii_cam_model)
- **Folder:** [`ascii_cam_model/`](file:///Users/elinelson/Documents/Development/Learn_ML/ascii_cam_model)
- **Role:** Houses the current production `.onnx` and `.keras` model weights, serving as a single source of truth for the training scripts, web interface, and desktop app.

---

## Quick Start

### Running the Web Demo locally
To run the browser-based camera feed:
```bash
# Run the developer server (injects COOP/COEP headers for multithreading)
python web-app/server.py
```
Then visit `http://localhost:8000` in your web browser.

---

## License

This project is licensed under the MIT License - see the [LICENSE](file:///Users/elinelson/Documents/Development/Learn_ML/LICENSE) file for details.
