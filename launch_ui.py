#!/usr/bin/env python3
"""
Launcher script for the Self-Quiz Generator Agent Web UI
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit web UI."""
    print("🚀 Starting Self-Quiz Generator Agent Web UI...")
    print("=" * 50)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly"])
        print("✅ Streamlit installed successfully")
    
    # Launch the web UI
    web_ui_path = os.path.join(os.path.dirname(__file__), "web_ui.py")
    
    print(f"🌐 Launching web interface...")
    print(f"📱 The UI will open in your default browser")
    print(f"🔗 If it doesn't open automatically, go to: http://localhost:8501")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", web_ui_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web UI stopped. Thanks for using Self-Quiz Generator Agent!")
    except Exception as e:
        print(f"❌ Error launching web UI: {e}")
        print("💡 Try running: streamlit run web_ui.py")

if __name__ == "__main__":
    main()
