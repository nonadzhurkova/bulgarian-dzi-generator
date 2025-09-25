#!/usr/bin/env python3
"""
All Questions Viewer Runner
Shows both real and generated questions in one interface
"""

import subprocess
import sys
import os

def main():
    print("📚 Starting All Questions Viewer...")
    print("✅ Shows both real and generated questions")
    print("📱 The app will open in your browser automatically")
    print("🔗 If it doesn't open, go to: http://localhost:8508")
    print("=" * 50)
    
    try:
        # Run the all questions app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_all_questions.py",
            "--server.port", "8508",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
