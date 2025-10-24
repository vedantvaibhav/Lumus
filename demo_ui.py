#!/usr/bin/env python3
"""
Demo script showing the Self-Quiz Generator Agent Web UI features.
"""

import os
import sys
import webbrowser
import time
import subprocess
from pathlib import Path

def print_banner():
    """Print a welcome banner."""
    print("=" * 60)
    print("🎓 Self-Quiz Generator Agent - Web UI Demo")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = ['streamlit', 'plotly', 'openai', 'beautifulsoup4']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "streamlit", "plotly", "openai", "beautifulsoup4", 
                "requests", "pdfplumber", "PyPDF2", "python-dotenv", 
                "click", "pydantic"
            ])
            print("✅ All dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    print()
    return True

def check_api_key():
    """Check if API key is configured."""
    print("🔑 Checking API key configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OpenAI API key found in environment variables")
        return True
    else:
        print("⚠️  OpenAI API key not found in environment variables")
        print("   You can set it with: export OPENAI_API_KEY='your-key-here'")
        print("   Or enter it directly in the web UI")
        return False

def launch_web_ui():
    """Launch the web UI."""
    print("🚀 Launching Web UI...")
    print()
    print("The web interface will open in your browser.")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print()
    print("Features you can try:")
    print("• 📝 Paste sample text about photosynthesis")
    print("• 🌐 Enter a Wikipedia URL")
    print("• ⚙️  Adjust quiz parameters (difficulty, question types)")
    print("• 📊 View interactive charts and analytics")
    print("• 💾 Download quizzes in multiple formats")
    print()
    print("Press Ctrl+C to stop the web server")
    print("=" * 60)
    
    try:
        web_ui_path = Path(__file__).parent / "web_ui.py"
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(web_ui_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web UI stopped. Thanks for trying the Self-Quiz Generator Agent!")
    except Exception as e:
        print(f"❌ Error launching web UI: {e}")
        print("💡 Try running: streamlit run web_ui.py")

def show_sample_content():
    """Show sample content that users can try."""
    print("📚 Sample Content to Try:")
    print("-" * 30)
    
    samples = [
        {
            "title": "Photosynthesis",
            "content": """
            Photosynthesis is the process by which plants convert light energy into chemical energy.
            This process occurs in the chloroplasts of plant cells, specifically in structures called thylakoids.
            The main pigment involved in photosynthesis is chlorophyll, which absorbs light primarily in the blue and red wavelengths.
            
            The process can be divided into two main stages: the light-dependent reactions and the Calvin cycle.
            In the light-dependent reactions, light energy is captured and used to produce ATP and NADPH.
            The Calvin cycle uses these energy carriers to convert carbon dioxide into glucose.
            """
        },
        {
            "title": "Machine Learning",
            "content": """
            Machine Learning is a subset of artificial intelligence that focuses on algorithms
            that can learn and make decisions from data without being explicitly programmed.
            
            There are three main types of machine learning:
            1. Supervised Learning: Uses labeled training data to learn a mapping from inputs to outputs
            2. Unsupervised Learning: Finds hidden patterns in data without labeled examples
            3. Reinforcement Learning: Learns through interaction with an environment using rewards and penalties
            """
        }
    ]
    
    for i, sample in enumerate(samples, 1):
        print(f"{i}. {sample['title']}")
        print(f"   {sample['content'].strip()[:100]}...")
        print()

def main():
    """Main demo function."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check API key
    api_key_configured = check_api_key()
    print()
    
    # Show sample content
    show_sample_content()
    
    # Launch web UI
    if api_key_configured:
        print("🎯 Ready to launch! Your API key is configured.")
    else:
        print("🎯 Ready to launch! You can enter your API key in the web UI.")
    
    input("Press Enter to launch the web UI...")
    launch_web_ui()

if __name__ == "__main__":
    main()
