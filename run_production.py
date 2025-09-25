"""
Run Production DZI Matura App
Reads real questions + AI questions from ai-data folder
No AI generation, no imports - just displays questions
"""
import subprocess
import sys

def main():
    print("🚀 Starting Production DZI Matura App...")
    print("📚 Reads real questions + AI questions from ai-data folder")
    print("🤖 No AI generation, no imports - just displays questions")
    print("-" * 50)
    
    try:
        # Run the production app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app_production.py", 
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Production app stopped by user")
    except Exception as e:
        print(f"❌ Error running production app: {e}")

if __name__ == "__main__":
    main()
