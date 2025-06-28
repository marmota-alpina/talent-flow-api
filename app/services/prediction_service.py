import numpy as np
import hashlib
import json
from typing import Dict
from app.models import ResumePayload
from app.utils import load_model_artifacts, extract_features_for_prediction
from app.config import config
from datetime import datetime


class ResumeClassifierService:
    def __init__(self):
        self.model, self.artifacts = load_model_artifacts(
            config.model.model_path,
            config.model.preprocessors_path
        )

    def predict(self, resume: ResumePayload) -> Dict[str, str]:
        features = extract_features_for_prediction(resume.model_dump())
        processed_features = self._preprocess_features(features)
        prediction_encoded = self.model.predict(processed_features)[0]
        predicted_level = self._decode_prediction(prediction_encoded)
        confidence_score = float(self.model.predict_proba(processed_features).max())
        resume_hash = self._generate_resume_hash(resume)

        return {
            "userId": resume.userId,
            "predictedExperienceLevel": predicted_level,
            "confidenceScore": confidence_score,
            "hash": resume_hash
        }

    def _preprocess_features(self, features: dict) -> np.ndarray:
        num_order = self.artifacts['numerical_features_order']
        scaler = self.artifacts['scaler']
        ohe = self.artifacts['one_hot_encoder']
        mlb_tech = self.artifacts['mlb_tech']
        mlb_skills = self.artifacts['mlb_skills']
        tfidf = self.artifacts['tfidf_vectorizer']

        num_features = scaler.transform([[features[n] for n in num_order]])
        edu_features = ohe.transform([[features["highestEducationLevel"]]])
        tech_features = mlb_tech.transform([features["technologies"]])
        skills_features = mlb_skills.transform([features["softSkills"]])
        text_features = tfidf.transform([features["fullText"]]).toarray()

        return np.concatenate([
            num_features,
            edu_features,
            tech_features,
            skills_features,
            text_features
        ], axis=1)

    def _decode_prediction(self, encoded_label: int) -> str:
        inverse_map = {v: k for k, v in self.artifacts['level_mapping'].items()}
        return inverse_map.get(encoded_label, "Desconhecido")

    def _generate_resume_hash(self, resume: ResumePayload) -> str:
        """Gera um hash SHA-256 a partir do conteúdo do currículo."""

        def convert(obj):
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(v) for v in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        raw = resume.model_dump()
        converted = convert(raw)
        resume_json = json.dumps(converted, sort_keys=True)
        return hashlib.sha256(resume_json.encode("utf-8")).hexdigest()

