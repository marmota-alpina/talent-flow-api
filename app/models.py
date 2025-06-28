from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ActivityPerformed(BaseModel):
    """Model for activities performed in a professional experience."""
    activity: Optional[str] = None
    problemSolved: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    appliedSoftSkills: List[str] = Field(default_factory=list)

class ProfessionalExperience(BaseModel):
    """Model for professional experience entries."""
    role: Optional[str] = None
    isCurrent: Optional[bool] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    activitiesPerformed: List[ActivityPerformed] = Field(default_factory=list)

class AcademicFormation(BaseModel):
    """Model for academic formation entries."""
    level: Optional[str] = None

class ResumePayload(BaseModel):
    """Model for the resume classification request payload."""
    userId: str
    summary: Optional[str] = None
    professionalExperiences: List[ProfessionalExperience] = Field(default_factory=list)
    academicFormations: List[AcademicFormation] = Field(default_factory=list)

class ClassificationResponse(BaseModel):
    """Model for the resume classification response."""
    userId: str
    predictedExperienceLevel: str
    confidenceScore: float