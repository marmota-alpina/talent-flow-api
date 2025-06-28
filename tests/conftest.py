"""
Pytest configuration and fixtures for the Talent Flow API tests.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import numpy as np

# Add the parent directory to the path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_model():
    """
    Fixture that provides a mock ML model for testing.
    """
    mock = MagicMock()
    # Configure the mock to return a fixed prediction and probability
    mock.predict.return_value = np.array([1])  # 1 corresponds to "Pleno"
    mock.predict_proba.return_value = np.array([[0.1, 0.7, 0.1, 0.1]])  # High confidence for "Pleno"
    return mock

@pytest.fixture
def mock_preprocessors():
    """
    Fixture that provides mock preprocessors for testing.
    """
    return {
        "scaler": MagicMock(),
        "education_encoder": MagicMock(),
        "tech_binarizer": MagicMock(),
        "skills_binarizer": MagicMock(),
        "vectorizer": MagicMock()
    }

@pytest.fixture
def sample_resume_payload():
    """
    Fixture that provides a sample resume payload for testing.
    """
    return {
        "userId": "test_user",
        "summary": "Experienced software developer with 5 years in Python and web development.",
        "professionalExperiences": [
            {
                "role": "Senior Developer",
                "isCurrent": True,
                "startDate": "2020-01-01",
                "endDate": None,
                "activitiesPerformed": [
                    {
                        "activity": "Developed RESTful APIs using FastAPI",
                        "problemSolved": "Improved API performance by 30%",
                        "technologies": ["Python", "FastAPI", "PostgreSQL"],
                        "appliedSoftSkills": ["Communication", "Problem Solving"]
                    }
                ]
            }
        ],
        "academicFormations": [
            {
                "level": "Bachelor"
            }
        ]
    }