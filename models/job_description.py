"""
Purpose:
Defines the structure of a Job Description object.

Dependencies:
dataclasses (Built-in Python library)
typing (Built-in Python library)
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class JobDescription:
    job_title: str
    required_skills: List[str]
    soft_skills: List[str]
    experience_level: str
    education: str
    certifications: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)