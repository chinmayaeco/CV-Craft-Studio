"""
CV-Craft-Studio - Grammar Checker (Rule-Based)
Checks common resume grammar mistakes without any API or paid service.
"""

import re
from typing import List, Dict


# ─────────────────────────────────────────────────────────────────────────────
# RULE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

GRAMMAR_RULES = [
    {
        'id': 'first_person_pronoun',
        'name': 'First-Person Pronouns',
        'pattern': r'\b(I |I\'m |I\'ve |I\'d |I\'ll |my |me |myself |we |our |us )\b',
        'message': 'Avoid first-person pronouns in resumes. Rewrite as action verb + result.',
        'example': 'Instead of "I managed a team", write "Managed a cross-functional team of 8"',
        'severity': 'high',
        'flag': True,
    },
    {
        'id': 'passive_voice_weak',
        'name': 'Passive Voice',
        'pattern': r'\b(was responsible for|were responsible for|was involved in|was part of|was tasked with|was assigned to)\b',
        'message': 'Passive voice detected. Use active action verbs instead.',
        'example': 'Instead of "was responsible for data analysis", write "Analyzed datasets to..."',
        'severity': 'high',
        'flag': True,
    },
    {
        'id': 'vague_words',
        'name': 'Vague Filler Words',
        'pattern': r'\b(various|several|many|some|a lot of|lots of|numerous|etc|things|stuff|good|great|excellent|best|amazing|outstanding)\b',
        'message': 'Vague word detected. Be specific with numbers and details.',
        'example': 'Instead of "managed various projects", write "Managed 6 concurrent projects"',
        'severity': 'medium',
        'flag': True,
    },
    {
        'id': 'tense_consistency_past',
        'name': 'Present Tense in Past Roles',
        'pattern': r'\b(manage|lead|develop|create|build|design|coordinate|implement|analyze|report|present)s?\b',
        'message': 'Possible tense issue: use past tense for previous roles (e.g., "managed", "led").',
        'example': 'Use past tense for roles you no longer hold.',
        'severity': 'low',
        'flag': False,  # Only flagged contextually
    },
    {
        'id': 'redundant_phrases',
        'name': 'Redundant Phrases',
        'pattern': r'\b(team player|hard worker|detail oriented|go getter|self starter|results driven|fast learner|quick learner|passionate about|love to|enjoy working)\b',
        'message': 'Overused resume cliché detected. Replace with specific, quantified achievements.',
        'example': 'Instead of "team player", describe collaboration: "Led 5-person cross-functional team..."',
        'severity': 'medium',
        'flag': True,
    },
    {
        'id': 'article_mistakes',
        'name': 'Article Usage',
        'pattern': r'\b(a [aeiouAEIOU])\b',
        'message': 'Possible article error: use "an" before vowel sounds.',
        'example': '"a analytics" → "an analytics"; "a MBA" → "an MBA"',
        'severity': 'low',
        'flag': True,
    },
    {
        'id': 'double_spaces',
        'name': 'Double Spaces',
        'pattern': r'  +',
        'message': 'Multiple consecutive spaces found.',
        'example': 'Remove extra spaces between words.',
        'severity': 'low',
        'flag': True,
    },
    {
        'id': 'missing_period_bullet',
        'name': 'Inconsistent Punctuation',
        'pattern': r'[a-z]\n[A-Z]',
        'message': 'Inconsistent line endings detected in bullet points.',
        'example': 'Either end all bullets with a period or none — be consistent.',
        'severity': 'low',
        'flag': True,
    },
    {
        'id': 'numbers_in_words',
        'name': 'Spell Out Small Numbers',
        'pattern': r'\b(one |two |three |four |five |six |seven |eight |nine |ten ) (team|member|project|year|month|week)s?\b',
        'message': 'Consider using numerals for impact: "5 team members" reads stronger than "five team members".',
        'example': '"Led five team members" → "Led 5 team members"',
        'severity': 'low',
        'flag': True,
    },
]


