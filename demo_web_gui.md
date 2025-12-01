# 🎉 Enhanced WSC Web GUI with Directory Browser

## ✅ New Features Added

The web GUI now includes an **enhanced directory browser** that makes it much easier to select output directories!

### 🆕 Key Improvements

1. **📁 Interactive Directory Browser**
   - Click the "Browse" button to open a modal dialog
   - Navigate through directories by clicking on folder names
   - Use ".." to go up one level
   - Current path is clearly displayed

2. **🖱️ Better User Experience**
   - Output directory field is now read-only (prevents typos)
   - Visual feedback with folder icons (📁)
   - Modal dialog that can be closed with Escape key or Cancel button
   - Click outside modal to close

3. **🛡️ Security & Stability**
   - Prevents directory traversal attacks
   - Graceful handling of permission errors
   - Default fallback to home directory

## 🚀 How to Use

1. **Start the server:**
   ```bash
   python3 web_gui.py --port 8081
   ```

2. **Open browser:**
   Navigate to http://localhost:8081

3. **Select output directory:**
   - Click the **"📁 Browse"** button
   - Navigate to your desired directory
   - Click **"Select"** to confirm

4. **Add files & decompile:**
   - Drag & drop .WSC files
   - Click **"Start Decompilation"**

## 🖼️ Interface Preview

**Output Directory Section:**
```
Output Directory:
[ /home/user/output/ ] [📁 Browse]
```

**Directory Browser Modal:**
```
┌─ 📁 Select Output Directory ─────────────────┐
│ /home/user/projects                          │
│ ┌─────────────────────────────────────────┐ │
│ │ 📁 ..                                   │ │
│ │ 📁 Documents                            │ │
│ │ 📁 Downloads                            │ │
│ │ 📁 wsc-output (selected)                │ │
│ │ 📁 Projects                             │ │
│ └─────────────────────────────────────────┘ │
│                                          [Cancel][Select] └
└────────────────────────────────────────────────────┘
```

## 🎯 Benefits

- ✅ **No more typing paths manually**
- ✅ **Visual directory navigation**
- ✅ **Prevents path errors**
- ✅ **Intuitive folder browsing**
- ✅ **Works in any browser**

## 🔧 Technical Details

The directory browser includes:

- **Backend API**: `/api/browse?path=/path/to/dir`
- **Frontend**: Modal dialog with JavaScript navigation
- **Security**: Path validation and directory traversal prevention
- **Cross-platform**: Works on Windows, Linux, macOS
- **Responsive**: Adapts to different screen sizes

## 🌟 Complete Feature Set

The WSC Web GUI now provides:

- 📁 **Interactive directory browser** ← NEW!
- 🎯 **Drag & drop file upload**
- 📋 **Batch processing**
- 📄 **Real-time logging**
- ⚙️ **Settings persistence**
- 🔧 **Japanese text support**
- 🎨 **Modern responsive design**

This makes the WSC decompiler extremely user-friendly while maintaining all the powerful functionality from the original requirements!