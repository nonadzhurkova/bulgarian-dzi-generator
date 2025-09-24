#!/usr/bin/env python3
"""
Script to run the DZI Question Generator app
"""
import subprocess
import sys
import os

def main():
    """Run the question generator app"""
    print("📝 Starting Bulgarian DZI Question Generator...")
    print("✅ Starting Question Generator app...")
    print("📱 The app will open in your browser automatically")
    print("🔗 If it doesn't open, go to: http://localhost:8501")
    print("=" * 50)
    
    try:
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_questions.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main()
