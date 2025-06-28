import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import config
from app.models import ResumePayload, ClassificationResponse
from app.services.prediction_service import ResumeClassifierService

# Logger setup
logger.remove()
logger.add(sys.stdout, level=config.log.level, format=config.log.format)

# App
app = FastAPI(
    title=config.api.title,
    description=config.api.description,
    version=config.api.version,
    debug=config.debug,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate service
classifier_service = ResumeClassifierService()

@app.get("/")
async def root():
    return {
        "api": config.api.title,
        "version": config.api.version,
        "status": "online",
    }

@app.post("/classify-resume/", response_model=ClassificationResponse)
async def classify_resume(payload: ResumePayload):
    try:
        return classifier_service.predict(payload)
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))
