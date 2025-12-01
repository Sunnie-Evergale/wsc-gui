# WSC Decompiler GUI

A graphical user interface for decompiling .WSC script files from visual novel engines.

## Features

- Drag-and-drop support for .WSC files
- Batch decompilation of multiple files
- Japanese CP932/Shift-JIS text decoding
- Speaker name detection with `.Name` format
- GitHub-style output format with hex offsets
- Settings persistence
- Comprehensive logging

## Requirements

```bash
pip install tkinterdnd2
```

## Usage

1. Run the GUI:
   ```bash
   python gui.py
   ```

2. Add .WSC files using:
   - File menu (Open Single/Multiple)
   - Drag & drop onto the designated area

3. Select an output directory

4. Click "Start Decompilation" to process files

## Output Format

Each extracted string is formatted as:
```
<OFFSET_START:OFFSET_END>
Content here
```

Speaker names are prefixed with a dot (`.Name`) while narration lines are output normally.

## Build EXE

```bash
pyinstaller gui.py --onefile --noconsole
```

This will create a standalone executable in the `dist/` folder.