"""
CV-Craft-Studio - Bullet Point Improver
Rule-based bullet improvement. No AI APIs. Never invents facts.
"""

import re
from typing import Dict, List, Tuple

# ─────────────────────────────────────────────
# ACTION VERBS BY DOMAIN
# ─────────────────────────────────────────────

ACTION_VERBS_BY_DOMAIN = {
    'general': [
        'Analyzed', 'Designed', 'Developed', 'Implemented', 'Optimized', 'Automated',
        'Led', 'Coordinated', 'Evaluated', 'Improved', 'Built', 'Delivered',
        'Researched', 'Presented', 'Managed', 'Created', 'Established', 'Launched',
        'Streamlined', 'Enhanced', 'Reduced', 'Increased', 'Generated', 'Achieved',
        'Collaborated', 'Facilitated', 'Initiated', 'Executed', 'Deployed',
    ],
    'data_analytics': [
        'Analyzed', 'Visualized', 'Modeled', 'Forecasted', 'Extracted', 'Processed',
        'Queried', 'Cleaned', 'Transformed', 'Aggregated', 'Integrated', 'Interpreted',
        'Profiled', 'Validated', 'Benchmarked', 'Synthesized', 'Identified',
    ],
    'software': [
        'Developed', 'Engineered', 'Architected', 'Debugged', 'Deployed', 'Configured',
        'Integrated', 'Migrated', 'Refactored', 'Automated', 'Tested', 'Optimized',
        'Built', 'Implemented', 'Programmed', 'Designed', 'Maintained',
    ],
    'management': [
        'Led', 'Managed', 'Supervised', 'Mentored', 'Directed', 'Coordinated',
        'Spearheaded', 'Orchestrated', 'Strategized', 'Planned', 'Delegated',
        'Facilitated', 'Negotiated', 'Influenced', 'Guided', 'Oversaw',
    ],
    'research': [
        'Researched', 'Investigated', 'Analyzed', 'Published', 'Authored', 'Conducted',
        'Designed', 'Evaluated', 'Synthesized', 'Reviewed', 'Documented', 'Explored',
        'Tested', 'Validated', 'Hypothesized', 'Presented', 'Discovered',
    ],
    'finance': [
        'Analyzed', 'Forecasted', 'Budgeted', 'Audited', 'Modeled', 'Calculated',
        'Evaluated', 'Monitored', 'Optimized', 'Reconciled', 'Reported', 'Assessed',
        'Projected', 'Advised', 'Structured', 'Managed',
    ],
    'marketing': [
        'Launched', 'Developed', 'Executed', 'Drove', 'Grew', 'Managed', 'Created',
        'Designed', 'Campaigned', 'Generated', 'Increased', 'Targeted', 'Segmented',
        'Optimized', 'Presented', 'Tracked', 'Reported',
    ],
}

# Passive/weak patterns
WEAK_PATTERNS = [
    (r'^\s*helped\s+', 'weak_verb'),
    (r'^\s*assisted\s+', 'weak_verb'),
    (r'^\s*worked\s+on\s+', 'weak_verb'),
    (r'^\s*was\s+responsible\s+for\s+', 'passive'),
    (r'^\s*responsible\s+for\s+', 'passive'),
    (r'^\s*tried\s+to\s+', 'tentative'),
    (r'^\s*participated\s+in\s+', 'weak_verb'),
    (r'^\s*involved\s+in\s+', 'weak_verb'),
    (r'^\s*did\s+', 'weak_verb'),
    (r'^\s*made\s+', 'weak_verb'),
    (r'^\s*contributed\s+to\s+', 'weak_verb'),
    (r'^\s*was\s+part\s+of\s+', 'passive'),
    (r'^\s*took\s+part\s+in\s+', 'weak_verb'),
]

# Strong action verb patterns
STRONG_VERB_PATTERN = re.compile(
    r'^\s*(Analyzed|Designed|Developed|Implemented|Optimized|Automated|Led|'
    r'Coordinated|Evaluated|Improved|Built|Delivered|Researched|Presented|'
    r'Managed|Created|Established|Launched|Streamlined|Enhanced|Reduced|'
    r'Increased|Generated|Achieved|Collaborated|Facilitated|Initiated|'
    r'Executed|Deployed|Integrated|Monitored|Resolved|Supervised|Trained|'
    r'Mentored|Spearheaded|Formulated|Negotiated|Identified|Transformed|'
    r'Engineered|Architected|Forecasted|Budgeted|Audited|Modeled|Published)',
    re.IGNORECASE
)

