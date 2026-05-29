"""
CV-Craft-Studio - ATS Resume Scorer
Transparent rule-based scoring system. No AI APIs.
"""

import re
from typing import Dict, List, Tuple

# ─────────────────────────────────────────────
# ACTION VERBS
# ─────────────────────────────────────────────
ACTION_VERBS = [
    'analyzed', 'designed', 'developed', 'implemented', 'optimized', 'automated',
    'led', 'coordinated', 'evaluated', 'improved', 'built', 'delivered',
    'researched', 'presented', 'managed', 'created', 'established', 'launched',
    'streamlined', 'enhanced', 'reduced', 'increased', 'generated', 'achieved',
    'collaborated', 'facilitated', 'initiated', 'executed', 'deployed', 'integrated',
    'monitored', 'resolved', 'supervised', 'trained', 'mentored', 'spearheaded',
    'conceptualized', 'formulated', 'negotiated', 'identified', 'transformed',
    'accelerated', 'administered', 'advised', 'allocated', 'applied', 'assessed',
    'authored', 'budgeted', 'calculated', 'classified', 'compiled', 'conducted',
    'configured', 'consolidated', 'constructed', 'consulted', 'customized',
    'debugged', 'defined', 'demonstrated', 'directed', 'discovered', 'documented',
    'drove', 'engineered', 'ensured', 'established', 'extracted', 'forecasted',
    'guided', 'handled', 'headed', 'highlighted', 'identified', 'illustrated',
    'influenced', 'informed', 'inspected', 'installed', 'integrated',
    'interpreted', 'introduced', 'investigated', 'maintained', 'measured',
    'migrated', 'modeled', 'modified', 'operated', 'orchestrated', 'organized',
    'planned', 'prepared', 'processed', 'produced', 'programmed', 'proposed',
    'provided', 'published', 'recommended', 'redesigned', 'refined', 'reported',
    'restructured', 'reviewed', 'scheduled', 'secured', 'selected', 'simplified',
    'solved', 'standardized', 'strategized', 'structured', 'supported',
    'synthesized', 'tested', 'tracked', 'updated', 'utilized', 'validated',
    'visualized', 'wrote'
]

WEAK_WORDS = [
    'helped', 'assisted', 'worked on', 'was responsible for', 'tried',
    'attempted', 'participated in', 'involved in', 'handled', 'dealt with',
    'was part of', 'contributed to', 'did', 'made'
]

QUANT_PATTERNS = [
    r'\d+\s*%',
    r'\$\s*\d+',
    r'\d+\s*(million|billion|thousand|k|m|b)',
    r'\d+\s*(users|customers|clients|employees|team members|projects|reports)',
    r'(increased|decreased|reduced|improved|grew|boosted|cut|saved).*\d+',
    r'\d+x\s*(faster|better|more)',
    r'from\s+\d+.*to\s+\d+',
    r'top\s+\d+',
    r'\d+\s*(hours|days|weeks|months)',
    r'\d+\+',
]


# ─────────────────────────────────────────────
# SCORING FUNCTIONS
# ─────────────────────────────────────────────

