import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def score_gauge(score: float):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#1d4ed8"},
                "steps": [
                    {"range": [0, 40], "color": "#fee2e2"},
                    {"range": [40, 70], "color": "#fef3c7"},
                    {"range": [70, 100], "color": "#dcfce7"},
                ],
            },
            title={"text": "Resume Match Score"},
        )
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="white")
    return fig


def skills_pie_chart(matched_count: int, missing_count: int):
    data = pd.DataFrame(
        {"Category": ["Matched Skills", "Missing Skills"], "Count": [matched_count, missing_count]}
    )
    fig = px.pie(
        data,
        names="Category",
        values="Count",
        hole=0.45,
        color_discrete_sequence=["#2563eb", "#ef4444"],
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=35, b=20), paper_bgcolor="white")
    return fig


def skills_bar_chart(skills: list[str], title: str, color: str = "#2563eb"):
    display_skills = skills[:12] if skills else ["No data"]
    data = pd.DataFrame({"Skill": display_skills, "Count": [1] * len(display_skills)})
    fig = px.bar(data, x="Count", y="Skill", orientation="h", title=title, color_discrete_sequence=[color])
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=20), showlegend=False, paper_bgcolor="white")
    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(title=None, autorange="reversed")
    return fig


def score_breakdown_chart(result: dict):
    data = pd.DataFrame(
        {
            "Metric": ["Skill Coverage", "TF-IDF Similarity", "Keyword Coverage", "Resume Completeness"],
            "Score": [
                result.get("skill_coverage", 0),
                result.get("tfidf_similarity", 0),
                result.get("keyword_score", 0),
                result.get("profile_strength", 0),
            ],
        }
    )
    fig = px.bar(data, x="Metric", y="Score", text="Score", color="Score", color_continuous_scale="Blues")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        height=340,
        yaxis_range=[0, 110],
        margin=dict(l=20, r=20, t=35, b=20),
        paper_bgcolor="white",
        showlegend=False,
    )
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Score (%)")
    return fig


def candidate_ranking_chart(ranking_data: list[dict]):
    if not ranking_data:
        ranking_data = [{"Candidate": "No candidates", "Score": 0}]
    data = pd.DataFrame(ranking_data)
    fig = px.bar(
        data,
        x="Score",
        y="Candidate",
        orientation="h",
        title="Candidate Ranking",
        color="Score",
        color_continuous_scale="Blues",
    )
    fig.update_layout(height=420, xaxis_range=[0, 100], margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="white")
    fig.update_yaxes(autorange="reversed")
    return fig