# Improvement templates
IMPROVEMENT_TEMPLATES = [
    {
        'pattern': r'(?:worked on|helped with|assisted with)?\s*(.+?)\s*(?:data|dataset|database)',
        'template': 'Analyzed {subject} data using [tool/method] to identify [pattern/insight], supporting [business decision/outcome].',
        'category': 'data_work'
    },
    {
        'pattern': r'(?:worked on|built|created|developed)\s*(.+?)\s*(?:report|dashboard|visualization)',
        'template': 'Developed [interactive/automated] {subject} dashboard/report using [tool], enabling [stakeholder group] to [decision made].',
        'category': 'reporting'
    },
    {
        'pattern': r'(?:helped|assisted|supported)\s*(.+?)\s*(?:team|project|initiative)',
        'template': 'Collaborated with {subject} team to [specific contribution], resulting in [outcome/impact].',
        'category': 'collaboration'
    },
    {
        'pattern': r'(?:managed|handled|led)\s*(.+?)\s*(?:team|people|employees|members)',
        'template': 'Led {subject} team of [N] members to [achieve specific goal], delivering [outcome] within [timeframe].',
        'category': 'leadership'
    },
    {
        'pattern': r'(?:wrote|created|developed)\s*(.+?)\s*(?:code|program|script|application)',
        'template': 'Developed {subject} [application/script/tool] using [technology], reducing [process/time] by [insert real percentage].',
        'category': 'development'
    },
    {
        'pattern': r'(?:analyzed|studied|reviewed)\s*(.+)',
        'template': 'Analyzed {subject} to identify [key findings/trends], providing actionable insights for [decision/team].',
        'category': 'analysis'
    },
]

METRIC_PLACEHOLDERS = [
    '[insert real percentage improvement]',
    '[insert number of records/items processed]',
    '[insert time saved per week/month]',
    '[insert revenue/cost impact if known]',
    '[insert team size]',
    '[insert number of stakeholders/users]',
]


# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────

def analyze_bullet(bullet: str) -> Dict:
    """Analyze a bullet point for quality issues."""
    result = {
        'original': bullet,
        'issues': [],
        'suggestions': [],
        'has_weak_verb': False,
        'has_passive': False,
        'has_metrics': False,
        'is_vague': False,
        'is_too_long': False,
        'starts_with_action_verb': False,
        'score': 0
    }

    # Length check
    word_count = len(bullet.split())
    if word_count > 35:
        result['is_too_long'] = True
        result['issues'].append(f'Too long ({word_count} words) — aim for 15–25 words')
    elif word_count < 5:
        result['issues'].append('Too short — add more detail')

    # Weak verb check
    for pattern, ptype in WEAK_PATTERNS:
        if re.search(pattern, bullet, re.IGNORECASE):
            result['has_weak_verb'] = True if ptype == 'weak_verb' else result['has_weak_verb']
            result['has_passive'] = True if ptype == 'passive' else result['has_passive']
            if ptype == 'weak_verb':
                result['issues'].append('Starts with a weak verb — use a strong action verb')
            elif ptype == 'passive':
                result['issues'].append('Passive/vague phrasing — rewrite in active voice')
            elif ptype == 'tentative':
                result['issues'].append('Tentative language — be assertive about what you did')
            break

    # Strong verb check
    if STRONG_VERB_PATTERN.match(bullet):
        result['starts_with_action_verb'] = True
        result['score'] += 30
    else:
        result['suggestions'].append('Start with a strong action verb (e.g., Analyzed, Developed, Led)')

    # Metrics check
    metric_patterns = [
        r'\d+\s*%', r'\$\s*\d+', r'\d+x', r'\d+\s*(users|customers|records|projects)',
        r'(increased|decreased|reduced|improved|grew).*\d+',
        r'\d+\s*(hours|days|weeks|months)',
    ]
    for mp in metric_patterns:
        if re.search(mp, bullet, re.IGNORECASE):
            result['has_metrics'] = True
            result['score'] += 30
            break

    if not result['has_metrics']:
        result['issues'].append('No measurable impact — add numbers/percentages if truthfully available')
        result['suggestions'].append('Add a metric: ' + METRIC_PLACEHOLDERS[0])

    # Vagueness check
    vague_words = ['various', 'several', 'many', 'some', 'things', 'stuff',
                   'good', 'great', 'excellent', 'various tasks', 'etc.']
    vague_found = [w for w in vague_words if w in bullet.lower()]
    if vague_found:
        result['is_vague'] = True
        result['issues'].append(f'Vague language detected: "{vague_found[0]}" — be specific')

    # Score
    if result['starts_with_action_verb']:
        result['score'] += 20
    if not result['has_weak_verb'] and not result['has_passive']:
        result['score'] += 20
    if not result['is_vague']:
        result['score'] += 10
    if not result['is_too_long']:
        result['score'] += 10
    if result['has_metrics']:
        result['score'] += 10

    result['score'] = min(100, result['score'])
    return result


