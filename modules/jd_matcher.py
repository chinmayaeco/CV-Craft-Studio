"""
CV-Craft-Studio - Job Description Matcher
Uses TF-IDF cosine similarity + keyword matching. No external APIs.
"""

import re
from typing import Dict, List, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ─────────────────────────────────────────────
# SKILL DICTIONARY
# ─────────────────────────────────────────────

SKILL_DICTIONARY = [
    # Programming
    'python', 'r', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
    'scala', 'kotlin', 'swift', 'php', 'ruby', 'perl', 'matlab', 'julia',
    # Data / Analytics
    'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'sqlite', 'nosql',
    'excel', 'google sheets', 'tableau', 'power bi', 'looker', 'qlikview',
    'sas', 'spss', 'stata', 'r studio', 'jupyter', 'numpy', 'pandas',
    'matplotlib', 'seaborn', 'plotly', 'ggplot',
    # Machine Learning
    'machine learning', 'deep learning', 'nlp', 'natural language processing',
    'computer vision', 'reinforcement learning', 'tensorflow', 'pytorch',
    'keras', 'scikit-learn', 'xgboost', 'lightgbm', 'catboost', 'hugging face',
    'bert', 'gpt', 'random forest', 'neural network',
    # Cloud / DevOps
    'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins',
    'git', 'github', 'gitlab', 'ci/cd', 'terraform', 'ansible', 'linux',
    # Web / Backend
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask',
    'fastapi', 'spring boot', 'rest api', 'graphql', 'microservices',
    # BI / Reporting
    'data visualization', 'dashboard', 'reporting', 'kpi', 'metrics',
    'business intelligence', 'etl', 'data pipeline', 'data warehouse',
    'apache spark', 'hadoop', 'airflow', 'kafka',
    # Business / Management
    'project management', 'agile', 'scrum', 'kanban', 'jira', 'confluence',
    'stakeholder management', 'strategic planning', 'business analysis',
    'requirements gathering', 'process improvement', 'change management',
    'budgeting', 'forecasting', 'financial modeling', 'risk management',
    # Soft skills
    'communication', 'leadership', 'teamwork', 'problem solving',
    'critical thinking', 'presentation', 'collaboration', 'time management',
    'adaptability', 'attention to detail', 'analytical thinking',
    # Research / Academic
    'research', 'statistical analysis', 'hypothesis testing', 'regression',
    'survey design', 'literature review', 'academic writing', 'publications',
]


def normalize_text(text: str) -> str:
    """Lowercase, remove special chars, normalize whitespace."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s+#\./]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_skills_from_text(text: str) -> List[str]:
    """Find skills from the global skill dictionary present in text."""
    text_lower = text.lower()
    found = []
    for skill in SKILL_DICTIONARY:
        # Match whole skill (handles multi-word skills)
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def extract_jd_keywords(jd_text: str, top_n: int = 40) -> List[str]:
    """Extract top keywords from job description."""
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=300,
            token_pattern=r'[a-zA-Z][a-zA-Z0-9+#.]*[a-zA-Z0-9]'
        )
        tfidf = vectorizer.fit_transform([jd_text])
        scores = list(zip(vectorizer.get_feature_names_out(), tfidf.toarray()[0]))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return [w for w, s in sorted_scores[:top_n] if s > 0]
    except Exception:
        words = re.findall(r'[a-zA-Z][a-zA-Z+#.]*', jd_text.lower())
        freq = {}
        stopwords = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'are', 'will', 'be', 'we', 'you', 'your'}
        for w in words:
            if w not in stopwords and len(w) > 2:
                freq[w] = freq.get(w, 0) + 1
        return [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]]


def compute_cosine_similarity(text1: str, text2: str) -> float:
    """TF-IDF cosine similarity between two texts."""
    if not text1.strip() or not text2.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(sim)
    except Exception:
        return 0.0


def match_keywords(resume_text: str, jd_keywords: List[str]) -> Tuple[List[str], List[str]]:
    """Return (matched_keywords, missing_keywords) for a list of JD keywords."""
    resume_lower = resume_text.lower()
    matched = []
    missing = []
    for kw in jd_keywords:
        if re.search(r'\b' + re.escape(kw.lower()) + r'\b', resume_lower):
            matched.append(kw)
        else:
            missing.append(kw)
    return matched, missing


def compute_job_fit_score(cosine_sim: float, keyword_match_ratio: float, skill_match_ratio: float) -> int:
    """Compute overall job-fit score (0–100)."""
    # Weighted combination
    score = (
        cosine_sim * 40 +
        keyword_match_ratio * 35 +
        skill_match_ratio * 25
    )
    return min(100, int(score * 100))


def generate_jd_suggestions(missing_skills: List[str], missing_keywords: List[str]) -> List[str]:
    """Generate honest, rule-based suggestions. Never tells user to fake skills."""
    suggestions = []

    if missing_skills:
        suggestions.append(f"**Skills to Verify**: The following skills appear in the JD but not your resume: {', '.join(missing_skills[:5])}. " +
                           "Only add them if you genuinely have experience with them.")
    if missing_keywords:
        suggestions.append(f"**Keywords to Consider**: Naturally integrate these JD terms if applicable: {', '.join(missing_keywords[:8])}.")

    if missing_skills:
        learn_skills = missing_skills[:3]
        suggestions.append(f"**Learn Before Claiming**: If you lack these skills, consider upskilling: {', '.join(learn_skills)}.")

    suggestions.append("**Resume Tailoring Tip**: Mirror the language of the job description in your experience bullets where truthfully applicable.")
    suggestions.append("**Verify Before Adding**: Do not list skills or tools you haven't used — verify your actual proficiency before claiming them.")

    return suggestions


def match_resume_to_jd(resume_parsed: Dict, jd_text: str) -> Dict:
    """Full job description matching pipeline."""
    resume_text = resume_parsed.get('raw_text', '')

    # Similarity
    cosine_sim = compute_cosine_similarity(resume_text, jd_text)

    # Keyword matching
    jd_keywords = extract_jd_keywords(jd_text)
    matched_kw, missing_kw = match_keywords(resume_text, jd_keywords)
    kw_ratio = len(matched_kw) / max(len(jd_keywords), 1)

    # Skill matching
    resume_skills = extract_skills_from_text(resume_text)
    jd_skills = extract_skills_from_text(jd_text)
    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))
    skill_ratio = len(matched_skills) / max(len(jd_skills), 1)

    # Overall score
    fit_score = compute_job_fit_score(cosine_sim, kw_ratio, skill_ratio)

    suggestions = generate_jd_suggestions(missing_skills, missing_kw)

    return {
        'fit_score': fit_score,
        'cosine_similarity': round(cosine_sim * 100, 1),
        'keyword_match_count': len(matched_kw),
        'keyword_total': len(jd_keywords),
        'keyword_match_pct': round(kw_ratio * 100, 1),
        'matched_keywords': matched_kw[:20],
        'missing_keywords': missing_kw[:20],
        'jd_skills': jd_skills,
        'resume_skills': resume_skills,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'skill_match_pct': round(skill_ratio * 100, 1),
        'suggestions': suggestions,
    }
