import re

def score_resume(text):
    text = text.lower()

    score = 0
    matched = []
    missing = []

    skills = [
        "python", "java", "c++", "javascript",
        "react", "node", "flask", "django",
        "sql", "mongodb", "docker", "aws"
    ]

    for skill in skills:
        if skill in text:
            score += 3
            matched.append(skill)
        else:
            missing.append(skill)

    ai_keywords = [
        "machine learning", "deep learning",
        "nlp", "tensorflow", "pytorch"
    ]

    for word in ai_keywords:
        if word in text:
            score += 6
            matched.append(word)

    if "project" in text:
        score += 10

    if "intern" in text or "experience" in text:
        score += 10

    if "achieved" in text or "improved" in text:
        score += 8

    numbers = re.findall(r'\d+', text)
    score += min(len(numbers) * 2, 10)

    if len(text.split()) > 300:
        score += 10

    score = min(score, 100)

    return score, matched, missing