from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp.preprocessing import clean_text, preprocess_text
from nlp.skill_extractor import extract_skills, match_skills, recommend_skills


def calculate_tfidf_similarity(resume_text: str, job_description_text: str) -> float:
    """Calculate semantic similarity using TF-IDF and cosine similarity."""
    documents = [preprocess_text(resume_text), preprocess_text(job_description_text)]
    if not documents[0].strip() or not documents[1].strip():
        return 0.0

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(documents)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


def calculate_similarity_score(resume_text: str, job_description_text: str) -> float:
    """Backward-compatible helper used by tests and simple integrations."""
    return calculate_match_details("Candidate", resume_text, job_description_text)["match_score"]


def calculate_skill_coverage(matched_skills: list[str], missing_skills: list[str]) -> float:
    required_skill_count = len(matched_skills) + len(missing_skills)
    if required_skill_count == 0:
        return 0.0
    return round((len(matched_skills) / required_skill_count) * 100, 2)


def calculate_keyword_score(resume_text: str, job_description_text: str) -> float:
    resume_terms = set(preprocess_text(resume_text).split())
    job_terms = {term for term in preprocess_text(job_description_text).split() if len(term) > 2}
    if not job_terms:
        return 0.0
    return round((len(resume_terms.intersection(job_terms)) / len(job_terms)) * 100, 2)


def calculate_profile_strength(resume_text: str) -> float:
    """Reward resumes that contain the sections recruiters expect."""
    normalized = clean_text(resume_text)
    expected_signals = {
        "education": ["education", "b.tech", "bachelor", "degree"],
        "projects": ["project", "projects", "built", "developed"],
        "skills": ["skills", "technical skills", "tools"],
        "experience": ["experience", "internship", "work", "training"],
        "contact": ["email", "phone", "linkedin", "github"],
    }
    present = 0
    for keywords in expected_signals.values():
        if any(keyword in normalized for keyword in keywords):
            present += 1
    return round((present / len(expected_signals)) * 100, 2)


def extract_keyword_matches(resume_text: str, job_description_text: str) -> list[str]:
    resume_terms = set(preprocess_text(resume_text).split())
    job_terms = set(preprocess_text(job_description_text).split())
    keywords = sorted(term for term in resume_terms.intersection(job_terms) if len(term) > 2)
    return keywords[:25]


def get_hiring_recommendation(score: float) -> str:
    if score >= 80:
        return "Strong Shortlist"
    if score >= 65:
        return "Shortlist"
    if score >= 50:
        return "Consider After Skill Review"
    return "Needs Improvement"


def build_resume_summary(candidate_name: str, score: float, matched_skills: list[str], missing_skills: list[str]) -> str:
    top_matches = ", ".join(matched_skills[:6]) if matched_skills else "limited direct skill overlap"
    top_missing = ", ".join(missing_skills[:5]) if missing_skills else "no major required skills"
    if score >= 80:
        fit = "strong"
    elif score >= 65:
        fit = "good"
    elif score >= 50:
        fit = "moderate"
    else:
        fit = "developing"
    return (
        f"{candidate_name} is a {fit} match with an overall screening score of {score:.2f}%. "
        f"Matched strengths include {top_matches}. Key improvement areas include {top_missing}."
    )


def calculate_match_details(candidate_name: str, resume_text: str, job_description_text: str) -> dict:
    matched_skills, missing_skills = match_skills(resume_text, job_description_text)
    tfidf_similarity = calculate_tfidf_similarity(resume_text, job_description_text)
    skill_coverage = calculate_skill_coverage(matched_skills, missing_skills)
    keyword_score = calculate_keyword_score(resume_text, job_description_text)
    profile_strength = calculate_profile_strength(resume_text)
    score = round(
        (skill_coverage * 0.55)
        + (tfidf_similarity * 0.15)
        + (keyword_score * 0.20)
        + (profile_strength * 0.10),
        2,
    )
    return {
        "match_score": min(score, 100.0),
        "tfidf_similarity": tfidf_similarity,
        "skill_coverage": skill_coverage,
        "keyword_score": keyword_score,
        "profile_strength": profile_strength,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "summary": build_resume_summary(candidate_name, min(score, 100.0), matched_skills, missing_skills),
        "recommendation": get_hiring_recommendation(min(score, 100.0)),
    }


def analyze_resume(candidate_name: str, resume_text: str, job_description_text: str) -> dict:
    details = calculate_match_details(candidate_name, resume_text, job_description_text)
    resume_skills = extract_skills(resume_text)
    recommended_skills = recommend_skills(details["missing_skills"], resume_skills)
    keyword_matches = extract_keyword_matches(resume_text, job_description_text)
    details.update(
        {
            "recommended_skills": recommended_skills,
            "keyword_matches": keyword_matches,
        }
    )
    return details
