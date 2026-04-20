def extract_skills(text):
    skills_db = [
        "python", "java", "c", "c++", "sql",
        "machine learning", "deep learning",
        "data structures", "algorithms",
        "flask", "django", "react",
        "html", "css", "javascript",
        "Node js", "React Native", 
        "flask", "white", "Powershell"
    ]

    text = text.lower()

    found = [skill for skill in skills_db if skill in text]

    return found
