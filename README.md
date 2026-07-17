# AI Resume Screening System

This is a final-year B.Tech style project that screens resumes against a job description. It runs completely offline and uses Python, Streamlit, SQLite, NLP, and Scikit-learn.

The goal of this project is simple: upload resumes, add a job description, calculate a match score, show missing skills, rank candidates, and generate a PDF report.

## Why I Built This Project

Manual resume screening takes time, especially when many candidates apply for the same role. This project automates the first-level screening process by combining resume text extraction, NLP preprocessing, skill matching, and machine learning based similarity scoring.

It is not meant to replace a recruiter. It is meant to help shortlist candidates faster.

## Main Features

- Admin login and logout
- Upload resume PDFs
- View extracted resume text
- Delete uploaded resumes
- Paste or upload job descriptions
- Extract skills from resumes and job descriptions
- Match required skills with candidate skills
- Show missing skills and recommended skills
- Calculate resume match percentage
- Rank all candidates for a selected job description
- Show charts for score, skill match, missing skills, and ranking
- Generate downloadable PDF screening reports
- Store all data in SQLite
- Includes sample resumes and sample job description for demo

## Tech Stack

- Python 3.12+
- Streamlit
- Scikit-learn
- Pandas
- NumPy
- spaCy
- NLTK
- pdfplumber
- PyPDF2
- Plotly
- Matplotlib
- ReportLab
- SQLite

## Project Structure

```text
AIResumeScreeningSystem/
├── app.py
├── database/
│   ├── connection.py
│   ├── db_config.py
│   └── init_db.py
├── ml/
│   └── scoring.py
├── models/
│   └── entities.py
├── nlp/
│   ├── preprocessing.py
│   ├── skill_extractor.py
│   └── skills.py
├── services/
│   ├── analysis_service.py
│   ├── auth_service.py
│   ├── job_service.py
│   ├── report_service.py
│   └── resume_service.py
├── utils/
│   ├── charts.py
│   ├── text_extraction.py
│   └── validators.py
├── static/
│   ├── css/
│   └── images/
├── sample_data/
├── uploads/
├── reports/
├── tests/
├── database.db
├── requirements.txt
└── README.md
```

## How The Matching Works

The project does not depend on any paid API or online model. The matching is calculated locally.

The final score uses four parts:

```text
55% Skill Coverage
15% TF-IDF Cosine Similarity
20% Keyword Coverage
10% Resume Completeness
```

This is better than only using keyword counting because it checks both required skills and text similarity.

## Database Tables

The SQLite database contains these tables:

- `Users`
- `Candidates`
- `Resumes`
- `JobDescriptions`
- `Analysis`

The default admin account is created automatically when the app starts.

## Software Requirements

- Python 3.12 or higher
- VS Code
- A browser
- Internet only for installing dependencies the first time

No Django, Flask, FastAPI, React, Angular, Vue, LangChain, OpenAI API, paid API, or cloud service is used.

## Recommended VS Code Extensions

- Python
- Pylance
- SQLite Viewer
- Markdown All in One

## Setup

Open this folder in VS Code:

```text
AIResumeScreeningSystem
```

Create a virtual environment:

```bash
python3.12 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Login details:

```text
Username: admin
Password: admin123
```

## Quick Demo Steps

1. Login with the default admin account.
2. Go to Dashboard.
3. Click `Load Sample Dataset`.
4. Go to Resume Analysis.
5. Select one resume and one job description.
6. Click `Run Screening`.
7. Check the score, matched skills, missing skills, and recommendation.
8. Go to Reports and generate the PDF report.

## Testing

Check syntax:

```bash
python -m compileall .
```

Run tests:

```bash
pytest tests
```

## Common Errors

### Streamlit command not found

Activate the virtual environment and install requirements again:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Resume text is not extracted

Use a text-based PDF. If the PDF is scanned like an image, this project will not read it because OCR is not included.

### spaCy model warning

The project works without downloading the spaCy English model. It falls back to a blank English pipeline. If you want to install the model, run:

```bash
python -m spacy download en_core_web_sm
```

### Reset database

```bash
python database/init_db.py
```

## Good Resume Points For This Project

- Built an offline AI resume screening system using Python, Streamlit, SQLite, NLP, and Scikit-learn.
- Implemented PDF text extraction, skill extraction, TF-IDF vectorization, cosine similarity, and candidate ranking.
- Designed a hybrid scoring system using skill coverage, keyword coverage, text similarity, and resume completeness.
- Created an interactive dashboard with Plotly charts and downloadable PDF reports.
- Organized the project into separate database, service, NLP, ML, utility, and UI modules.

## Limitations

- Scanned image PDFs are not supported because OCR is not included.
- The skill list is rule-based and can be expanded for more job roles.
- The score is useful for first-level screening, not final hiring decisions.

## Future Improvements

- Add OCR for scanned resumes
- Add Excel export for candidate ranking
- Add password change option
- Add role-wise skill templates
- Add more detailed candidate analytics
