def recommend_skills(missing_keywords: list) -> list:
    """
    Receives the list of missing skill keywords from scoring_engine
    and returns human-readable improvement suggestions.
    """
    missing = [k.lower() for k in missing_keywords]
    recs = []

    if "machine learning" in missing:
        recs.append("Add Machine Learning projects or courses")

    if "python" in missing:
        recs.append("Highlight Python skills and projects")

    if "sql" in missing:
        recs.append("Add SQL / database experience")

    if "docker" in missing:
        recs.append("Learn Docker for containerisation")

    if "aws" in missing:
        recs.append("Add cloud experience (AWS / GCP / Azure)")

    if "react" in missing or "javascript" in missing:
        recs.append("Add frontend skills (React / JavaScript)")

    if "flask" in missing or "django" in missing:
        recs.append("Add a Python web framework (Flask / Django)")

    # Generic suggestions always shown
    recs.append("Quantify achievements with numbers (e.g. 'improved speed by 30%')")
    recs.append("Add a Projects section with GitHub links")

    return recs[:6]   # cap at 6 suggestions