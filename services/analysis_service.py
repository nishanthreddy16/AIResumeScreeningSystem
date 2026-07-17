import json
from datetime import datetime

from database.connection import get_connection
from ml.scoring import analyze_resume
from services.job_service import get_job_description
from services.resume_service import get_all_resumes, get_resume


def run_analysis(resume_id: int, job_id: int) -> dict:
    resume = get_resume(resume_id)
    job = get_job_description(job_id)
    if not resume or not job:
        raise ValueError("Please select a valid resume and job description.")

    result = analyze_resume(resume["candidate_name"], resume["extracted_text"], job["description"])
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO Analysis (
                resume_id, job_id, match_score, matched_skills, missing_skills,
                recommended_skills, keyword_matches, summary, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resume_id,
                job_id,
                result["match_score"],
                json.dumps(result["matched_skills"]),
                json.dumps(result["missing_skills"]),
                json.dumps(result["recommended_skills"]),
                json.dumps(result["keyword_matches"]),
                result["summary"],
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        result["analysis_id"] = int(cursor.lastrowid)
    result["candidate_name"] = resume["candidate_name"]
    result["job_title"] = job["title"]
    return result


def rank_candidates(job_id: int) -> list[dict]:
    job = get_job_description(job_id)
    if not job:
        return []
    ranking = []
    for resume in get_all_resumes():
        result = analyze_resume(resume["candidate_name"], resume["extracted_text"], job["description"])
        ranking.append(
            {
                "Candidate": resume["candidate_name"],
                "Resume ID": resume["resume_id"],
                "Score": result["match_score"],
                "Recommendation": result["recommendation"],
                "Skill Coverage": result["skill_coverage"],
                "Matched Skills": ", ".join(result["matched_skills"]),
                "Missing Skills": ", ".join(result["missing_skills"]),
            }
        )
    return sorted(ranking, key=lambda item: item["Score"], reverse=True)


def get_dashboard_metrics() -> dict:
    with get_connection() as connection:
        total_resumes = connection.execute("SELECT COUNT(*) AS count FROM Resumes").fetchone()["count"]
        average_score = connection.execute("SELECT AVG(match_score) AS avg_score FROM Analysis").fetchone()["avg_score"]
        best = connection.execute(
            """
            SELECT c.candidate_name, a.match_score
            FROM Analysis a
            JOIN Resumes r ON r.resume_id = a.resume_id
            JOIN Candidates c ON c.candidate_id = r.candidate_id
            ORDER BY a.match_score DESC
            LIMIT 1
            """
        ).fetchone()
        worst = connection.execute(
            """
            SELECT c.candidate_name, a.match_score
            FROM Analysis a
            JOIN Resumes r ON r.resume_id = a.resume_id
            JOIN Candidates c ON c.candidate_id = r.candidate_id
            ORDER BY a.match_score ASC
            LIMIT 1
            """
        ).fetchone()
        recent = connection.execute(
            """
            SELECT c.candidate_name, r.file_name, r.uploaded_at
            FROM Resumes r
            JOIN Candidates c ON c.candidate_id = r.candidate_id
            ORDER BY r.uploaded_at DESC
            LIMIT 5
            """
        ).fetchall()
    return {
        "total_resumes": total_resumes,
        "average_score": round(float(average_score or 0), 2),
        "best_candidate": dict(best) if best else None,
        "worst_candidate": dict(worst) if worst else None,
        "recent_uploads": [dict(row) for row in recent],
    }
