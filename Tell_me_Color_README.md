# Tell Me Color

Accessible color description and contrast checker (PySide6)

## Overview

This small tool helps you inspect colors by hex value and get an accessible, human-friendly description and contrast ratios against black and white. It also aims to be screen-reader friendly by exposing accessible names and descriptions on controls and output panes.

## Files

- `Color.py` — (original project file in the workspace; may currently be under active edits)
- `Color_fixed.py` — a clean, standalone copy that uses `QTextEdit` for results (read-only) so you can test the UI in isolation
- `requirements.txt` — Python dependencies for the project
- `Tell_me_Color_README.md` — this file

## Prerequisites

- Python 3.10+ recommended
- Windows / macOS / Linux with a supported Qt backend

## Install

Open a PowerShell terminal in the project folder and run:

```powershell
python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
```

## Notes about dependencies

- `PySide6` provides the Qt GUI. It includes most Qt modules including `QtWidgets`. `QTextToSpeech` (used for TTS) may require additional platform packages or plugins; on many systems the basic PySide6 install is sufficient.
- `webcolors` is used to map RGB to CSS3 color names.

## Running the small demo

To run the clean demo (`Color_fixed.py`) from PowerShell:

```powershell
python .\Color_fixed.py
```

Type a 6-digit hex color (for example `#1E90FF`) in the input box and press Enter or the "Describe Color" button.

If you want to run the main `Color.py`, ensure its syntax is valid and required libraries are installed, then run similarly.

## Accessibility notes

- Both result panes are `QTextEdit` and set to read-only so they are selectable and expose their contents to assistive technologies.
- Controls include `accessibleName` and `accessibleDescription` properties to improve screen reader announcements.
- Keyboard navigation: tab order is set (input -> Describe -> description -> contrast output).

## Next steps

- Implement a PySide-only, word-by-word reader using `QTextToSpeech` (guarded import) and keyboard controls (play/pause/stop, rate). This is tracked in the project todo list.

## License

MIT (adapt as needed)

## test
