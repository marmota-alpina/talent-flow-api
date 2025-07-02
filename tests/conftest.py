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