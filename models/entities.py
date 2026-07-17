from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    candidate_id: int
    candidate_name: str
    email: str | None
    phone: str | None


@dataclass(frozen=True)
class Resume:
    resume_id: int
    candidate_id: int
    candidate_name: str
    file_name: str
    file_path: str
    extracted_text: str
    uploaded_at: str


@dataclass(frozen=True)
class JobDescription:
    job_id: int
    title: str
    description: str
    created_at: str


@dataclass(frozen=True)
class AnalysisResult:
    resume_id: int
    job_id: int
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    recommended_skills: list[str]
    keyword_matches: list[str]
    summary: str