def score_contact_info(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score contact information (max 10)."""
    score = 0
    strengths = []
    issues = []
    contact = parsed.get('contact', {})

    if contact.get('email'):
        score += 3
        strengths.append('Email address present')
    else:
        issues.append('Missing email address — critical for ATS')

    if contact.get('phone'):
        score += 3
        strengths.append('Phone number present')
    else:
        issues.append('Missing phone number')

    if contact.get('linkedin'):
        score += 2
        strengths.append('LinkedIn profile linked')
    else:
        issues.append('LinkedIn URL missing — add to improve recruiter reach')

    if contact.get('name'):
        score += 2
        strengths.append('Name detected')
    else:
        issues.append('Name not clearly detected at top of resume')

    return min(score, 10), strengths, issues


def score_summary(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score professional summary (max 10)."""
    sections = parsed.get('sections', {})
    summary_text = sections.get('summary', '')
    score = 0
    strengths = []
    issues = []

    if not summary_text or len(summary_text.strip()) < 30:
        issues.append('Professional summary missing or too short')
        return 0, strengths, issues

    score += 5
    strengths.append('Professional summary present')

    word_count = len(summary_text.split())
    if 40 <= word_count <= 100:
        score += 3
        strengths.append('Summary length is appropriate (40–100 words)')
    elif word_count > 100:
        issues.append('Summary is too long — aim for 40–100 words')
        score += 1
    else:
        issues.append('Summary is too brief — expand to 40–100 words')
        score += 1

    # Check for relevant keywords
    lower = summary_text.lower()
    keyword_hits = sum(1 for v in ACTION_VERBS[:20] if v in lower)
    if keyword_hits >= 2:
        score += 2
        strengths.append('Summary uses strong action language')
    else:
        issues.append('Summary lacks strong action verbs')

    return min(score, 10), strengths, issues


def score_education(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score education section (max 10)."""
    sections = parsed.get('sections', {})
    edu_text = sections.get('education', '')
    score = 0
    strengths = []
    issues = []

    if not edu_text or len(edu_text.strip()) < 20:
        issues.append('Education section missing or too brief')
        return 0, strengths, issues

    score += 5
    strengths.append('Education section present')

    # Check for degree keywords
    degree_keywords = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba',
                       'bsc', 'msc', 'b.com', 'm.com', 'be', 'me', 'diploma',
                       'degree', 'graduate', 'postgraduate', 'pgdm', 'bba']
    has_degree = any(kw in edu_text.lower() for kw in degree_keywords)
    if has_degree:
        score += 3
        strengths.append('Degree/qualification mentioned')
    else:
        issues.append('Degree type not clearly mentioned')

    # Check for dates
    date_pattern = r'(20\d\d|19\d\d)'
    if re.search(date_pattern, edu_text):
        score += 2
        strengths.append('Education dates/years present')
    else:
        issues.append('Education years/dates missing')

    return min(score, 10), strengths, issues


def score_skills(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score skills section (max 15)."""
    sections = parsed.get('sections', {})
    skills_text = sections.get('skills', '')
    score = 0
    strengths = []
    issues = []

    if not skills_text or len(skills_text.strip()) < 20:
        issues.append('Skills section missing — this is critical for ATS parsing')
        return 0, strengths, issues

    score += 5
    strengths.append('Skills section present')

    # Count skills (words/phrases separated by commas, bullets, newlines)
    skill_items = re.split(r'[,|\n•·\-]+', skills_text)
    skill_items = [s.strip() for s in skill_items if len(s.strip()) > 1]
    num_skills = len(skill_items)

    if num_skills >= 10:
        score += 5
        strengths.append(f'{num_skills} skills listed — good coverage')
    elif num_skills >= 5:
        score += 3
        strengths.append(f'{num_skills} skills listed — consider adding more')
        issues.append('Add more relevant skills (target 10+)')
    else:
        issues.append(f'Only {num_skills} skills listed — ATS needs more keywords')
        score += 1

    # Check for technical terms
    tech_terms = ['python', 'sql', 'excel', 'java', 'javascript', 'r', 'tableau',
                  'powerbi', 'power bi', 'machine learning', 'deep learning', 'nlp',
                  'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'html',
                  'css', 'react', 'node', 'django', 'flask', 'spark', 'hadoop',
                  'sas', 'spss', 'stata', 'matlab', 'tensorflow', 'pytorch']
    tech_hits = sum(1 for t in tech_terms if t in skills_text.lower())
    if tech_hits >= 3:
        score += 5
        strengths.append(f'{tech_hits} technical tools/technologies mentioned')
    elif tech_hits >= 1:
        score += 2
        issues.append('Include more specific tools and technologies')
    else:
        issues.append('No specific technologies/tools detected in skills')

    return min(score, 15), strengths, issues


def score_experience(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score experience/projects (max 20)."""
    sections = parsed.get('sections', {})
    exp_text = sections.get('experience', '') + '\n' + sections.get('projects', '') + '\n' + sections.get('internship', '')
    score = 0
    strengths = []
    issues = []

    if len(exp_text.strip()) < 50:
        issues.append('No experience, internship, or project content found')
        return 0, strengths, issues

    # Count bullet points
    bullets = re.findall(r'^[•\-*\d+\.)]\s*.+', exp_text, re.MULTILINE)
    if len(bullets) >= 5:
        score += 8
        strengths.append(f'{len(bullets)} bullet points found')
    elif len(bullets) >= 2:
        score += 4
        issues.append('Add more bullet points for each role/project (target 3–5 each)')
    else:
        issues.append('Use bullet points to list accomplishments — not paragraphs')

    # Date presence
    if re.search(r'(20\d\d|19\d\d)', exp_text):
        score += 4
        strengths.append('Work/project dates present')
    else:
        issues.append('Add dates to experience/project entries')

    # Has actual content
    if len(exp_text.split()) > 100:
        score += 4
        strengths.append('Experience section has sufficient detail')
    else:
        issues.append('Expand experience descriptions with more detail')

    # Company/org names (heuristic: capitalized proper nouns)
    org_pattern = r'(?:at|@|for)\s+([A-Z][a-zA-Z0-9\s&,]+)'
    orgs = re.findall(org_pattern, exp_text)
    if orgs:
        score += 4
        strengths.append('Organization names detected in experience')
    else:
        score += 2  # Partial credit

    return min(score, 20), strengths, issues


def score_action_verbs(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score use of action verbs (max 10)."""
    text = parsed.get('raw_text', '').lower()
    score = 0
    strengths = []
    issues = []

    found_verbs = [v for v in ACTION_VERBS if v in text]
    unique_verbs = list(set(found_verbs))

    if len(unique_verbs) >= 8:
        score = 10
        strengths.append(f'{len(unique_verbs)} unique action verbs used')
    elif len(unique_verbs) >= 5:
        score = 7
        strengths.append(f'{len(unique_verbs)} action verbs used')
        issues.append('Use more varied action verbs (target 8+)')
    elif len(unique_verbs) >= 2:
        score = 4
        issues.append(f'Only {len(unique_verbs)} action verbs found — use more')
    else:
        score = 1
        issues.append('Almost no action verbs found — critical issue')

    # Check for weak language
    weak_found = [w for w in WEAK_WORDS if w in text]
    if weak_found:
        issues.append(f'Weak phrasing detected: {", ".join(weak_found[:3])}')

    return min(score, 10), strengths, issues


def score_quantified(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score quantified achievements (max 10)."""
    text = parsed.get('raw_text', '')
    score = 0
    strengths = []
    issues = []

    quant_hits = []
    for pattern in QUANT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        quant_hits.extend(matches)

    unique_hits = len(set(str(h) for h in quant_hits))

    if unique_hits >= 5:
        score = 10
        strengths.append(f'{unique_hits} quantified achievements/metrics found')
    elif unique_hits >= 3:
        score = 7
        strengths.append(f'{unique_hits} quantified metrics found')
        issues.append('Add more measurable results (percentages, numbers, outcomes)')
    elif unique_hits >= 1:
        score = 4
        issues.append('Very few quantified achievements — add metrics where truthful')
    else:
        score = 0
        issues.append('No quantified achievements — add real numbers/percentages where applicable')

    return min(score, 10), strengths, issues


def score_ats_formatting(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score ATS formatting simplicity (max 10)."""
    text = parsed.get('raw_text', '')
    score = 8  # Start high, deduct
    strengths = []
    issues = []

    strengths.append('Standard text content detected (ATS-readable)')

    # Check for overly complex formatting signals
    if len(re.findall(r'[|│]', text)) > 10:
        score -= 2
        issues.append('Possible table or column separator detected — avoid in ATS version')

    if len(re.findall(r'[★☆●○■□►▶]', text)) > 3:
        score -= 2
        issues.append('Special symbols/graphics detected — may confuse ATS parsers')

    # Check for clear section headings
    sections = parsed.get('sections', {})
    detected_sections = [k for k in sections if k != '_header' and sections[k].strip()]
    if len(detected_sections) >= 4:
        score += 2
        strengths.append(f'{len(detected_sections)} distinct sections detected')
    else:
        issues.append('Section headings may not be ATS-friendly — use standard headings')

    return max(0, min(score, 10)), strengths, issues


def score_length_readability(parsed: Dict) -> Tuple[int, List[str], List[str]]:
    """Score resume length and readability (max 5)."""
    text = parsed.get('raw_text', '')
    word_count = len(text.split())
    score = 0
    strengths = []
    issues = []

    if 300 <= word_count <= 700:
        score = 5
        strengths.append(f'Resume length is optimal ({word_count} words)')
    elif 200 <= word_count < 300:
        score = 3
        issues.append(f'Resume is short ({word_count} words) — consider expanding')
    elif 700 < word_count <= 1000:
        score = 3
        issues.append(f'Resume is a bit long ({word_count} words) — consider trimming')
    elif word_count > 1000:
        score = 1
        issues.append(f'Resume is very long ({word_count} words) — aim for 1–2 pages')
    else:
        score = 1
        issues.append(f'Resume is very short ({word_count} words) — add more content')

    return min(score, 5), strengths, issues


# ─────────────────────────────────────────────
# RED FLAG DETECTOR
# ─────────────────────────────────────────────

def detect_red_flags(parsed: Dict) -> List[Dict]:
    """Return list of detected red flags with severity."""
    flags = []
    contact = parsed.get('contact', {})
    sections = parsed.get('sections', {})
    text = parsed.get('raw_text', '')
    word_count = len(text.split())

    # Contact
    if not contact.get('email'):
        flags.append({'flag': 'Missing email', 'severity': 'critical'})
    if not contact.get('phone'):
        flags.append({'flag': 'Missing phone number', 'severity': 'high'})
    if not contact.get('linkedin'):
        flags.append({'flag': 'Missing LinkedIn URL', 'severity': 'medium'})

    # Sections
    if not sections.get('summary'):
        flags.append({'flag': 'No professional summary/objective', 'severity': 'high'})
    if not sections.get('skills'):
        flags.append({'flag': 'No skills section', 'severity': 'critical'})
    if not sections.get('experience') and not sections.get('projects') and not sections.get('internship'):
        flags.append({'flag': 'No experience, internship, or projects', 'severity': 'critical'})
    if not sections.get('education'):
        flags.append({'flag': 'No education section', 'severity': 'high'})

    # Action verbs
    action_verb_count = sum(1 for v in ACTION_VERBS if v in text.lower())
    if action_verb_count < 3:
        flags.append({'flag': 'Insufficient action verbs', 'severity': 'high'})

    # Weak language
    weak_count = sum(1 for w in WEAK_WORDS if w in text.lower())
    if weak_count >= 3:
        flags.append({'flag': f'Passive/weak language detected ({weak_count} instances)', 'severity': 'medium'})

    # No quantified achievements
    quant_hits = sum(1 for p in QUANT_PATTERNS if re.search(p, text, re.IGNORECASE))
    if quant_hits == 0:
        flags.append({'flag': 'No quantified achievements (numbers/percentages)', 'severity': 'high'})

    # Length
    if word_count > 1000:
        flags.append({'flag': f'Resume too long ({word_count} words)', 'severity': 'medium'})
    elif word_count < 150:
        flags.append({'flag': f'Resume too short ({word_count} words)', 'severity': 'high'})

    # Repeated action verbs
    verb_freq = {}
    for v in ACTION_VERBS:
        count = len(re.findall(r'\b' + v + r'\b', text.lower()))
        if count > 3:
            verb_freq[v] = count
    if verb_freq:
        most_repeated = max(verb_freq, key=lambda k: verb_freq[k])
        flags.append({'flag': f'Repeated action verb: "{most_repeated}" used {verb_freq[most_repeated]}x', 'severity': 'low'})

    return flags


# ─────────────────────────────────────────────
# MAIN SCORING FUNCTION
# ─────────────────────────────────────────────

def score_resume(parsed: Dict) -> Dict:
    """
    Run full ATS scoring on a parsed resume.
    Returns a comprehensive scoring report.
    """
    # Run individual scorers
    contact_score, contact_strengths, contact_issues = score_contact_info(parsed)
    summary_score, summary_strengths, summary_issues = score_summary(parsed)
    edu_score, edu_strengths, edu_issues = score_education(parsed)
    skills_score, skills_strengths, skills_issues = score_skills(parsed)
    exp_score, exp_strengths, exp_issues = score_experience(parsed)
    verb_score, verb_strengths, verb_issues = score_action_verbs(parsed)
    quant_score, quant_strengths, quant_issues = score_quantified(parsed)
    format_score, format_strengths, format_issues = score_ats_formatting(parsed)
    length_score, length_strengths, length_issues = score_length_readability(parsed)

    total = (contact_score + summary_score + edu_score + skills_score +
             exp_score + verb_score + quant_score + format_score + length_score)

    all_strengths = (contact_strengths + summary_strengths + edu_strengths +
                     skills_strengths + exp_strengths + verb_strengths +
                     quant_strengths + format_strengths + length_strengths)
    all_issues = (contact_issues + summary_issues + edu_issues + skills_issues +
                  exp_issues + verb_issues + quant_issues + format_issues + length_issues)

    # Classify issues
    critical_fixes = [i for i in all_issues if any(w in i.lower() for w in ['missing', 'no ', 'critical', 'almost no'])]
    quick_wins = [i for i in all_issues if i not in critical_fixes]

    red_flags = detect_red_flags(parsed)

    return {
        'total_score': total,
        'max_score': 100,
        'grade': _get_grade(total),
        'sections': {
            'contact_info': {'score': contact_score, 'max': 10},
            'professional_summary': {'score': summary_score, 'max': 10},
            'education': {'score': edu_score, 'max': 10},
            'skills': {'score': skills_score, 'max': 15},
            'experience_projects': {'score': exp_score, 'max': 20},
            'action_verbs': {'score': verb_score, 'max': 10},
            'quantified_achievements': {'score': quant_score, 'max': 10},
            'ats_formatting': {'score': format_score, 'max': 10},
            'length_readability': {'score': length_score, 'max': 5},
        },
        'strengths': all_strengths,
        'issues': all_issues,
        'critical_fixes': critical_fixes,
        'quick_wins': quick_wins,
        'red_flags': red_flags,
    }


def _get_grade(score: int) -> str:
    if score >= 85:
        return 'A - Excellent'
    elif score >= 70:
        return 'B - Good'
    elif score >= 55:
        return 'C - Average'
    elif score >= 40:
        return 'D - Needs Work'
    else:
        return 'F - Poor'
