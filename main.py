import sys
import uvicorn
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def launch_server():
    print("==================================================")
    print("[ProjectPulse AI] Production Platform")
    print("==================================================")
    print("Launching FastAPI Server & Dashboard at: http://127.0.0.1:8000")
    print("==================================================")
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    launch_server()
