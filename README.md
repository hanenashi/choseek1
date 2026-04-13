<p align="center">
  <img src="choseek1.ico" width="400" alt="choseek1 icon">
</p>

# choseek1

A focused, lightning-fast PyQt-based photo culling tool for JPEG+RAW workflows. 

## Goal

Shoot RAW+JPEG on camera, review JPEGs fast, mark keepers, then delete:
- all rejected JPEGs
- all rejected RAWs
- all keeper JPEGs

Final result:
- only keeper RAW files remain in the folder

## Features (v1.0 Stable)

This repository is no longer a skeleton—it is a fully featured culling machine:
- **High-Performance Scanning:** Background threading and native EXIF-aware `QImageReader` decoding for instant visual feedback.
- **Dark Mode UI:** A distraction-free, professional dark theme.
- **Dynamic Thumbnails:** Fluid scaling via a status bar slider, complete with visual KEEP/DELETE badges.
- **Interactive Preview:** Mouse-wheel zoom, click-and-drag panning, and middle-click reset.
- **The Loupe:** Hold right-click for a customizable, high-res magnification lens.
- **Keyboard-First Flow:** Configurable shortcuts to blast through queues without lifting your hands.
- **Multi-Select:** Shift/Ctrl click support with right-click contextual menus for batch tagging.
- **Dev Safe Mode:** A simulated deletion mode so you can test your culling logic without touching your hard drive.
- **Session Persistence:** Automatically remembers your window size, splitter position, and slider settings.

## TL;DR Workflow

1. Shoot RAW+JPEG and put them in one folder.
2. Click **Load** to scan them (JPEGs load instantly).
3. Navigate with Arrow Keys.
4. **Shift-Click** or **Ctrl-Click** thumbnails to multi-select.
5. Scroll Wheel to Zoom, Left-Click Drag to Pan, Middle-Click to Fit.
6. Hold Right-Click for Loupe (Magnifier).
7. Right-Click the ribbon for batch Keep/Delete/Invert.
8. Press **Space** to toggle selected items.
9. Press **Delete** to execute deletion.

## Install on Windows (Source)

1. Open the project folder
2. Run the included batch scripts:

```bat
install.bat
run.bat
```

## Build Standalone `.exe`

Want to share the app or run it without Python installed? You can compile it into a standalone Windows executable.

1. Ensure you have run `install.bat` once to set up your environment.
2. Run:
```bat
build.bat
```
3. Your compiled app will be generated inside the `dist/choseek1` folder. You can zip this folder and run `choseek1.exe` on any Windows machine.

## Manual install

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

## Notes

This is intentionally not a full cataloging or editing app.
It is built to do one job fast:
JPEG-driven culling for RAW keepers.
