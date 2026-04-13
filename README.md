# choseek1

A focused PyQt-based photo culling tool for JPEG+RAW workflows.

## Goal

Shoot RAW+JPEG on camera, review JPEGs fast, mark keepers, then delete:
- all rejected JPEGs
- all rejected RAWs
- all keeper JPEGs

Final result:
- only keeper RAW files remain in the folder

## Current status

This repository currently contains the initial skeleton:
- PyQt app bootstrap
- main window with vertical split
- preview pane
- thumbnail strip
- folder scan for JPEG/RAW pairs
- keep/delete toggling
- delete plan execution

## Workflow concept

1. Open a folder with paired JPEG and RAW files
2. JPEGs are used for review only
3. Mark keeper shots
4. Run delete action
5. App removes all JPEGs and all rejected RAWs
6. Only keeper RAWs remain

## Planned modules

- `app/models/`
  - data models such as `PhotoPair`
- `app/services/`
  - folder scan
  - settings persistence
  - deletion logic
- `app/gui/`
  - main window
  - preview widget
  - thumbnail strip
  - status widgets

## Planned roadmap

### Phase 1
- base skeleton
- folder scan
- selection and preview

### Phase 2
- visual keep/delete overlays
- keyboard-first culling flow
- improved thumbnail generation

### Phase 3
- click-and-hold rectangular magnifier
- zoom settings
- smoother preview scaling

### Phase 4
- safer delete confirmation
- optional trash/recycle-bin support
- session persistence

## Install on Windows

1. Open the project folder
2. Run:

```bat
install.bat
run.bat
```

## Manual install

```py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

## Notes

This is intentionally not a full cataloging or editing app.
It is built to do one job fast:
JPEG-driven culling for RAW keepers.