def _clean_subject(subject: str) -> str:
    """Return a concise, readable subject phrase for template-based bullets."""
    subject = re.sub(r'^[\s:;,.\-]+|[\s:;,.\-]+$', '', subject or '')
    subject = re.sub(r'\b(data|dataset|database|report|dashboard|visualization|team|project|initiative|code|program|script|application)\b\s*$', '', subject, flags=re.IGNORECASE).strip()
    subject = re.sub(r'\s+', ' ', subject)
    return subject or 'relevant work'


def _strip_weak_opening(bullet: str) -> str:
    """Remove a weak/passive opening without damaging a drafted template."""
    cleaned = bullet.strip()
    for pattern, _ in WEAK_PATTERNS:
        updated = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()
        if updated != cleaned and updated:
            return updated
    return cleaned


def _choose_action_verb(text: str) -> str:
    lower = text.lower()
    if any(term in lower for term in ['data', 'analysis', 'analytics', 'dashboard', 'report', 'excel', 'sql', 'power bi', 'tableau']):
        return 'Analyzed'
    if any(term in lower for term in ['team', 'stakeholder', 'project', 'initiative']):
        return 'Coordinated'
    if any(term in lower for term in ['code', 'script', 'app', 'application', 'model', 'tool']):
        return 'Developed'
    if any(term in lower for term in ['research', 'literature', 'study', 'survey']):
        return 'Researched'
    return 'Improved'


def improve_bullet(bullet: str) -> Dict:
    """Generate an improved bullet using honest, rule-based templates.

    The function deliberately avoids inventing metrics. When a measurable outcome is
    missing, it uses an explicit placeholder that the user must replace only if true.
    """
    analysis = analyze_bullet(bullet)
    original = bullet.strip().lstrip('•-* ').strip()
    improved = original
    reasoning = []

    # Prefer domain-specific templates when a pattern is detected.
    for tmpl in IMPROVEMENT_TEMPLATES:
        match = re.search(tmpl['pattern'], original, re.IGNORECASE)
        if match:
            subject = _clean_subject(match.group(1) if match.lastindex else 'relevant work')
            improved = tmpl['template'].replace('{subject}', subject)
            reasoning.append(f'Applied {tmpl["category"]} improvement template')
            break

    # If no template matched, remove weak opening and rebuild the sentence.
    if improved == original:
        core = _strip_weak_opening(original).rstrip(' .;:')
        if not STRONG_VERB_PATTERN.match(core):
            verb = _choose_action_verb(core)
            core_lower = core.lower()
            if core_lower.startswith(('managing ', 'handling ', 'coordinating ')):
                core = core.split(' ', 1)[1].strip()
                improved = f'Coordinated {core} to [specific contribution], achieving [insert measurable outcome if true]'
            elif verb == 'Researched' and 'research' in core_lower:
                improved = f'Conducted {core} to identify [key findings], supporting [decision/team]'
            else:
                improved = f'{verb} {core[0].lower() + core[1:] if core else "assigned work"}'
            reasoning.append('Replaced weak/passive opening with a stronger action verb')

    # Ensure first character is capitalized.
    if improved and not improved[0].isupper():
        improved = improved[0].upper() + improved[1:]

    # Add measurable-outcome placeholder only when the original bullet has no metrics
    # and the generated template has not already included one.
    if not analysis['has_metrics'] and '[' not in improved:
        improved = improved.rstrip('.') + ', achieving [insert measurable outcome if true].'
        reasoning.append('Added a truthful-metric placeholder instead of inventing impact')

    # Remove awkward duplicate openings introduced by naive rewriting.
    improved = re.sub(r'^(Developed|Improved|Analyzed)\s+\1\b', r'\1', improved, flags=re.IGNORECASE)
    improved = re.sub(r'\s+', ' ', improved).strip()

    if not improved.endswith('.'):
        improved += '.'

    if not STRONG_VERB_PATTERN.match(improved):
        reasoning.append('Review the opening verb and consider a stronger action verb')

    return {
        'original': bullet,
        'improved': improved,
        'analysis': analysis,
        'reasoning': reasoning if reasoning else ['Improved structure while preserving truthful content'],
        'action_verbs': ACTION_VERBS_BY_DOMAIN['general'][:10],
        'is_placeholder_present': '[' in improved,
        'note': 'Replace bracketed placeholders only with real, verifiable facts.'
    }

def improve_multiple_bullets(bullets: List[str]) -> List[Dict]:
    """Improve a list of bullet points."""
    return [improve_bullet(b) for b in bullets if b.strip()]
