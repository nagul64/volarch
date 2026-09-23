from pydantic import BaseModel


class Student(BaseModel):
    id: int
    name: str
    school: str
    grade: str
    zip_code: str
    latitude: float
    longitude: float
    max_hours_per_week: int
    skills: list[str]
    interests: list[str]
    bio: str


class Opportunity(BaseModel):
    id: int
    title: str
    org_name: str
    category: str
    description: str
    tags: list[str]
    zip_code: str
    latitude: float
    longitude: float
    hours_min: int
    hours_max: int
    required_skills: list[str]
    helpful_skills: list[str]


class ScoreFactor(BaseModel):
    name: str
    weight: float
    score: int
    note: str


class MatchResult(BaseModel):
    opportunity: Opportunity
    total: int
    breakdown: list[ScoreFactor]
    reasons: list[str]


class SemanticDiagnostics(BaseModel):
    provider: str
    description: str


class SearchRequest(BaseModel):
    query: str
    zip: str | None = None


class SearchProfile(BaseModel):
    skills: list[str]
    interests: list[str]
    max_hours_per_week: int
    zip_code: str
    bio: str
    latitude: float | None = None
    longitude: float | None = None


class SearchResult(BaseModel):
    extraction: str
    semantic: str
    profile: SearchProfile
    matches: list[MatchResult]