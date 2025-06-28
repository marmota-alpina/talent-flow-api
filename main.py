"""
Entry point for the Talent Flow API.
This file imports the FastAPI app from the app module.
"""
from app.main import app

# This file is kept for backward compatibility
# The actual implementation is in app/main.py

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
