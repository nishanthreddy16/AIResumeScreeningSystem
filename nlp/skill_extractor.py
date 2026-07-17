from nlp.preprocessing import clean_text
from nlp.skills import RECOMMENDATION_MAP, SKILL_KEYWORDS


def extract_skills(text: str) -> list[str]:
    """Extract known technical and professional skills from text."""
    normalized_text = f" {clean_text(text)} "
    detected_skills = []
    for skill in sorted(SKILL_KEYWORDS):
        if f" {skill.lower()} " in normalized_text or skill.lower() in normalized_text:
            detected_skills.append("scikit-learn" if skill == "sklearn" else skill)
    return sorted(set(detected_skills))


def match_skills(resume_text: str, job_description_text: str) -> tuple[list[str], list[str]]:
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description_text))
    matched_skills = sorted(resume_skills.intersection(job_skills))
    missing_skills = sorted(job_skills.difference(resume_skills))
    return matched_skills, missing_skills


def recommend_skills(missing_skills: list[str], resume_skills: list[str]) -> list[str]:
    recommendations = set(missing_skills)
    for skill in resume_skills:
        recommendations.update(RECOMMENDATION_MAP.get(skill.lower(), []))
    return sorted(skill for skill in recommendations if skill.lower() not in {s.lower() for s in resume_skills})[:10]

