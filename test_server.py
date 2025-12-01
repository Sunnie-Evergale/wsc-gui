#!/usr/bin/env python3
# test_server.py
# Simple test server for debugging JavaScript issues

import http.server
import socketserver
import os

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.path = '/test_tabs.html'
        return super().do_GET()

def start_test_server():
    """Start a simple test server."""
    port = 8084
    handler = TestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🧪 Test server running at http://localhost:{port}")
        print("Open this URL in your browser to test tab switching")
        print("Check the browser console for debugging information")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Test server stopped")

if __name__ == "__main__":
    start_test_server()