#!/usr/bin/env python3
"""
Launcher for Self-Quiz Generator Agent HTML UI
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading

def open_browser(url):
    """Open browser after a short delay."""
    time.sleep(2)
    webbrowser.open(url)

def main():
    """Launch the HTML UI server."""
    print("🎓 Self-Quiz Generator Agent - HTML UI")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists('index.html'):
        print("❌ index.html not found!")
        return
    
    if not os.path.exists('server.py'):
        print("❌ server.py not found!")
        return
    
    # Check Python dependencies
    try:
        import http.server
        print("✅ HTTP server module available")
    except ImportError:
        print("❌ HTTP server module not available")
        return
    
    # Start server
    port = 8080
    url = f"http://localhost:{port}"
    
    print(f"🚀 Starting server on port {port}...")
    print(f"🌐 Opening browser to: {url}")
    print("=" * 50)
    
    # Open browser in background
    browser_thread = threading.Thread(target=open_browser, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server
    try:
        subprocess.run([sys.executable, "server.py", "--port", str(port)])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thanks for using Self-Quiz Generator Agent!")

if __name__ == "__main__":
    main()
