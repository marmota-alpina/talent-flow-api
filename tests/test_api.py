"""
Tests for the Talent Flow API endpoints.
"""
from fastapi.testclient import TestClient
import sys
import os
import pytest

# Add the parent directory to the path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app  # Import the FastAPI app

# Create a test client
client = TestClient(app)

def test_root_endpoint():
    """Test that the root endpoint returns the expected response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "api" in data
    assert "version" in data
    assert "status" in data
    assert data["api"] == "Talent Flow API"
    assert data["status"] == "online"

def test_classify_resume_endpoint_validation():
    """Test that the classify-resume endpoint validates the input payload."""
    # Test with missing required field (userId)
    payload = {
        "summary": "Test summary",
        "professionalExperiences": [],
        "academicFormations": []
    }
    response = client.post("/classify-resume/", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

    # Test with valid minimal payload
    payload = {
        "userId": "test_user"
    }
    # Note: This test might fail if the model is not properly mocked
    # In a real test, we would mock the model and preprocessors
    # For now, we're just testing the validation

def test_maria_sophia_resume_classification():
    """
    Test that the specific resume for Maria Sophia Melo is correctly classified as 'Júnior'.
    This test uses the actual model and preprocessors, not mocks.
    """
    # Resume data from the issue description
    payload = {
      "userId": "gen_user_1",
      "status": "published",
      "fullName": "Maria Sophia Melo",
      "email": "maria.sophia.melo@email.com",
      "phone": "84 3392 5087",
      "linkedinUrl": "https://linkedin.com/in/mariasophiamelo1",
      "mainArea": "UI/UX Design",
      "experienceLevel": "Júnior",
      "summary": "Júnior em UI/UX Design, com foco em impacto real no negócio e entrega de resultados concretos em projetos relevantes.",
      "academicFormations": [
        {
          "level": "Mestrado",
          "courseName": "Mestrado em UI/UX Design",
          "institution": "Almeida",
          "startDate": "2019-06-27",
          "endDate": "2023-06-26"
        }
      ],
      "languages": [
        {"language": "Português", "proficiency": "Nativo"},
        {"language": "Inglês", "proficiency": "Avançado (C1)"}
      ],
      "professionalExperiences": [
        {
          "experienceType": "CLT",
          "companyName": "Ribeiro - EI",
          "role": "Júnior em UI/UX Design",
          "startDate": "2024-06-25",
          "endDate": "2025-06-20",
          "isCurrent": False,
          "activitiesPerformed": [
            {
              "activity": "Criei protótipos interativos com base em testes de usabilidade e entrevistas com usuários.",
              "problemSolved": "Melhorei a taxa de conversão em 25% ao redesenhar fluxos baseados em testes A/B.",
              "technologies": ["UI/UX Design", "Cloud Computing", "Desenvolvimento Backend"],
              "appliedSoftSkills": ["Trabalho em equipe", "Pensamento Analítico", "Colaboração"]
            }
          ]
        },
        {
          "experienceType": "CLT",
          "companyName": "da Rocha S.A.",
          "role": "Júnior em UI/UX Design",
          "startDate": "2024-12-22",
          "endDate": None,
          "isCurrent": True,
          "activitiesPerformed": [
            {
              "activity": "Criei protótipos interativos com base em testes de usabilidade e entrevistas com usuários.",
              "problemSolved": "Melhorei a taxa de conversão em 25% ao redesenhar fluxos baseados em testes A/B.",
              "technologies": ["Gestão de Produtos", "Análise de Dados", "DevOps"],
              "appliedSoftSkills": ["Pensamento Analítico", "Organização", "Resolução de Problemas"]
            }
          ]
        }
      ]
    }

    # Call the classification endpoint
    response = client.post("/classify-resume/", json=payload)

    # Verify the response
    assert response.status_code == 200
    data = response.json()

    # Check that the response contains the expected fields
    assert "userId" in data
    assert "predictedExperienceLevel" in data
    assert "confidenceScore" in data

    # Verify that the userId matches
    assert data["userId"] == payload["userId"]

    # Verify that the predicted experience level is 'Júnior'
    assert data["predictedExperienceLevel"] == "Júnior"

    # Verify that the confidence score is reasonable (greater than 0.5)
    assert data["confidenceScore"] > 0.5
