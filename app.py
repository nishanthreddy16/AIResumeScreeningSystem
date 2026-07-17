from pathlib import Path

import pandas as pd
import streamlit as st

from database.init_db import initialize_database
from services.analysis_service import get_dashboard_metrics, rank_candidates, run_analysis
from services.auth_service import authenticate_user
from services.job_service import (
    get_all_job_descriptions,
    job_description_exists,
    save_job_description,
    save_uploaded_job_description,
)
from services.report_service import generate_pdf_report
from services.resume_service import (
    add_sample_resume,
    delete_resume,
    get_all_resumes,
    resume_exists_by_file_name,
    save_uploaded_resume,
)
from utils.charts import (
    candidate_ranking_chart,
    score_breakdown_chart,
    score_gauge,
    skills_bar_chart,
    skills_pie_chart,
)


BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "static" / "css" / "style.css"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"


st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon=":page_facing_up:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    if CSS_PATH.exists():
        st.markdown(f"<style>{CSS_PATH.read_text()}</style>", unsafe_allow_html=True)


def initialize_session() -> None:
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("latest_result", None)


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f"<h1 class='app-title'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def pill(label: str, value: str, class_name: str = "pill") -> None:
    st.markdown(f"<span class='{class_name}'>{label}: {value}</span>", unsafe_allow_html=True)


def load_sample_dataset() -> tuple[int, int]:
    resume_count = 0
    job_count = 0
    samples = [
        ("sample_ai_engineer_resume.pdf", "Aarav Sharma"),
        ("sample_data_analyst_resume.pdf", "Priya Menon"),
    ]
    for file_name, candidate_name in samples:
        if not resume_exists_by_file_name(file_name):
            add_sample_resume(SAMPLE_DATA_DIR / file_name, candidate_name)
            resume_count += 1

    title = "Machine Learning Engineer Intern"
    if not job_description_exists(title):
        save_job_description(title, (SAMPLE_DATA_DIR / "sample_job_description.txt").read_text())
        job_count += 1
    return resume_count, job_count


def login_page() -> None:
    page_header("AI Resume Screening System", "A simple offline tool to compare resumes with a job description.")
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        st.markdown("<div class='section-panel'>", unsafe_allow_html=True)
        st.subheader("Admin Login")
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="admin123")
        if st.button("Login", use_container_width=True):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.info("Default credentials: admin / admin123")
        st.markdown("</div>", unsafe_allow_html=True)


