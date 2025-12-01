# WSC Decompiler - Usage Guide

## 🚀 Quick Start

### Option 1: Web GUI (Recommended - No Dependencies)
```bash
python3 web_gui.py
```
Then open your browser to http://localhost:8080

**Features:**
- ✅ Works on any system with Python 3
- ✅ Drag & drop interface
- ✅ No external dependencies needed
- ✅ Batch processing
- ✅ Real-time logging

### Option 2: Command Line Interface
```bash
# Single file
python3 cli.py input.wsc

# Batch processing
python3 cli.py *.wsc -d output_folder/

# Verbose output
python3 cli.py input.wsc -v
```

### Option 3: Desktop GUI (Requires tkinter)
```bash
# Install tkinter first
sudo apt install python3-tk  # Ubuntu/Debian

# Run simple GUI
python3 gui_simple.py

# For full drag-and-drop support
pip install tkinterdnd2
python3 gui.py
```

## 📋 Web GUI Instructions

1. **Start the server:**
   ```bash
   python3 web_gui.py --port 8080
   ```

2. **Open browser:**
   Navigate to http://localhost:8080

3. **Set output directory:**
   - Enter your desired output folder path
   - Settings are automatically saved

4. **Add files:**
   - **Drag & Drop**: Drag .WSC files onto the upload area
   - **Click to Select**: Click the upload area to browse files

5. **Process files:**
   - Click "Start Decompilation"
   - Watch the real-time log
   - Files will be saved as .txt in your output directory

## 📄 Output Format

Each decompiled file follows this GitHub-style format:

```
<OFFSET_START:OFFSET_END>
Content here

<OFFSET_START:OFFSET_END>
Another string
```

**Special formatting:**
- **Speaker names**: `.Name` (prefixed with dot)
- **Narration**: Text without dot
- **Resource IDs**: Preserved as-is (DAY, BG, ST, HOS)
- **Audio files**: Preserved (SE_, BGM_)
- **Commands**: Preserved (%K%P, %N, etc.)

## 🔧 CLI Options

```bash
python3 cli.py [options] input_files

Options:
  -o, --output FILE     Output file (for single input)
  -d, --dir DIR         Output directory (default: current)
  -v, --verbose         Verbose output
  --version             Show version
  -h, --help            Show help

Examples:
  python3 cli.py script.wsc
  python3 cli.py script.wsc -o output.txt
  python3 cli.py *.wsc -d decompiled/
  python3 cli.py script.wsc -v
```

## 📁 File Types Supported

**Input:** `.WSC` files (visual novel script files)

**Output:** `.TXT` files (decoded script text)

## 🔍 What Gets Extracted

The decompiler extracts and processes:

✅ **Always Kept:**
- Japanese text (CP932/Shift-JIS decoded)
- Resource IDs: `DAY0904`, `BG108_02`, `ST13A05S`, `HOS_1318`
- Audio files: `SE_104.ogg`, `BGM_06`
- Engine commands: `%K%P`, `%N`

✅ **Speaker Detection:**
- `0x0F` + Japanese name → `.Name` format
- Example: `0F0F夜久` → `.夜久`

✅ **Narration Processing:**
- `0x0F` + full sentence → Text without prefix
- Example: `0Fこんにちは世界` → `こんにちは世界`

❌ **Filtered Out:**
- Single character garbage (I, t, F)
- Random byte sequences
- Empty strings

## 🛠️ Troubleshooting

### Web GUI Issues

**Server won't start:**
```bash
# Check if port is available
netstat -an | grep 8080

# Use different port
python3 web_gui.py --port 8081
```

**Files not processing:**
- Ensure files have `.wsc` extension (case-insensitive)
- Check output directory permissions
- View log for error messages

### CLI Issues

**Python not found:**
```bash
# Use python3 instead
python3 cli.py input.wsc
```

**Permission errors:**
```bash
# Check file permissions
ls -la input.wsc

# Change permissions if needed
chmod 644 input.wsc
```

### Desktop GUI Issues

**tkinter not available:**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Use Web GUI instead (no dependencies)
python3 web_gui.py
```

**tkinterdnd2 not available:**
```bash
# Install for full drag-and-drop
pip install tkinterdnd2

# Or use simple GUI
python3 gui_simple.py
```

## 📝 Examples

### Example 1: Single File Processing
```bash
python3 cli.py DAY0904.wsc
# Output: DAY0904.txt
```

### Example 2: Batch Processing
```bash
python3 cli.py *.wsc -d output/
# Creates multiple .txt files in output/ folder
```

### Example 3: Web GUI Workflow
1. Start: `python3 web_gui.py`
2. Open: http://localhost:8080
3. Set output: `/home/user/decompiled/`
4. Drag files: Drop `script1.wsc`, `script2.wsc`
5. Click: "Start Decompilation"
6. Results: `script1.txt`, `script2.txt` in output folder

### Example 4: Typical Output
**Input WSC file contains:**
```
DAY0904
0F0F夜久
0Fこんにちは世界
SE_104.ogg
%K%P
```

**Output TXT file contains:**
```
<00000000:00000007>
DAY0904

<00000008:0000000E>
.夜久

<0000000F:0000001E>
こんにちは世界

<0000001F:00000029>
SE_104.ogg

<0000002A:0000002E>
%K%P
```

## 🔒 Security Notes

- Files are processed locally on your machine
- Web GUI runs only on localhost (no external access)
- Temporary files are automatically cleaned up
- No data is sent to external servers

## 📞 Getting Help

If you encounter issues:

1. **Check the log output** for specific error messages
2. **Verify file permissions** on input and output directories
3. **Test with a simple file** using the CLI first
4. **Try the Web GUI** if desktop GUI has dependency issues
5. **Check Python version** (requires Python 3.6+)

For more technical details, see `PROJECT_SUMMARY.md`.