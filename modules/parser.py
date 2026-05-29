"""
CV-Craft-Studio - Resume Parser Module
Parses PDF, DOCX, and TXT resumes using pdfplumber, python-docx, and regex.
No external AI APIs required.
"""

import re
import io
from typing import Dict, List, Optional, Tuple

# PDF parsing
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# DOCX parsing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import docx2txt
    DOCX2TXT_AVAILABLE = True
except ImportError:
    DOCX2TXT_AVAILABLE = False


# ─────────────────────────────────────────────
# SECTION HEADING PATTERNS
# ─────────────────────────────────────────────
SECTION_HEADINGS = {
    'summary': [
        'summary', 'professional summary', 'profile', 'objective',
        'career objective', 'about me', 'overview', 'personal statement',
        'executive summary', 'professional profile'
    ],
    'education': [
        'education', 'educational background', 'academic background',
        'qualifications', 'academic qualifications', 'degrees', 'academics'
    ],
    'experience': [
        'experience', 'work experience', 'professional experience',
        'employment history', 'work history', 'career history',
        'employment', 'professional background'
    ],
    'internship': [
        'internship', 'internships', 'internship experience',
        'training', 'industrial training', 'summer training', 'apprenticeship'
    ],
    'projects': [
        'projects', 'project experience', 'academic projects',
        'personal projects', 'key projects', 'notable projects', 'project work'
    ],
    'skills': [
        'skills', 'technical skills', 'core competencies', 'competencies',
        'key skills', 'areas of expertise', 'expertise', 'technologies',
        'tools', 'programming languages', 'software skills'
    ],
    'certifications': [
        'certifications', 'certificates', 'professional certifications',
        'courses', 'online courses', 'training & certifications', 'licenses'
    ],
    'achievements': [
        'achievements', 'accomplishments', 'awards', 'honors', 'recognitions',
        'honors & awards', 'key achievements', 'notable achievements'
    ],
    'publications': [
        'publications', 'research papers', 'papers', 'journals',
        'conference papers', 'research publications', 'articles'
    ],
    'leadership': [
        'leadership', 'positions of responsibility', 'extracurricular activities',
        'activities', 'volunteer', 'volunteering', 'community service',
        'co-curricular', 'extra-curricular'
    ],
    'languages': [
        'languages', 'language skills', 'language proficiency'
    ],
    'references': [
        'references', 'referees'
    ]
}

# Flat lookup: heading text → section key
HEADING_LOOKUP: Dict[str, str] = {}
for section_key, headings in SECTION_HEADINGS.items():
    for h in headings:
        HEADING_LOOKUP[h.lower()] = section_key


# ─────────────────────────────────────────────
# FILE PARSERS
# ─────────────────────────────────────────────

def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber, fallback to PyPDF2."""
    text = ""
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception:
            pass

    if PYPDF2_AVAILABLE:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception:
            pass

    return text


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes."""
    text = ""
    if DOCX_AVAILABLE:
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            text = "\n".join(paragraphs)
            if text.strip():
                return text
        except Exception:
            pass

    if DOCX2TXT_AVAILABLE:
        try:
            text = docx2txt.process(io.BytesIO(file_bytes))
        except Exception:
            pass

    return text


def parse_txt(file_bytes: bytes) -> str:
    """Decode plain text file."""
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            return file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode('utf-8', errors='replace')


def parse_resume_file(file_bytes: bytes, filename: str) -> str:
    """Dispatch parser based on file extension."""
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext == 'pdf':
        return parse_pdf(file_bytes)
    elif ext in ('docx', 'doc'):
        return parse_docx(file_bytes)
    elif ext == 'txt':
        return parse_txt(file_bytes)
    else:
        # Try as plain text
        return parse_txt(file_bytes)


# ─────────────────────────────────────────────
# CONTACT INFORMATION EXTRACTION
# ─────────────────────────────────────────────

