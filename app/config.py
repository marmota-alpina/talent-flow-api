"""
Configuration module for the Talent Flow API.

This module provides centralized configuration management with support for
different environments (development, testing, production) and .env files.
"""

import os
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Environment(str, Enum):
    """Enum for different environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class LogConfig(BaseModel):
    """Configuration for logging."""
    level: str
    format: str
    file_path: Optional[str] = None

class APIConfig(BaseModel):
    """Configuration for the API."""
    title: str
    version: str
    description: str
    cors_origins: list[str]

class ModelConfig(BaseModel):
    """Configuration for ML models."""
    model_path: str
    preprocessors_path: str

class Config(BaseModel):
    """Main configuration class."""
    env: Environment
    debug: bool
    api: APIConfig
    log: LogConfig
    model: ModelConfig

# Default configurations
default_config = {
    Environment.DEVELOPMENT: {
        "debug": True,
        "api": {
            "title": "Talent Flow API",
            "version": "1.0.0",
            "description": "API for classifying resumes by experience level",
            "cors_origins": [
                "http://localhost",
                "http://localhost:4200",
                "https://talent-flow-webapp.web.app"
            ]
        },
        "log": {
            "level": "DEBUG",
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        },
        "model": {
            "model_path": "ml/talent_flow_classifier.pkl",
            "preprocessors_path": "ml/talent_flow_preprocessors.pkl"
        }
    },
    Environment.TESTING: {
        "debug": True,
        "api": {
            "title": "Talent Flow API (Test)",
            "version": "1.0.0",
            "description": "API for classifying resumes by experience level (Test Environment)",
            "cors_origins": [
                "http://localhost",
                "http://localhost:4200"
            ]
        },
        "log": {
            "level": "INFO",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        },
        "model": {
            "model_path": "ml/talent_flow_classifier.pkl",
            "preprocessors_path": "ml/talent_flow_preprocessors.pkl"
        }
    },
    Environment.PRODUCTION: {
        "debug": False,
        "api": {
            "title": "Talent Flow API",
            "version": "1.0.0",
            "description": "API for classifying resumes by experience level",
            "cors_origins": [
                "https://talent-flow-webapp.web.app"
            ]
        },
        "log": {
            "level": "WARNING",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            "file_path": "logs/talent_flow_api.log"
        },
        "model": {
            "model_path": "ml/talent_flow_classifier.pkl",
            "preprocessors_path": "ml/talent_flow_preprocessors.pkl"
        }
    }
}

def get_environment() -> Environment:
    """
    Get the current environment from environment variables.
    
    Returns:
        Environment: The current environment (development, testing, or production)
    """
    env_str = os.getenv("ENVIRONMENT", "development").lower()
    if env_str == "production":
        return Environment.PRODUCTION
    elif env_str == "testing":
        return Environment.TESTING
    else:
        return Environment.DEVELOPMENT

def get_config() -> Config:
    """
    Get the configuration for the current environment.
    
    Returns:
        Config: The configuration object for the current environment
    """
    env = get_environment()
    config_dict = default_config[env]
    
    # Override with environment variables if they exist
    if os.getenv("DEBUG"):
        config_dict["debug"] = os.getenv("DEBUG").lower() in ("true", "1", "t")
    
    if os.getenv("LOG_LEVEL"):
        config_dict["log"]["level"] = os.getenv("LOG_LEVEL")
    
    if os.getenv("MODEL_PATH"):
        config_dict["model"]["model_path"] = os.getenv("MODEL_PATH")
    
    if os.getenv("PREPROCESSORS_PATH"):
        config_dict["model"]["preprocessors_path"] = os.getenv("PREPROCESSORS_PATH")
    
    # Create and return the Config object
    config_dict["env"] = env
    return Config(**config_dict)

# Export the configuration
config = get_config()