"""
Main FastAPI application for the Talent Flow API.
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

from app.models import ResumePayload, ClassificationResponse
from app.utils import load_model_artifacts, extract_features_for_prediction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("talent-flow-api")

# Create FastAPI app
app = FastAPI(
    title="Talent Flow API",
    description="API for classifying resumes by experience level",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:4200",  # Angular development server
    "https://talent-flow-webapp.web.app",  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML model and preprocessors on startup
MODEL_PATH = os.path.join("ml", "talent_flow_classifier.pkl")
PREPROCESSORS_PATH = os.path.join("ml", "talent_flow_preprocessors.pkl")

try:
    model, preprocessors = load_model_artifacts(MODEL_PATH, PREPROCESSORS_PATH)
    logger.info("ML model and preprocessors loaded successfully")
except FileNotFoundError as e:
    logger.error(f"Failed to load ML model or preprocessors: {e}")
    raise RuntimeError("Application failed to start: ML model files not found")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "api": "Talent Flow API",
        "version": "1.0.0",
        "status": "online",
    }

@app.post("/classify-resume/", response_model=ClassificationResponse)
async def classify_resume(payload: ResumePayload):
    """
    Classify a resume by experience level.

    Args:
        payload: Resume data in the format specified by ResumePayload

    Returns:
        ClassificationResponse with predicted experience level and confidence score
    """
    logger.info(f"Received classification request for user: {payload.userId}")

    try:
        # Extract features from resume data
        features = extract_features_for_prediction(payload.model_dump())

        # Apply preprocessing steps as described in RF-003
        # 1. Extract numerical features
        numerical_features = np.array([
            features["totalYearsExperience"],
            features["numberOfJobs"],
            features["avgYearsPerJob"]
        ]).reshape(1, -1)

        # 2. Apply MinMaxScaler to numerical features
        scaled_numerical = preprocessors["scaler"].transform(numerical_features)

        # 3. Apply OneHotEncoder to education level
        # Map unknown education levels to known ones
        known_education_levels = ["Graduação", "Pós-graduação", "MBA", "Doutorado", "Técnico", "Especialização", "Nenhum"]
        if features["highestEducationLevel"] not in known_education_levels:
            # Map "Mestrado" to "Pós-graduação" as a fallback
            if features["highestEducationLevel"] == "Mestrado":
                features["highestEducationLevel"] = "Pós-graduação"
            else:
                features["highestEducationLevel"] = "Graduação"  # Default fallback

        education_encoded = preprocessors["one_hot_encoder"].transform(
            [[features["highestEducationLevel"]]]
        )
        # Convert to dense array if it's a sparse matrix
        if hasattr(education_encoded, 'toarray'):
            education_encoded = education_encoded.toarray()

        # 4. Apply MultiLabelBinarizer to technologies and soft skills
        tech_encoded = preprocessors["mlb_tech"].transform([features["technologies"]])
        # Convert to dense array if it's a sparse matrix
        if hasattr(tech_encoded, 'toarray'):
            tech_encoded = tech_encoded.toarray()

        skills_encoded = preprocessors["mlb_skills"].transform([features["softSkills"]])
        # Convert to dense array if it's a sparse matrix
        if hasattr(skills_encoded, 'toarray'):
            skills_encoded = skills_encoded.toarray()

        # 5. Apply TfidfVectorizer to full text
        text_features = preprocessors["tfidf_vectorizer"].transform([features["fullText"]])
        # Convert to dense array if it's a sparse matrix
        if hasattr(text_features, 'toarray'):
            text_features = text_features.toarray()

        # 6. Concatenate all features
        all_features = np.hstack([
            scaled_numerical,
            education_encoded,
            tech_encoded,
            skills_encoded,
            text_features
        ])

        # Make prediction
        prediction = model.predict(all_features)[0]
        prediction_proba = model.predict_proba(all_features)[0]
        confidence_score = float(np.max(prediction_proba))

        # Map prediction to experience level
        experience_levels = ["Júnior", "Pleno", "Sênior", "Especialista"]
        predicted_level = experience_levels[prediction]

        # Create response
        response = ClassificationResponse(
            userId=payload.userId,
            predictedExperienceLevel=predicted_level,
            confidenceScore=confidence_score
        )

        logger.info(f"Classification completed for user {payload.userId}: {predicted_level} (confidence: {confidence_score:.2f})")
        return response

    except Exception as e:
        logger.error(f"Error processing classification request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing classification request: {str(e)}"
        )
