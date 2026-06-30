"""
HackForge AI — Entry Point
Run with: python run.py
"""
import os
import sys
import uvicorn

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[HackForge] .env file loaded.")
except ImportError:
    print("[HackForge] python-dotenv not installed. Skipping .env load.")

if __name__ == "__main__":
    print("=" * 60)
    print("  HackForge AI — Multi-Agent Hackathon Copilot")
    print("  Starting server at http://127.0.0.1:8000")
    print("  Open http://127.0.0.1:8000 in your browser")
    print("=" * 60)
    
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
