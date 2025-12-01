#!/usr/bin/env python3
# minimal_gui.py
# Minimal web GUI to test tab switching functionality

import http.server
import socketserver

class MinimalHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.serve_minimal_gui()
        else:
            super().do_GET()

    def serve_minimal_gui(self):
        """Serve a minimal HTML page with just the tab switching functionality."""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WSC Minimal GUI Test</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
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
        .tab-button:hover { background: rgba(255,255,255,0.3); }
        .tab-button.active { background: rgba(255,255,255,0.4); border-color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .controls { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 WSC Minimal GUI Test</h1>
            <p>Testing tab switching functionality</p>

            <div style="margin-top: 15px;">
                <button id="decompilerTab" class="tab-button active">📖 Decompiler</button>
                <button id="recompilerTab" class="tab-button">✏️ Recompiler</button>
            </div>
        </div>

        <div id="decompilerTabContent" class="tab-content active">
            <div class="controls">
                <h2>📖 Decompiler Tab</h2>
                <p>This is the decompiler content area. Upload .WSC files here.</p>
                <div style="border: 2px dashed #3498db; padding: 40px; text-align: center;">
                    <p>Drag & Drop .WSC files here</p>
                </div>
            </div>
        </div>

        <div id="recompilerTabContent" class="tab-content">
            <div class="controls">
                <h2>✏️ Recompiler Tab</h2>
                <p>This is the recompiler content area. Upload .txt files here.</p>
                <div style="border: 2px dashed #e74c3c; padding: 40px; text-align: center;">
                    <p>Upload decompiled .txt files here</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        console.log('Script starting...');

        function switchTab(tabName) {
            console.log('Switching to tab:', tabName);

            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('active');
            });

            // Show selected tab content
            const tabContent = document.getElementById(tabName + 'TabContent');
            const tabButton = document.getElementById(tabName + 'Tab');

            if (tabContent) {
                tabContent.classList.add('active');
                console.log('Tab content activated:', tabName + 'TabContent');
            } else {
                console.error('Tab content not found:', tabName + 'TabContent');
            }

            if (tabButton) {
                tabButton.classList.add('active');
                console.log('Tab button activated:', tabName + 'Tab');
            } else {
                console.error('Tab button not found:', tabName + 'Tab');
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM Content Loaded - setting up event listeners');

            const decompilerTab = document.getElementById('decompilerTab');
            const recompilerTab = document.getElementById('recompilerTab');

            if (decompilerTab) {
                decompilerTab.addEventListener('click', function() {
                    console.log('Decompiler tab clicked via event listener');
                    switchTab('decompiler');
                });
                console.log('Decompiler tab event listener added');
            }

            if (recompilerTab) {
                recompilerTab.addEventListener('click', function() {
                    console.log('Recompiler tab clicked via event listener');
                    switchTab('recompiler');
                });
                console.log('Recompiler tab event listener added');
            }

            console.log('switchTab function type:', typeof switchTab);
            console.log('Setup complete');
        });
    </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))


def start_minimal_server():
    """Start minimal test server."""
    port = 8085
    handler = MinimalHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🧪 Minimal WSC GUI running at http://localhost:{port}")
        print("Test the tab switching functionality here")
        print("Check browser console (F12) for debugging information")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Minimal server stopped")


if __name__ == "__main__":
    start_minimal_server()