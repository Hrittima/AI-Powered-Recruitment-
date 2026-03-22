def recommend_skills(text):
    text = text.lower()

    recs = []

    if "machine learning" not in text:
        recs.append("Add Machine Learning projects")

    if "project" not in text:
        recs.append("Add Projects section")

    if "intern" not in text:
        recs.append("Add Internship/Experience")

    if "python" not in text:
        recs.append("Add Python skills")

    return recs