def extract_email(text: str) -> str:
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    patterns = [
        r'(?:\+91[\-\s]?)?(?:\(?\d{3,5}\)?[\-\s]?)?\d{3}[\-\s]?\d{4}',
        r'(?:\+1[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',
        r'\+?\d{1,3}[\-\s]?\d{4,5}[\-\s]?\d{4,5}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return ""


def extract_linkedin(text: str) -> str:
    pattern = r'(?:linkedin\.com/in/|linkedin:\s*)([a-zA-Z0-9\-]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return f"linkedin.com/in/{match.group(1)}"
    return ""


def extract_github(text: str) -> str:
    pattern = r'(?:github\.com/)([a-zA-Z0-9\-]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return f"github.com/{match.group(1)}"
    return ""


def extract_name(text: str) -> str:
    """Heuristic: first non-empty line that looks like a name."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:5]:
        # Skip lines that look like contact info
        if re.search(r'[@|\d{5,}|linkedin|github|http]', line, re.IGNORECASE):
            continue
        # Name: 2–4 words, each capitalized, no special chars
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return lines[0] if lines else ""


def extract_contact_info(text: str) -> Dict[str, str]:
    return {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'linkedin': extract_linkedin(text),
        'github': extract_github(text),
    }


# ─────────────────────────────────────────────
# SECTION EXTRACTION
# ─────────────────────────────────────────────

def _is_section_heading(line: str) -> Optional[str]:
    """
    Returns the section key if this line is a recognized section heading, else None.
    Headings are typically: ALL CAPS, or title-case short lines, possibly with colon.
    """
    clean = line.strip().rstrip(':').strip()
    if not clean or len(clean.split()) > 7:
        return None
    normalized = clean.lower()
    if normalized in HEADING_LOOKUP:
        return HEADING_LOOKUP[normalized]
    # Try matching partial (e.g., "WORK EXPERIENCE" → "experience")
    for heading, key in HEADING_LOOKUP.items():
        if normalized == heading:
            return key
    return None


def extract_sections(text: str) -> Dict[str, str]:
    """Split resume text into sections using heading detection."""
    lines = text.split('\n')
    sections: Dict[str, List[str]] = {'_header': []}
    current_section = '_header'

    for line in lines:
        section_key = _is_section_heading(line)
        if section_key:
            current_section = section_key
            if current_section not in sections:
                sections[current_section] = []
        else:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append(line)

    # Join each section's lines
    return {k: '\n'.join(v).strip() for k, v in sections.items()}


# ─────────────────────────────────────────────
# KEYWORD EXTRACTION (TF-IDF based)
# ─────────────────────────────────────────────

STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'shall', 'can', 'i', 'me', 'my',
    'we', 'our', 'you', 'your', 'he', 'she', 'it', 'they', 'their', 'this',
    'that', 'these', 'those', 'as', 'if', 'not', 'no', 'so', 'up', 'out',
    'about', 'than', 'more', 'into', 'also', 'its', 'well', 'one', 'two'
}


def extract_keywords(text: str, top_n: int = 30) -> List[str]:
    """Extract top keywords from text using simple TF scoring + stopword removal."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=200,
            token_pattern=r'[a-zA-Z][a-zA-Z0-9+#.]*[a-zA-Z0-9]'
        )
        tfidf_matrix = vectorizer.fit_transform([text])
        scores = zip(vectorizer.get_feature_names_out(), tfidf_matrix.toarray()[0])
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return [word for word, score in sorted_scores[:top_n] if score > 0]
    except Exception:
        # Fallback: frequency counting
        words = re.findall(r'[a-zA-Z][a-zA-Z0-9+#.]*', text.lower())
        freq: Dict[str, int] = {}
        for w in words:
            if w not in STOPWORDS and len(w) > 2:
                freq[w] = freq.get(w, 0) + 1
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:top_n]]


# ─────────────────────────────────────────────
# FULL RESUME PARSE
# ─────────────────────────────────────────────

def parse_resume(file_bytes: bytes, filename: str) -> Dict:
    """Full pipeline: file → structured resume dict."""
    raw_text = parse_resume_file(file_bytes, filename)
    contact = extract_contact_info(raw_text)
    sections = extract_sections(raw_text)
    keywords = extract_keywords(raw_text)

    return {
        'raw_text': raw_text,
        'contact': contact,
        'sections': sections,
        'keywords': keywords,
        'filename': filename,
        'char_count': len(raw_text),
        'word_count': len(raw_text.split()),
        'line_count': len(raw_text.split('\n')),
    }