def sidebar_navigation() -> str:
    st.sidebar.title("Navigation")
    st.sidebar.caption(f"Logged in as {st.session_state.username}")
    page = st.sidebar.radio(
        "Go to",
        [
            "Dashboard",
            "Resume Management",
            "Job Description",
            "Resume Analysis",
            "Candidate Ranking",
            "Reports",
            "Project Notes",
        ],
    )
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.latest_result = None
        st.rerun()
    return page


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_page() -> None:
    page_header("Dashboard", "Quick view of uploaded resumes, saved analyses, and recent activity.")
    metrics = get_dashboard_metrics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Resumes", str(metrics["total_resumes"]))
    with col2:
        metric_card("Average Match Score", f"{metrics['average_score']}%")
    with col3:
        best = metrics["best_candidate"]
        metric_card("Best Candidate", best["candidate_name"] if best else "N/A")
    with col4:
        worst = metrics["worst_candidate"]
        metric_card("Worst Candidate", worst["candidate_name"] if worst else "N/A")

    st.divider()
    action_col, info_col = st.columns([1, 2])
    with action_col:
        if st.button("Load Sample Dataset", use_container_width=True):
            try:
                resume_count, job_count = load_sample_dataset()
                st.success(f"Sample data ready. Added {resume_count} resumes and {job_count} job descriptions.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    with info_col:
        st.info("For a quick demo, load the sample data. For your own testing, upload resumes and add a job description.")

    st.subheader("Recent Uploads")
    if metrics["recent_uploads"]:
        st.dataframe(pd.DataFrame(metrics["recent_uploads"]), use_container_width=True, hide_index=True)
    else:
        st.info("No resumes uploaded yet.")


def resume_management_page() -> None:
    page_header("Resume Management", "Add candidate resumes and check the extracted text before screening.")
    upload_col, list_col = st.columns([1, 1.4])

    with upload_col:
        st.subheader("Upload Resume")
        with st.form("resume_upload_form", clear_on_submit=True):
            candidate_name = st.text_input("Candidate Name")
            uploaded_file = st.file_uploader("Resume PDF", type=["pdf"])
            submitted = st.form_submit_button("Save Resume", use_container_width=True)
        if submitted:
            try:
                resume_id = save_uploaded_resume(uploaded_file, candidate_name)
                st.success(f"Resume saved successfully. Resume ID: {resume_id}")
            except Exception as exc:
                st.error(str(exc))

    with list_col:
        st.subheader("Uploaded Resumes")
        resumes = get_all_resumes()
        if not resumes:
            st.info("No resumes available.")
            return

        resume_options = {f"{item['candidate_name']} - {item['file_name']}": item for item in resumes}
        selected_label = st.selectbox("Select Resume", list(resume_options.keys()))
        selected_resume = resume_options[selected_label]
        c1, c2, c3 = st.columns(3)
        c1.metric("Candidate", selected_resume["candidate_name"])
        c2.metric("Email", selected_resume.get("email") or "Not detected")
        c3.metric("Phone", selected_resume.get("phone") or "Not detected")
        st.caption(f"Uploaded: {selected_resume['uploaded_at']}")
        with st.expander("View Extracted Resume Text"):
            st.text_area("Resume Text", selected_resume["extracted_text"], height=260)
        with open(selected_resume["file_path"], "rb") as resume_file:
            st.download_button("Download Uploaded Resume", resume_file, file_name=selected_resume["file_name"])
        if st.button("Delete Selected Resume", type="secondary"):
            delete_resume(selected_resume["resume_id"])
            st.success("Resume deleted.")
            st.rerun()


def job_description_page() -> None:
    page_header("Job Description", "Save the role description that resumes should be compared against.")
    tab1, tab2, tab3 = st.tabs(["Paste JD", "Upload JD PDF", "Saved JDs"])

    with tab1:
        with st.form("paste_jd_form", clear_on_submit=True):
            title = st.text_input("Job Title", value="Machine Learning Engineer Intern")
            description = st.text_area("Job Description", height=260)
            submitted = st.form_submit_button("Save Job Description", use_container_width=True)
        if submitted:
            try:
                job_id = save_job_description(title, description)
                st.success(f"Job description saved. Job ID: {job_id}")
            except Exception as exc:
                st.error(str(exc))

    with tab2:
        with st.form("upload_jd_form", clear_on_submit=True):
            title = st.text_input("Uploaded JD Title", value="Python AI Developer")
            uploaded_file = st.file_uploader("Job Description PDF", type=["pdf"])
            submitted = st.form_submit_button("Extract and Save", use_container_width=True)
        if submitted:
            try:
                job_id = save_uploaded_job_description(title, uploaded_file)
                st.success(f"Uploaded job description saved. Job ID: {job_id}")
            except Exception as exc:
                st.error(str(exc))

    with tab3:
        jobs = get_all_job_descriptions()
        if jobs:
            st.dataframe(pd.DataFrame(jobs), use_container_width=True, hide_index=True)
        else:
            st.info("No job descriptions saved yet.")


def analysis_page() -> None:
    page_header("Resume Analysis", "Compare one resume with one job description and review the result.")
    resumes = get_all_resumes()
    jobs = get_all_job_descriptions()

    if not resumes or not jobs:
        st.warning("Upload at least one resume and save at least one job description before analysis.")
        return

    resume_options = {f"{item['candidate_name']} - {item['file_name']}": item["resume_id"] for item in resumes}
    job_options = {f"{item['title']} ({item['created_at']})": item["job_id"] for item in jobs}
    col1, col2 = st.columns(2)
    selected_resume = col1.selectbox("Select Candidate Resume", list(resume_options.keys()))
    selected_job = col2.selectbox("Select Job Description", list(job_options.keys()))

    if st.button("Run Screening", use_container_width=True):
        try:
            result = run_analysis(resume_options[selected_resume], job_options[selected_job])
            st.session_state.latest_result = result
            st.success("Analysis completed. Review the score and skill gaps below.")
        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.latest_result
    if not result:
        return

    st.subheader("Screening Result")
    score = result["match_score"]
    pill("Decision Helper", result.get("recommendation", "N/A"), "pill-strong")
    st.progress(min(score / 100, 1.0), text=f"Match Percentage: {score:.2f}%")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Overall Score", f"{score:.2f}%")
    metric_cols[1].metric("Skill Coverage", f"{result.get('skill_coverage', 0):.2f}%")
    metric_cols[2].metric("TF-IDF Similarity", f"{result.get('tfidf_similarity', 0):.2f}%")
    metric_cols[3].metric("Keyword Coverage", f"{result.get('keyword_score', 0):.2f}%")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(score_gauge(score), use_container_width=True)
    with col2:
        st.plotly_chart(score_breakdown_chart(result), use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(
            skills_pie_chart(len(result["matched_skills"]), len(result["missing_skills"])),
            use_container_width=True,
        )
    with col2:
        st.write("**Short Summary**")
        st.info(result["summary"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<span class='success-text'>Matched Skills</span>", unsafe_allow_html=True)
        st.write(", ".join(result["matched_skills"]) or "No matched skills found.")
        st.plotly_chart(skills_bar_chart(result["matched_skills"], "Matched Skills"), use_container_width=True)
    with col2:
        st.markdown("<span class='danger-text'>Missing Skills</span>", unsafe_allow_html=True)
        st.write(", ".join(result["missing_skills"]) or "No major missing skills found.")
        st.plotly_chart(skills_bar_chart(result["missing_skills"], "Missing Skills", "#ef4444"), use_container_width=True)

    st.write("**Skills To Improve**")
    st.write(", ".join(result["recommended_skills"]) or "No recommendations available.")
    st.write("**Keyword Matches**")
    st.write(", ".join(result["keyword_matches"]) or "No keyword matches found.")


def ranking_page() -> None:
    page_header("Candidate Ranking", "Compare all uploaded candidates for one role.")
    jobs = get_all_job_descriptions()
    if not jobs:
        st.warning("Save a job description first.")
        return
    job_options = {f"{item['title']} ({item['created_at']})": item["job_id"] for item in jobs}
    selected_job = st.selectbox("Select Job Description", list(job_options.keys()))
    ranking = rank_candidates(job_options[selected_job])
    if ranking:
        st.plotly_chart(candidate_ranking_chart(ranking), use_container_width=True)
        ranking_df = pd.DataFrame(ranking)
        st.dataframe(
            ranking_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.2f%%"),
                "Skill Coverage": st.column_config.ProgressColumn(
                    "Skill Coverage", min_value=0, max_value=100, format="%.2f%%"
                ),
            },
        )
    else:
        st.info("No candidates available for ranking.")


def reports_page() -> None:
    page_header("Reports", "Create a PDF report for the latest screening result.")
    result = st.session_state.latest_result
    if not result:
        st.info("Run an AI analysis first to generate a downloadable report.")
        return
    st.metric("Latest Analysis Score", f"{result['match_score']:.2f}%", result.get("recommendation", ""))
    st.write(result["summary"])
    if st.button("Generate PDF Report", use_container_width=True):
        report_path = generate_pdf_report(result)
        st.session_state.latest_report = str(report_path)
        st.success(f"Report generated: {report_path.name}")

    latest_report = st.session_state.get("latest_report")
    if latest_report and Path(latest_report).exists():
        with open(latest_report, "rb") as report_file:
            st.download_button(
                "Download Result PDF",
                report_file,
                file_name=Path(latest_report).name,
                mime="application/pdf",
                use_container_width=True,
            )


def project_notes_page() -> None:
    page_header("Project Notes", "A short explanation of how this project is designed.")
    st.subheader("What this project does")
    st.write(
        "This app screens resumes by extracting PDF text, identifying skills, comparing the resume "
        "with a job description, and ranking candidates using a hybrid score."
    )
    st.subheader("How the score is calculated")
    st.write(
        "The final score combines skill coverage, TF-IDF cosine similarity, keyword coverage, and "
        "basic resume completeness. This keeps the logic understandable while still being more useful "
        "than plain keyword counting."
    )
    st.subheader("Current limitations")
    st.write(
        "The app works best with text-based PDFs. Scanned resumes need OCR, which is not included "
        "because the goal is to keep the project fully offline and beginner-friendly."
    )


def main() -> None:
    # initialize_database()
    initialize_session()
    load_css()

    if not st.session_state.authenticated:
        login_page()
        return

    page = sidebar_navigation()
    if page == "Dashboard":
        dashboard_page()
    elif page == "Resume Management":
        resume_management_page()
    elif page == "Job Description":
        job_description_page()
    elif page == "Resume Analysis":
        analysis_page()
    elif page == "Candidate Ranking":
        ranking_page()
    elif page == "Reports":
        reports_page()
    elif page == "Project Notes":
        project_notes_page()


if __name__ == "__main__":
    main()
