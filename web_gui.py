#!/usr/bin/env python3
# web_gui.py
# Web-based GUI for WSC decompiler - works without tkinter

import http.server
import socketserver
import webbrowser
import json
import os
import sys
import threading
import urllib.parse
from pathlib import Path
from decompiler import decompile_wsc_file
from recompiler import parse_github_format, recompile_wsc_file, content_to_binary
from validator import WSCValidator


class WSCWebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.settings_file = "settings.json"
        self.settings = self.load_settings()
        super().__init__(*args, **kwargs)

    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {"output_dir": "", "last_input_dir": ""}

    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.serve_main_page()
        elif self.path.startswith('/api/'):
            self.handle_api_get()
        elif self.path.startswith('/download'):
            self.handle_download()
        else:
            super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404)

    def serve_main_page(self):
        """Serve the main HTML page."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WSC Decompiler Web GUI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .controls { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .upload-area { border: 2px dashed #3498db; padding: 40px; text-align: center; background: #ecf0f1; border-radius: 8px; margin: 20px 0; }
        .upload-area.dragover { background: #d5e8f4; border-color: #2980b9; }
        .file-list { max-height: 200px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; margin: 10px 0; }
        .file-item { padding: 8px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .file-item:last-child { border-bottom: none; }
        .btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #2980b9; }
        .btn.danger { background: #e74c3c; }
        .btn.danger:hover { background: #c0392b; }
        .input-group { margin: 10px 0; }
        .input-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .input-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .log { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 8px; font-family: monospace; height: 300px; overflow-y: auto; }
        .status { background: #34495e; color: white; padding: 10px; border-radius: 4px; margin-top: 10px; }
        .success { color: #2ecc71; }
        .error { color: #e74c3c; }
        .info { color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 WSC Decompiler & Recompiler Web GUI</h1>
            <p>Decompile and compile visual novel script files with Japanese text support</p>

            <!-- Navigation Tabs -->
            <div style="margin-top: 15px;">
                <button id="decompilerTab" class="tab-button active">📖 Decompiler</button>
                <button id="recompilerTab" class="tab-button">✏️ Recompiler</button>
            </div>
        </div>

        <!-- Tab Styles -->
        <style>
        .tab-button {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 8px 16px;
            margin-right: 5px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .tab-button:hover {
            background: rgba(255,255,255,0.3);
        }
        .tab-button.active {
            background: rgba(255,255,255,0.4);
            border-color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        </style>

        <!-- Decompiler Tab -->
        <div id="decompilerTabContent" class="tab-content active">
            <div class="controls">
                <div class="input-group">
                    <label for="outputDir">Output Directory:</label>
                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="outputDir" placeholder="Click 'Browse' to select directory..." value="" readonly>
                        <button class="btn" onclick="browseDirectory()">📁 Browse</button>
                    </div>
                </div>

                <div class="upload-area" id="uploadArea">
                    <h3>📁 Drag & Drop .WSC files here</h3>
                    <p>or click to select files</p>
                    <input type="file" id="fileInput" multiple accept=".wsc,.WSC" style="display: none;">
                </div>

                <div class="file-list" id="fileList">
                    <div style="padding: 20px; text-align: center; color: #7f8c8d;">No files selected</div>
                </div>

                <div>
                    <button class="btn" onclick="startDecompilation()">🚀 Start Decompilation</button>
                    <button class="btn danger" onclick="clearFiles()">🗑️ Clear Files</button>
                    <button class="btn" onclick="clearLog()">📋 Clear Log</button>
                </div>

                <div class="status" id="status">Ready</div>
            </div>

            <div class="controls">
                <h3>📄 Decompiler Log</h3>
                <div class="log" id="log">WSC Decompiler Web GUI started<br>Ready to process files...</div>
            </div>
        </div>

        <!-- Recompiler Tab -->
        <div id="recompilerTabContent" class="tab-content">
            <div class="controls">
                <div class="input-group">
                    <label for="recompileFile">Upload Decompiled .TXT File:</label>
                    <input type="file" id="recompileFile" accept=".txt,.TXT" onchange="handleRecompileUpload()" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                </div>

                <div class="recompiler-workspace" id="recompilerWorkspace" style="display: none;">
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <button class="btn" onclick="validateRecompileContent()">🔍 Validate</button>
                        <button class="btn" onclick="compileToWSC()">🔨 Compile to WSC</button>
                        <button class="btn" onclick="downloadWSC()">💾 Download WSC</button>
                        <div style="flex: 1;"></div>
                        <label style="display: flex; align-items: center; gap: 5px;">
                            <input type="checkbox" id="preserveOffsets" checked>
                            <span>Preserve original offsets</span>
                        </label>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; height: 400px;">
                        <!-- Editor Pane -->
                        <div>
                            <h4>📝 Editor</h4>
                            <textarea id="editorContent" style="width: 100%; height: 350px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; resize: vertical;" placeholder="Load a .txt file to start editing..."></textarea>
                        </div>

                        <!-- Validation Pane -->
                        <div>
                            <h4>✅ Validation</h4>
                            <div id="validationResults" style="height: 350px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; padding: 10px; background: #f9f9f9;">
                                <div style="color: #7f8c8d; text-align: center; padding: 20px;">Upload a file and click Validate to check for issues</div>
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 10px;">
                        <h4>ℹ️ File Info</h4>
                        <div id="recompileFileInfo" style="padding: 10px; background: #f5f5f5; border-radius: 4px;">
                            No file loaded
                        </div>
                    </div>
                </div>
            </div>

            <div class="controls">
                <h3>📄 Recompiler Log</h3>
                <div class="log" id="recompileLog">WSC Recompiler ready<br>Upload a decompiled .txt file to begin...</div>
            </div>
        </div>
    </div>

    <!-- Directory Browser Modal -->
    <div id="directoryModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; min-width: 500px; max-width: 80%; max-height: 80%; overflow: hidden;">
            <h3 style="margin-bottom: 15px;">📁 Select Output Directory</h3>
            <div id="currentPath" style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-bottom: 10px; font-family: monospace; word-break: break-all;"></div>
            <div id="directoryList" style="height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px;"></div>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn danger" onclick="closeDirectoryModal()">Cancel</button>
                <button class="btn" onclick="selectCurrentDirectory()">Select</button>
            </div>
        </div>
    </div>

    <script>
        let selectedFiles = [];
        let currentBrowsePath = '';
        let selectedDirectory = '';

        // Recompiler variables
        let recompilerEntries = [];
        let recompileFilename = '';
        let compiledWSCPath = '';

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadSettings();
            setupDragDrop();
            setupFileInput();

            // Setup tab switching
            setupTabSwitching();
        });

        function setupTabSwitching() {
            // Add event listeners to tab buttons
            const decompilerTab = document.getElementById('decompilerTab');
            const recompilerTab = document.getElementById('recompilerTab');

            if (decompilerTab) {
                decompilerTab.addEventListener('click', function() {
                    switchTab('decompiler');
                });
            }

            if (recompilerTab) {
                recompilerTab.addEventListener('click', function() {
                    switchTab('recompiler');
                });
            }
        }

        function setupDragDrop() {
            const uploadArea = document.getElementById('uploadArea');

            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.classList.add('dragover');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.classList.remove('dragover');
                }, false);
            });

            uploadArea.addEventListener('drop', handleDrop, false);
            uploadArea.addEventListener('click', () => {
                document.getElementById('fileInput').click();
            });
        }

        function setupFileInput() {
            document.getElementById('fileInput').addEventListener('change', function(e) {
                handleFiles(e.target.files);
            });
        }

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            [...files].forEach(file => {
                if (file.name.toLowerCase().endsWith('.wsc')) {
                    if (!selectedFiles.some(f => f.name === file.name)) {
                        selectedFiles.push(file);
                    }
                } else {
                    log(`Skipping non-WSC file: ${file.name}`, 'error');
                }
            });
            updateFileList();
        }

        function updateFileList() {
            const fileList = document.getElementById('fileList');
            if (selectedFiles.length === 0) {
                fileList.innerHTML = '<div style="padding: 20px; text-align: center; color: #7f8c8d;">No files selected</div>';
            } else {
                fileList.innerHTML = selectedFiles.map((file, index) => `<div class="file-item"><span>📄 ${file.name}</span><button class="btn danger" onclick="removeFile(${index})" style="padding: 4px 8px; font-size: 12px;">Remove</button></div>`).join('');
            }
        }

        function removeFile(index) {
            selectedFiles.splice(index, 1);
            updateFileList();
        }

        function clearFiles() {
            selectedFiles = [];
            updateFileList();
            document.getElementById('fileInput').value = '';
            log('Cleared all files');
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
            log('Log cleared');
        }

        function log(message, type = 'info') {
            const logDiv = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            const className = type === 'error' ? 'error' : type === 'success' ? 'success' : '';
            logDiv.innerHTML += `<div class="${className}">[${timestamp}] ${message}</div>`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }

        async function startDecompilation() {
            if (selectedFiles.length === 0) {
                alert('Please select WSC files first!');
                return;
            }

            const outputDir = document.getElementById('outputDir').value.trim();
            if (!outputDir) {
                alert('Please select an output directory!');
                return;
            }

            log(`Starting decompilation of ${selectedFiles.length} files...`, 'info');
            updateStatus('Processing...');

            try {
                const formData = new FormData();
                for (let file of selectedFiles) {
                    formData.append('files', file);
                }
                formData.append('output_dir', outputDir);

                const response = await fetch('/api/decompile', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    log(`Decompilation complete: ${result.success_count} files processed successfully`, 'success');
                    if (result.error_count > 0) {
                        log(`Errors: ${result.error_count} files failed`, 'error');
                    }
                    updateStatus('Complete');
                } else {
                    log(`Error: ${result.message}`, 'error');
                    updateStatus('Error');
                }

            } catch (error) {
                log(`Network error: ${error.message}`, 'error');
                updateStatus('Error');
            }
        }

        async function loadSettings() {
            try {
                const response = await fetch('/api/settings');
                const settings = await response.json();
                if (settings.output_dir) {
                    document.getElementById('outputDir').value = settings.output_dir;
                }
            } catch (error) {
                console.log('Could not load settings:', error);
            }
        }

        async function saveOutputDir() {
            const outputDir = document.getElementById('outputDir').value;
            try {
                await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ output_dir: outputDir })
                });
            } catch (error) {
                console.log('Could not save settings:', error);
            }
        }

        // Save output directory when changed
        document.getElementById('outputDir').addEventListener('change', saveOutputDir);

        // Directory Browser Functions
        async function browseDirectory() {
            document.getElementById('directoryModal').style.display = 'block';

            // Start with current output directory or home directory
            const currentDir = document.getElementById('outputDir').value || '/home';
            await loadDirectory(currentDir);
        }

        async function loadDirectory(path) {
            try {
                const response = await fetch(`/api/browse?path=${encodeURIComponent(path)}`);
                const data = await response.json();

                if (data.success) {
                    currentBrowsePath = data.current_path;
                    displayDirectoryList(data.items);
                    document.getElementById('currentPath').textContent = data.current_path;
                } else {
                    log(`Error loading directory: ${data.message}`, 'error');
                }
            } catch (error) {
                log(`Error loading directory: ${error.message}`, 'error');
            }
        }

        function displayDirectoryList(items) {
            const listDiv = document.getElementById('directoryList');

            if (items.length === 0) {
                listDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: #7f8c8d;">No directories found</div>';
                return;
            }

            listDiv.innerHTML = items.map(item => `<div onclick="selectDirectory('${item.path}')" style="padding: 10px; cursor: pointer; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 10px;" onmouseover="this.style.background='#f5f5f5'" onmouseout="this.style.background='white'"><span style="font-size: 16px;">${item.type === 'directory' ? '📁' : '📄'}</span><span>${item.name}</span></div>`).join('');
        }

        async function selectDirectory(path) {
            selectedDirectory = path;
            await loadDirectory(path);
        }

        function closeDirectoryModal() {
            document.getElementById('directoryModal').style.display = 'none';
            selectedDirectory = '';
        }

        function selectCurrentDirectory() {
            if (selectedDirectory || currentBrowsePath) {
                const finalPath = selectedDirectory || currentBrowsePath;
                document.getElementById('outputDir').value = finalPath;
                saveOutputDir();
                closeDirectoryModal();
                log(`Selected output directory: ${finalPath}`, 'success');
            } else {
                alert('Please select a directory');
            }
        }

        // Close modal when clicking outside
        document.getElementById('directoryModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeDirectoryModal();
            }
        });

        // Keyboard shortcuts for modal
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeDirectoryModal();
            }
        });

        // Tab switching functions
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + 'TabContent').classList.add('active');
            document.getElementById(tabName + 'Tab').classList.add('active');
        }

        // Recompiler functions
        function handleRecompileUpload() {
            const fileInput = document.getElementById('recompileFile');
            const file = fileInput.files[0];

            if (!file) {
                recompilerLog('No file selected', 'error');
                return;
            }

            if (!file.name.toLowerCase().endsWith('.txt')) {
                recompilerLog('Please select a .txt file from decompiler output', 'error');
                return;
            }

            recompilerLog(`Loading file: ${file.name}...`, 'info');

            const formData = new FormData();
            formData.append('file', file);

            fetch('/api/recompile/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    recompilerEntries = data.entries;
                    recompileFilename = data.filename.replace('.txt', '.wsc');

                    // Display content in editor
                    const content = formatEntriesAsText(data.entries);
                    document.getElementById('editorContent').value = content;

                    // Show workspace
                    document.getElementById('recompilerWorkspace').style.display = 'block';

                    // Update file info
                    updateRecompileFileInfo(data);

                    // Show initial validation results
                    displayValidationResults(data.parse_result, data.validation_result);

                    recompilerLog(`Successfully loaded ${data.entries.length} entries`, 'success');
                } else {
                    recompilerLog(`Error loading file: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                recompilerLog(`Network error: ${error.message}`, 'error');
            });
        }

        function formatEntriesAsText(entries) {
            return entries.map(entry => {
                const speaker_prefix = entry.is_speaker ? '.' : '';
                return `<${entry.start_offset.toString(16).padStart(8, '0').toUpperCase()}:${entry.end_offset.toString(16).padStart(8, '0').toUpperCase()}>\\n${speaker_prefix}${entry.content}\\n`;
            }).join('');
        }

        function updateRecompileFileInfo(data) {
            const fileInfo = document.getElementById('recompileFileInfo');
            fileInfo.innerHTML = `<strong>File:</strong> ${data.filename}<br>` +
                `<strong>Entries:</strong> ${data.entries.length}<br>` +
                `<strong>Valid:</strong> ${data.validation_result.valid ? '✅ Yes' : '❌ No'}<br>` +
                `<strong>Errors:</strong> ${data.parse_result.errors.length}<br>` +
                `<strong>Warnings:</strong> ${data.parse_result.warnings.length}<br>` +
                `<strong>Needs Recalculation:</strong> ${data.validation_result.needs_recalculation ? '⚠️ Yes' : '✅ No'}`;
        }

        function validateRecompileContent() {
            const content = document.getElementById('editorContent').value;

            if (!content.trim()) {
                recompilerLog('No content to validate', 'error');
                return;
            }

            recompilerLog('Validating content...', 'info');

            const requestData = {
                content: content,
                entries: recompilerEntries
            };

            fetch('/api/recompile/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayValidationResults(data.validation_result, data.quick_validation);
                    recompilerLog(`Validation complete: ${data.validation_result.valid ? '✅ Valid' : '❌ Issues found'}`, 'success');
                } else {
                    recompilerLog(`Validation error: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                recompilerLog(`Validation error: ${error.message}`, 'error');
            });
        }

        function displayValidationResults(validationResult, quickValidation) {
            const resultsDiv = document.getElementById('validationResults');

            // Overall status
            const statusDiv = `<div style="margin-bottom: 10px; padding: 10px; background: ${validationResult.valid ? '#d4edda' : '#f8d7da'}; border-radius: 4px;"><strong>Status:</strong> ${validationResult.valid ? '✅ Valid' : '❌ Issues found'}</div>`;

            let errorsDiv = '';
            // Errors
            if (validationResult.errors.length > 0) {
                errorsDiv = '<div style="margin-bottom: 10px;"><strong>🚨 Errors:</strong><ul>' +
                    validationResult.errors.map(error => `<li style="color: #d32f2f;">${error}</li>`).join('') + '</ul></div>';
            }

            let warningsDiv = '';
            // Warnings
            if (validationResult.warnings.length > 0) {
                warningsDiv = '<div style="margin-bottom: 10px;"><strong>⚠️ Warnings:</strong><ul>' +
                    validationResult.warnings.map(warning => `<li style="color: #f57c00;">${warning}</li>`).join('') + '</ul></div>';
            }

            let suggestionsDiv = '';
            // Suggestions
            if (validationResult.suggestions.length > 0) {
                suggestionsDiv = '<div><strong>💡 Suggestions:</strong><ul>' +
                    validationResult.suggestions.map(suggestion => `<li style="color: #1976d2;">${suggestion}</li>`).join('') + '</ul></div>';
            }

            let issuesDiv = '';
            // Quick validation results
            if (quickValidation && quickValidation.errors.length > 0) {
                issuesDiv = '<div style="margin-top: 10px;"><strong>📍 Line Issues:</strong><ul>' +
                    quickValidation.errors.map(error => `<li style="color: #d32f2f;">Line ${error.line}: ${error.message}</li>`).join('') + '</ul></div>';
            }

            resultsDiv.innerHTML = statusDiv + errorsDiv + warningsDiv + suggestionsDiv + issuesDiv || '<div style="color: #4caf50; text-align: center;">✅ No issues found!</div>';
        }

        function compileToWSC() {
            const content = document.getElementById('editorContent').value;
            const preserveOffsets = document.getElementById('preserveOffsets').checked;

            if (!content.trim()) {
                recompilerLog('No content to compile', 'error');
                return;
            }

            recompilerLog('Compiling to WSC format...', 'info');

            const requestData = {
                entries: recompilerEntries,
                preserve_offsets: preserveOffsets,
                filename: recompileFilename
            };

            fetch('/api/recompile/compile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    compiledWSCPath = data.file_path;
                    recompilerLog(`✅ Successfully compiled ${data.entries_count} entries`, 'success');
                    recompilerLog(`File size: ${data.file_size} bytes`, 'info');
                    recompilerLog(`Offsets recalculated: ${data.offsets_recalculated ? 'Yes' : 'No'}`, 'info');
                } else {
                    recompilerLog(`Compilation error: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                recompilerLog(`Compilation error: ${error.message}`, 'error');
            });
        }

        function downloadWSC() {
            if (!compiledWSCPath) {
                recompilerLog('No compiled WSC file available. Please compile first.', 'error');
                return;
            }

            // Create download link
            const link = document.createElement('a');
            link.href = '/download?file=' + encodeURIComponent(compiledWSCPath);
            link.download = recompileFilename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            recompilerLog(`Downloading ${recompileFilename}...`, 'info');
        }

        function recompilerLog(message, type = 'info') {
            const logDiv = document.getElementById('recompileLog');
            const timestamp = new Date().toLocaleTimeString();
            const className = type === 'error' ? 'error' : type === 'success' ? 'success' : '';
            logDiv.innerHTML += `<div class="${className}">[${timestamp}] ${message}</div>`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_api_get(self):
        """Handle API GET requests."""
        if self.path == '/api/settings':
            self.send_json_response(self.settings)
        elif self.path.startswith('/api/browse'):
            self.handle_directory_browse()
        else:
            self.send_error(404)

    def handle_api_post(self):
        """Handle API POST requests."""
        if self.path == '/api/decompile':
            self.handle_decompile()
        elif self.path == '/api/settings':
            self.handle_settings_update()
        elif self.path.startswith('/api/recompile/'):
            self.handle_recompile_requests()
        else:
            self.send_error(404)

    def handle_decompile(self):
        """Handle file decompilation."""
        try:
            import cgi
            import io

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Use cgi module for proper multipart parsing
            content_type = self.headers['Content-Type']
            if not content_type.startswith('multipart/form-data'):
                self.send_json_response({"success": False, "message": "Invalid content type"})
                return

            # Parse multipart form data properly
            environ = {
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
                'CONTENT_LENGTH': str(content_length)
            }

            form = cgi.FieldStorage(
                fp=io.BytesIO(post_data),
                environ=environ,
                keep_blank_values=True
            )

            files = []
            output_dir = ""

            # Extract files
            if 'files' in form:
                file_field = form['files']
                if isinstance(file_field, list):
                    file_items = file_field
                else:
                    file_items = [file_field]

                for file_item in file_items:
                    if file_item.filename:
                        filename = file_item.filename
                        file_data = file_item.file.read()

                        if filename.lower().endswith('.wsc'):
                            # Save file temporarily
                            temp_path = f"temp_{filename}"
                            with open(temp_path, 'wb') as f:
                                f.write(file_data)
                            files.append(temp_path)

            # Extract output directory
            if 'output_dir' in form:
                output_dir = form['output_dir'].value.strip()

            print(f"Files found: {len(files)}")
            print(f"Output directory: '{output_dir}'")

            if not files:
                self.send_json_response({"success": False, "message": "No valid WSC files found"})
                return

            if not output_dir:
                self.send_json_response({"success": False, "message": "No output directory specified"})
                return

            # Process files
            success_count = 0
            error_count = 0

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for temp_file in files:
                try:
                    filename = os.path.basename(temp_file)
                    base_name = filename.replace('temp_', '').replace('.wsc', '')
                    output_file = os.path.join(output_dir, f"{base_name}.txt")

                    decompile_wsc_file(temp_file, output_file)
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    print(f"Error processing {temp_file}: {e}")
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_file)
                    except:
                        pass

            self.send_json_response({
                "success": True,
                "success_count": success_count,
                "error_count": error_count
            })

        except Exception as e:
            self.send_json_response({"success": False, "message": str(e)})

    def handle_settings_update(self):
        """Handle settings update."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            settings = json.loads(post_data.decode('utf-8'))

            self.settings.update(settings)
            self.save_settings()

            self.send_json_response({"success": True})

        except Exception as e:
            self.send_json_response({"success": False, "message": str(e)})

    def handle_directory_browse(self):
        """Handle directory browsing requests."""
        try:
            # Parse path from URL
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)

            path = query_params.get('path', ['/'])[0]

            # Security check - prevent directory traversal
            if '..' in path or not os.path.isabs(path):
                path = '/'

            # Normalize path
            try:
                path = os.path.normpath(path)
                if not os.path.exists(path):
                    path = os.path.expanduser('~')  # Default to home directory
            except:
                path = os.path.expanduser('~')  # Default to home directory

            # Get directory contents
            if os.path.isdir(path):
                items = []

                # Add parent directory (except for root)
                if path != '/':
                    parent = os.path.dirname(path)
                    items.append({
                        'name': '..',
                        'path': parent,
                        'type': 'directory'
                    })

                # Add directory contents
                try:
                    for item in sorted(os.listdir(path)):
                        item_path = os.path.join(path, item)
                        item_type = 'directory' if os.path.isdir(item_path) else 'file'

                        # Only include directories and common folders
                        if item_type == 'directory':
                            items.append({
                                'name': item,
                                'path': item_path,
                                'type': 'directory'
                            })
                except PermissionError:
                    pass

                # Add common directories to the root
                if path == '/':
                    common_dirs = ['home', 'Users', 'mnt', 'tmp', 'var']
                    for common_dir in common_dirs:
                        if os.path.exists(f"/{common_dir}"):
                            items.append({
                                'name': common_dir,
                                'path': f"/{common_dir}",
                                'type': 'directory'
                            })

                response_data = {
                    'success': True,
                    'current_path': path,
                    'items': items
                }
            else:
                response_data = {
                    'success': False,
                    'message': 'Not a directory'
                }

            self.send_json_response(response_data)

        except Exception as e:
            self.send_json_response({
                'success': False,
                'message': str(e)
            })

    def handle_recompile_requests(self):
        """Handle recompiler API requests."""
        if self.path == '/api/recompile/upload':
            self.handle_recompile_upload()
        elif self.path == '/api/recompile/parse':
            self.handle_recompile_parse()
        elif self.path == '/api/recompile/validate':
            self.handle_recompile_validate()
        elif self.path == '/api/recompile/compile':
            self.handle_recompile_compile()
        else:
            self.send_error(404)

    def handle_recompile_upload(self):
        """Handle file upload for recompiler."""
        try:
            import cgi
            import io

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            content_type = self.headers['Content-Type']
            if not content_type.startswith('multipart/form-data'):
                self.send_json_response({"success": False, "message": "Invalid content type"})
                return

            environ = {
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
                'CONTENT_LENGTH': str(content_length)
            }

            form = cgi.FieldStorage(
                fp=io.BytesIO(post_data),
                environ=environ,
                keep_blank_values=True
            )

            if 'file' not in form or not form['file'].filename:
                self.send_json_response({"success": False, "message": "No file uploaded"})
                return

            uploaded_file = form['file']
            filename = uploaded_file.filename

            if not filename.lower().endswith('.txt'):
                self.send_json_response({"success": False, "message": "Please upload a .txt file from decompiler output"})
                return

            # Save uploaded file temporarily
            temp_path = f"recompile_temp_{filename}"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.file.read())

            # Read and parse the file
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the content
            entries, parse_result = parse_github_format(content)

            # Validate with validator
            validator = WSCValidator()
            validation_result = validator.comprehensive_validation(content, entries)

            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

            response = {
                "success": True,
                "filename": filename,
                "entries": [
                    {
                        "start_offset": entry.start_offset,
                        "end_offset": entry.end_offset,
                        "content": entry.content,
                        "is_speaker": entry.is_speaker,
                        "original_length": entry.original_length
                    }
                    for entry in entries
                ],
                "parse_result": {
                    "valid": parse_result.is_valid,
                    "errors": parse_result.errors,
                    "warnings": parse_result.warnings,
                    "suggestions": parse_result.suggestions,
                    "needs_recalculation": parse_result.needs_recalculation
                },
                "validation_result": {
                    "valid": validation_result.is_valid,
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings,
                    "suggestions": validation_result.suggestions,
                    "needs_recalculation": validation_result.needs_recalculation
                }
            }

            self.send_json_response(response)

        except Exception as e:
            self.send_json_response({"success": False, "message": f"Upload error: {str(e)}"})

    def handle_recompile_parse(self):
        """Handle parsing request for editor content."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            content = data.get('content', '')
            if not content:
                self.send_json_response({"success": False, "message": "No content provided"})
                return

            entries, parse_result = parse_github_format(content)

            response = {
                "success": True,
                "entries": [
                    {
                        "start_offset": entry.start_offset,
                        "end_offset": entry.end_offset,
                        "content": entry.content,
                        "is_speaker": entry.is_speaker,
                        "original_length": entry.original_length
                    }
                    for entry in entries
                ],
                "parse_result": {
                    "valid": parse_result.is_valid,
                    "errors": parse_result.errors,
                    "warnings": parse_result.warnings,
                    "suggestions": parse_result.suggestions,
                    "needs_recalculation": parse_result.needs_recalculation
                }
            }

            self.send_json_response(response)

        except Exception as e:
            self.send_json_response({"success": False, "message": f"Parse error: {str(e)}"})

    def handle_recompile_validate(self):
        """Handle validation request for editor content."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            content = data.get('content', '')
            entries_data = data.get('entries', [])

            # Convert back to WSCEntry objects
            from recompiler import WSCEntry
            entries = []
            for entry_data in entries_data:
                entry = WSCEntry(
                    entry_data['start_offset'],
                    entry_data['end_offset'],
                    entry_data['content'],
                    entry_data['is_speaker']
                )
                entries.append(entry)

            # Validate
            validator = WSCValidator()
            validation_result = validator.comprehensive_validation(content, entries)

            # Quick validation for real-time feedback
            quick_result = validator.quick_validate(content)

            response = {
                "success": True,
                "validation_result": {
                    "valid": validation_result.is_valid,
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings,
                    "suggestions": validation_result.suggestions,
                    "needs_recalculation": validation_result.needs_recalculation
                },
                "quick_validation": quick_result,
                "repair_suggestions": validator.generate_repair_suggestions(validation_result)
            }

            self.send_json_response(response)

        except Exception as e:
            self.send_json_response({"success": False, "message": f"Validation error: {str(e)}"})

    def handle_recompile_compile(self):
        """Handle compilation request back to WSC format."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            entries_data = data.get('entries', [])
            preserve_offsets = data.get('preserve_offsets', True)
            filename = data.get('filename', 'recompiled.wsc')

            # Convert back to WSCEntry objects
            from recompiler import WSCEntry
            entries = []
            for entry_data in entries_data:
                entry = WSCEntry(
                    entry_data['start_offset'],
                    entry_data['end_offset'],
                    entry_data['content'],
                    entry_data['is_speaker']
                )
                entries.append(entry)

            # Reconstruct binary
            from recompiler import reconstruct_wsc_binary
            binary_data = reconstruct_wsc_binary(entries, preserve_offsets)

            # Save to temporary file
            temp_path = f"recompile_output_{filename}"
            with open(temp_path, 'wb') as f:
                f.write(binary_data)

            # Get file info
            file_size = len(binary_data)
            file_path = os.path.abspath(temp_path)

            response = {
                "success": True,
                "filename": filename,
                "file_size": file_size,
                "file_path": file_path,
                "entries_count": len(entries),
                "preserve_offsets": preserve_offsets,
                "offsets_recalculated": not preserve_offsets or not all(
                    len(content_to_binary(e.content, e.is_speaker)) == e.original_length + 1
                    for e in entries
                )
            }

            self.send_json_response(response)

        except Exception as e:
            self.send_json_response({"success": False, "message": f"Compilation error: {str(e)}"})

    def handle_download(self):
        """Handle file download requests."""
        try:
            # Parse the file parameter from URL
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)

            if 'file' not in query_params:
                self.send_error(400, "Missing file parameter")
                return

            file_path = query_params['file'][0]

            # Security check - prevent directory traversal
            if '..' in file_path or not file_path.startswith('/'):
                self.send_error(400, "Invalid file path")
                return

            # Check if file exists and is a temporary recompile file
            if not os.path.exists(file_path) or not file_path.startswith('recompile_output_'):
                self.send_error(404, "File not found")
                return

            # Send file
            filename = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                file_data = f.read()

            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(len(file_data)))
            self.end_headers()
            self.wfile.write(file_data)

        except Exception as e:
            self.send_error(500, f"Download error: {str(e)}")

    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def start_web_server(port=8080):
    """Start the web server."""
    handler = WSCWebHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🌐 WSC Decompiler Web GUI started at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        print()
        print("Features:")
        print("- Drag & drop .WSC files")
        print("- Batch processing")
        print("- Real-time logging")
        print("- Settings persistence")
        print()

        # Open browser automatically
        def open_browser():
            import time
            time.sleep(1)  # Give server time to start
            webbrowser.open(f'http://localhost:{port}')

        threading.Thread(target=open_browser, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WSC Decompiler Web GUI")
    parser.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")
    args = parser.parse_args()

    start_web_server(args.port)