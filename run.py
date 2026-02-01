"""
Application entry point.
"""
import uvicorn
import os
import sys
from dotenv import load_dotenv

# 1. Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "true").lower() == "true"

    print("🔍 Checking imports...")
    
    try:
        # CHANGE 1: Import from app.main instead of main
        from app.main import app
        print("✅ app/main.py successfully imported!")
    except Exception as e:
        print("\n❌ CRITICAL ERROR:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print(f"""
    =============================================
         ShopBuddy AI - Enterprise Edition
                   Version 4.0.0
    =============================================
    Server: http://{host}:{port}
    Docs:   http://{host}:{port}/docs
    =============================================
    """)
    
    # CHANGE 2: "app.main:app" tells uvicorn to look inside app folder
    uvicorn.run(
        "app.main:app", 
        host=host,
        port=port,
        reload=debug,
        reload_dirs=["app"]
    )