def check_grammar(text: str) -> List[Dict]:
    """
    Run all grammar rules on text.
    Returns a list of issues found.
    """
    if not text.strip():
        return []

    issues = []
    text_lower = text.lower()

    for rule in GRAMMAR_RULES:
        if not rule.get('flag', True):
            continue
        try:
            pattern = re.compile(rule['pattern'], re.IGNORECASE)
            matches = list(pattern.finditer(text))
            for match in matches:
                start = match.start()
                end = match.end()
                # Context window
                ctx_start = max(0, start - 35)
                ctx_end = min(len(text), end + 35)
                context = text[ctx_start:ctx_end].replace('\n', ' ').strip()

                issues.append({
                    'rule_id': rule['id'],
                    'rule_name': rule['name'],
                    'matched_text': match.group(0).strip(),
                    'message': rule['message'],
                    'example': rule['example'],
                    'severity': rule['severity'],
                    'context': f'...{context}...',
                    'position': start,
                })
        except Exception:
            continue

    # Deduplicate by rule_id + matched_text
    seen = set()
    unique_issues = []
    for issue in issues:
        key = (issue['rule_id'], issue['matched_text'].lower())
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    return sorted(unique_issues, key=lambda x: ['high', 'medium', 'low'].index(x['severity']))


def check_grammar_in_sections(sections: Dict[str, str]) -> Dict[str, List[Dict]]:
    """Check grammar in each resume section."""
    results = {}
    for section, text in sections.items():
        if section == '_header' or not text.strip():
            continue
        issues = check_grammar(text)
        if issues:
            results[section] = issues
    return results


def get_grammar_score(text: str) -> Dict:
    """
    Return a grammar quality score for the resume text.
    Max 100 points. Deducts based on issue severity.
    """
    issues = check_grammar(text)
    deductions = 0
    for issue in issues:
        if issue['severity'] == 'high':
            deductions += 8
        elif issue['severity'] == 'medium':
            deductions += 4
        else:
            deductions += 2

    score = max(0, min(100, 100 - deductions))
    high_count = len([i for i in issues if i['severity'] == 'high'])
    med_count  = len([i for i in issues if i['severity'] == 'medium'])
    low_count  = len([i for i in issues if i['severity'] == 'low'])

    return {
        'score': score,
        'total_issues': len(issues),
        'high': high_count,
        'medium': med_count,
        'low': low_count,
        'issues': issues,
        'grade': 'A' if score >= 90 else 'B' if score >= 75 else 'C' if score >= 60 else 'D',
        'summary': (
            'No significant grammar issues found!' if not issues else
            f'{len(issues)} issue(s) detected: {high_count} critical, {med_count} medium, {low_count} minor.'
        )
    }


ROLE_SPECIFIC_TIPS = {
    'Data Analyst': [
        'Use precise metrics: "analyzed 2M+ records" not "analyzed large datasets"',
        'Mention specific tools: "Power BI dashboard" not just "dashboard"',
        'Quantify business impact: "reduced reporting time by 40%"',
    ],
    'Business Analyst': [
        'Mention stakeholder count: "presented to 25 stakeholders"',
        'Use process-improvement framing: "streamlined X, resulting in Y"',
        'Reference methodologies: Agile, Scrum, Six Sigma',
    ],
    'Software Engineer': [
        'Specify scale: "serves 100K+ daily users"',
        'Mention latency/performance: "reduced API response time by 60ms"',
        'Use version numbers for languages/frameworks where relevant',
    ],
    'HR': [
        'Quantify hires: "recruited and onboarded 45 employees in Q3"',
        'Mention cost savings: "reduced cost-per-hire by 18%"',
        'Reference frameworks: Competency-based, HRBP, OKRs',
    ],
}


def get_role_writing_tips(role: str) -> List[str]:
    """Get role-specific writing tips."""
    # Try exact match
    if role in ROLE_SPECIFIC_TIPS:
        return ROLE_SPECIFIC_TIPS[role]
    # Fuzzy match
    for key in ROLE_SPECIFIC_TIPS:
        if key.lower() in role.lower() or role.lower() in key.lower():
            return ROLE_SPECIFIC_TIPS[key]
    return [
        'Use strong action verbs at the start of each bullet point.',
        'Quantify achievements wherever possible.',
        'Keep bullet points to 1-2 lines each.',
        'Tailor your resume keywords to each specific job description.',
    ]
