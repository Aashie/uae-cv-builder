"""
Purpose:
Extract structured information from raw job descriptions using external reference data.

Inputs:
Raw job description string.

Outputs:
Structured Python dictionary.

Dependencies:
re (Regex)
utils.reference_loader
"""

import re
from utils.reference_loader import load_reference_data
from models.job_description import JobDescription

# Load data dynamically from JSON files
SKILLS_DATABASE = load_reference_data('skills.json')
SOFT_SKILLS_DATABASE = load_reference_data('soft_skills.json')
EDUCATION_DATABASE = load_reference_data('education.json')
CERTIFICATIONS_DATABASE = load_reference_data('certifications.json')
EXPERIENCE_MAPPING = load_reference_data('experience_levels.json')

def extract_education(text):
    """Scan text for degree requirements using the external database."""
    text_lower = text.lower()
    for degree in EDUCATION_DATABASE:
        if degree.lower() in text_lower:
            return f"{degree} Degree"
    return "Not Specified"

def extract_experience_level(text):
    """Categorize the role based on seniority keywords."""
    text_lower = text.lower()
    for level, keywords in EXPERIENCE_MAPPING.items():
        if any(keyword in text_lower for keyword in keywords):
            return level
    return "Not Specified"

def _extract_skills_from_list(text, skill_list):
    """Internal helper to avoid code repetition."""
    found_skills = []
    text_lower = text.lower()
    for skill in skill_list:
        if skill in text_lower:
            found_skills.append(skill.title())
    return found_skills

def clean_job_description(raw_text):
    """Normalize whitespace and handle common formatting issues."""
    return raw_text.strip()

def extract_job_title(text):
    """Uses Regex to extract only the title."""
    patterns = [
        r"(?:looking for|seeking|hiring)\s+(?:an|a)\s+(.*?)(?:\.|,|\n)",
        r"^(.*?)(?:\.|,|\n)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()
    return "Unknown Title"

def extract_technical_skills(text):
    return _extract_skills_from_list(text, SKILLS_DATABASE)

def extract_soft_skills(text):
    return _extract_skills_from_list(text, SOFT_SKILLS_DATABASE)

def extract_certifications(text):
    """Scan text for professional certifications."""
    text_lower = text.lower()
    found_certs = []
    for cert in CERTIFICATIONS_DATABASE:
        if cert in text_lower:
            found_certs.append(cert.upper())
    return found_certs

def extract_keywords(job_title, skills, soft_skills):
    """Automatically build a keyword list from existing data."""
    # Combine everything into one list
    keywords = [job_title] + skills + soft_skills
    return list(set(keywords)) # 'set' removes duplicates

def parse_job_description(raw_text):
    """Orchestrator function returns a JobDescription object."""
    text = clean_job_description(raw_text)
    
    # 1. Extract the raw components
    title = extract_job_title(text)
    req_skills = extract_technical_skills(text)
    soft_skills = extract_soft_skills(text)
    
    # 2. Return the object with the new fields included
    return JobDescription(
        job_title=title,
        required_skills=req_skills,
        soft_skills=soft_skills,
        experience_level=extract_experience_level(text),
        education=extract_education(text),
        certifications=extract_certifications(text),
        keywords=extract_keywords(title, req_skills, soft_skills)
    )