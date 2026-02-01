"""Application entry point."""

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print("""
    =============================================
         ShopBuddy AI - Enterprise Edition
                   Version 4.0.0
    =============================================
    """)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )