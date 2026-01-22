"""Test server with detailed logging."""
import logging
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    logger.info("Startup event triggered")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown event triggered")

if __name__ == "__main__":
    logger.info("Starting uvicorn server...")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
