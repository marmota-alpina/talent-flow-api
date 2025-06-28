"""
Utility functions for the Talent Flow API.
"""
from typing import Dict, Any, Tuple
import pickle
from datetime import datetime

def load_model_artifacts(model_path: str, preprocessors_path: str) -> Tuple[Any, Dict[str, Any]]:
    """
    Load the ML model and preprocessors from pickle files.
    
    Args:
        model_path: Path to the pickled model file
        preprocessors_path: Path to the pickled preprocessors file
        
    Returns:
        Tuple containing the model and preprocessors dictionary
    
    Raises:
        FileNotFoundError: If model or preprocessors files are not found
    """
    try:
        with open(model_path, 'rb') as model_file:
            model = pickle.load(model_file)
        
        with open(preprocessors_path, 'rb') as preprocessors_file:
            preprocessors = pickle.load(preprocessors_file)
            
        return model, preprocessors
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Required model file not found: {e}")

def extract_features_for_prediction(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract features from resume data for model prediction.
    
    Args:
        resume_data: Dictionary containing resume data
        
    Returns:
        Dictionary of extracted features
    """
    # Extract professional experiences
    experiences = resume_data.get("professionalExperiences", [])
    
    # Calculate total years of experience
    total_years = 0
    for exp in experiences:
        start_date = exp.get("startDate")
        end_date = exp.get("endDate")
        
        if start_date:
            start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
            end = datetime.fromisoformat(end_date) if isinstance(end_date, str) and end_date else datetime.now()
            
            # Calculate years between dates
            years = (end.year - start.year) - ((end.month, end.day) < (start.month, start.day))
            total_years += years
    
    # Count number of jobs
    number_of_jobs = len(experiences)
    
    # Calculate average years per job
    avg_years_per_job = total_years / number_of_jobs if number_of_jobs > 0 else 0
    
    # Extract highest education level
    academic_formations = resume_data.get("academicFormations", [])
    highest_education = academic_formations[0].get("level", "") if academic_formations else ""
    
    # Extract technologies and soft skills
    technologies = []
    soft_skills = []
    
    for exp in experiences:
        for activity in exp.get("activitiesPerformed", []):
            technologies.extend(activity.get("technologies", []))
            soft_skills.extend(activity.get("appliedSoftSkills", []))
    
    # Remove duplicates
    technologies = list(set(technologies))
    soft_skills = list(set(soft_skills))
    
    # Create full text for TF-IDF
    summary = resume_data.get("summary", "")
    full_text = summary
    
    for exp in experiences:
        for activity in exp.get("activitiesPerformed", []):
            if activity.get("activity"):
                full_text += " " + activity.get("activity")
            if activity.get("problemSolved"):
                full_text += " " + activity.get("problemSolved")
    
    return {
        "totalYearsExperience": total_years,
        "numberOfJobs": number_of_jobs,
        "avgYearsPerJob": avg_years_per_job,
        "highestEducationLevel": highest_education,
        "technologies": technologies,
        "softSkills": soft_skills,
        "fullText": full_text
    }