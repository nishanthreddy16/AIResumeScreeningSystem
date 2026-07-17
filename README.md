# AI Resume Screening System

## Developed By

**Dasari Nishanth Reddy**  
B.Tech – Computer Science and Engineering (Data Science)  
Lovely Professional University (LPU)

---

## Project Overview

AI Resume Screening System is a resume analysis and candidate ranking application developed as a final-year academic project. The system helps recruiters compare resumes with job descriptions by extracting resume content, identifying technical skills, calculating similarity scores, and ranking candidates based on their suitability for a job role.

The project is designed to reduce the time required for manual resume screening while providing a simple and user-friendly interface.

---

## Objectives

- Automate resume screening.
- Compare resumes with job descriptions.
- Identify matching and missing skills.
- Rank candidates based on AI-driven scoring.
- Generate downloadable PDF reports.

---

## Key Features

- Secure Admin Login
- Resume PDF Upload
- Resume Text Extraction
- Job Description Upload or Manual Entry
- AI-Based Resume Analysis
- Skill Matching
- Missing Skill Identification
- Resume Match Percentage
- Candidate Ranking
- Interactive Charts and Dashboard
- PDF Report Generation
- SQLite Database Storage
- Sample Dataset for Demonstration

---

## Technologies Used

- Python
- Streamlit
- SQLite
- Scikit-learn
- Pandas
- NumPy
- spaCy
- NLTK
- Plotly
- Matplotlib
- ReportLab
- pdfplumber
- PyPDF2

---

## Project Structure

```
AIResumeScreeningSystem/
│── app.py
│── database/
│── ml/
│── models/
│── nlp/
│── reports/
│── sample_data/
│── services/
│── static/
│── uploads/
│── utils/
│── requirements.txt
│── README.md
```

---

## How to Run

```bash
git clone https://github.com/nishanthreddy16/AIResumeScreeningSystem.git

cd AIResumeScreeningSystem

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

streamlit run app.py
```

---

## Future Improvements

- OCR support for scanned resumes
- AI-powered interview question generation
- Multi-user authentication
- Cloud database integration
- Email notification system
- Recruiter analytics dashboard

---

## Author

**Dasari Nishanth Reddy**

Final Year B.Tech Student  
Computer Science and Engineering (Data Science)  
Lovely Professional University

GitHub: https://github.com/nishanthreddy16

---

## License

This project is developed for academic and learning purposes.

© 2026 Dasari Nishanth Reddy. All Rights Reserved.
