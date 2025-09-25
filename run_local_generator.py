"""
Run Local AI Question Generator
For local development only - generates questions using AI/RAG
"""
import subprocess
import sys
import os

def main():
    print("🧠 Starting Local AI Question Generator...")
    print("📍 This is for local development only!")
    print("🚀 For deployment, use: streamlit run app_real_matura.py")
    print("-" * 50)
    
    try:
        # Run the local generator
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "local_question_generator.py", 
            "--server.port", "8502"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Local generator stopped by user")
    except Exception as e:
        print(f"❌ Error running local generator: {e}")

if __name__ == "__main__":
    main()
