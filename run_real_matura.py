#!/usr/bin/env python3
"""
Script to run the Real Matura Questions app
"""
import subprocess
import sys

def main():
    """Run the real matura questions app"""
    print("📚 Starting Real DZI Matura Questions...")
    print("✅ Starting Real Matura Questions app...")
    print("📱 The app will open in your browser automatically")
    print("🔗 If it doesn't open, go to: http://localhost:8502")
    print("=" * 50)
    
    try:
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_real_matura.py",
            "--server.port", "8502",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

if __name__ == "__main__":
    main()
