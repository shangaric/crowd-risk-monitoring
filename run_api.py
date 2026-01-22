"""
Run the FastAPI backend server
"""
import uvicorn
import config

if __name__ == "__main__":
    uvicorn.run(
        "backend.api:app",
        host=config.API_CONFIG["host"],
        port=config.API_CONFIG["port"],
        reload=True
    )
