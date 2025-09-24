#!/usr/bin/env python3
"""
Run script for RAG Question Generator
"""

import subprocess
import sys
import os

def main():
    print("🧠 Starting RAG Question Generator...")
    print("✅ Starting RAG Question Generator app...")
    print("📱 The app will open in your browser automatically")
    print("🔗 If it doesn't open, go to: http://localhost:8503")
    print("=" * 50)
    
    try:
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app_rag_generator.py",
            "--server.port", "8503",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main()
