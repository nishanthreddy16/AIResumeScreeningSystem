from ml.scoring import analyze_resume, calculate_similarity_score
from nlp.skill_extractor import extract_skills, match_skills


def test_skill_extraction_detects_common_skills():
    text = "Python developer with SQL, Pandas, NumPy, Streamlit and Machine Learning experience."
    skills = extract_skills(text)
    assert "python" in skills
    assert "sql" in skills
    assert "machine learning" in skills


def test_skill_matching_returns_missing_skills():
    resume = "Python pandas numpy streamlit"
    job = "Python pandas numpy streamlit sql machine learning"
    matched, missing = match_skills(resume, job)
    assert "python" in matched
    assert "sql" in missing


def test_similarity_score_is_numeric_percentage():
    score = calculate_similarity_score("python machine learning pandas", "python pandas machine learning")
    assert 0 <= score <= 100


def test_analysis_returns_professional_breakdown():
    result = analyze_resume(
        "Test Candidate",
        "Python SQL Pandas NumPy Scikit-learn Streamlit projects education email phone",
        "Python SQL Pandas NumPy Scikit-learn Streamlit machine learning",
    )
    assert result["match_score"] >= 50
    assert result["skill_coverage"] > 0
    assert result["recommendation"] in {
        "Strong Shortlist",
        "Shortlist",
        "Consider After Skill Review",
        "Needs Improvement",
    }
