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
    companyName: Optional[str] = None
    experienceType: Optional[str] = None
    role: Optional[str] = None
    isCurrent: Optional[bool] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    activitiesPerformed: List[ActivityPerformed] = Field(default_factory=list)

class AcademicFormation(BaseModel):
    """Model for academic formation entries."""
    level: Optional[str] = None
    courseName: Optional[str] = None
    institution: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class LanguageEntry(BaseModel):
    language: Optional[str] = None
    proficiency: Optional[str] = None

class ResumePayload(BaseModel):
    """Model for the resume classification request payload."""
    userId: str
    fullName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedinUrl: Optional[str] = None
    mainArea: Optional[str] = None
    experienceLevel: Optional[str] = None
    summary: Optional[str] = None
    academicFormations: List[AcademicFormation] = Field(default_factory=list)
    professionalExperiences: List[ProfessionalExperience] = Field(default_factory=list)
    languages: Optional[List[LanguageEntry]] = Field(default_factory=list)
    status: Optional[str] = None

class ClassificationResponse(BaseModel):
    """Model for the resume classification response."""
    userId: str
    predictedExperienceLevel: str
    confidenceScore: float
    hash: str
