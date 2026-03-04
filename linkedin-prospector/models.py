from dataclasses import dataclass
from typing import Optional


@dataclass
class Prospect:
    first_name: str
    last_name: str
    full_name: str
    title: str
    company: str
    company_size: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    source: str = ""
    apollo_id: Optional[str] = None
    # Populated after scoring
    score: Optional[int] = None
    verdict: Optional[str] = None
    reason: Optional[str] = None
    pain_angle: Optional[str] = None
    # Populated after messaging
    connection_message: Optional[str] = None
    pushaway_message: Optional[str] = None
    followup_dm: Optional[str] = None


@dataclass
class ScoringResult:
    score: int
    verdict: str
    reason: str
    best_pain_angle: str
