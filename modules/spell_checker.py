"""
CV-Craft-Studio - Spell Checker
Pure Python spell checking using pyspellchecker. No paid API.
"""

from typing import List, Dict, Tuple
import re

try:
    from spellchecker import SpellChecker
    SPELL_AVAILABLE = True
except ImportError:
    SPELL_AVAILABLE = False

# Domain-specific resume words that spellchecker may flag incorrectly
RESUME_WHITELIST = {
    # Tech
    'python', 'sql', 'mysql', 'postgresql', 'mongodb', 'nosql',
    'javascript', 'typescript', 'nodejs', 'reactjs', 'vuejs', 'angularjs',
    'tableau', 'powerbi', 'looker', 'databricks', 'snowflake', 'hadoop',
    'pyspark', 'sklearn', 'tensorflow', 'pytorch', 'keras', 'pandas',
    'numpy', 'matplotlib', 'seaborn', 'plotly', 'jupyter', 'airflow',
    'kubernetes', 'docker', 'jenkins', 'github', 'gitlab', 'bitbucket',
    'aws', 'gcp', 'azure', 'redshift', 'bigquery', 'elasticsearch',
    'fastapi', 'flask', 'django', 'springboot', 'microservices',
    'restful', 'graphql', 'devops', 'ci', 'cd', 'mlops', 'nlp',
    'lstm', 'bert', 'gpt', 'llm', 'rag', 'langchain', 'huggingface',
    'opencv', 'streamlit', 'gradio', 'metabase', 'superset',
    # Business
    'kpi', 'kpis', 'roi', 'cagr', 'ebitda', 'p&l', 'b2b', 'b2c',
    'saas', 'paas', 'iaas', 'crm', 'erp', 'hrms', 'lms',
    'agile', 'scrum', 'kanban', 'jira', 'confluence', 'trello',
    'stakeholder', 'stakeholders', 'roadmap', 'okrs', 'okr',
    # Degrees
    'btech', 'mtech', 'bcom', 'mcom', 'mba', 'phd', 'bsc', 'msc',
    'pgdm', 'pgdba', 'iit', 'iim', 'nit', 'bits', 'iisc',
    # Names / Companies
    'infosys', 'wipro', 'tcs', 'hcl', 'accenture', 'deloitte',
    'flipkart', 'amazon', 'google', 'microsoft', 'linkedin',
    # Other
    'spearheaded', 'streamlined', 'mentored', 'onboarded',
    'upskilled', 'upskilling', 'reskilling', 'gamification',
    'multivariate', 'multicollinearity', 'heteroscedasticity',
}


def check_spelling(text: str, language: str = 'en') -> List[Dict]:
    """
    Check spelling in the given text.
    Returns a list of dicts with: word, suggestions, context, position.
    """
    if not SPELL_AVAILABLE:
        return [{'error': 'pyspellchecker not installed. Run: pip install pyspellchecker',
                 'word': '', 'suggestions': [], 'context': ''}]

    try:
        spell = SpellChecker(language='en')
        # Add resume-specific whitelist words
        spell.word_frequency.load_words(list(RESUME_WHITELIST))

        # Extract words while preserving position context
        word_pattern = re.compile(r"\b[a-zA-Z']+\b")
        words = word_pattern.findall(text)
        positions = [(m.start(), m.end()) for m in word_pattern.finditer(text)]

        # Filter: only real words (skip acronyms, proper nouns from whitelist)
        misspelled = spell.unknown([w for w in words
                                    if len(w) > 2
                                    and w.lower() not in RESUME_WHITELIST
                                    and not w.isupper()  # skip acronyms
                                    and not w[0].isupper()  # skip proper nouns
                                    ])

        results = []
        seen = set()
        for i, (word, (start, end)) in enumerate(zip(words, positions)):
            if word.lower() in misspelled and word.lower() not in seen:
                seen.add(word.lower())
                # Get context (50 chars before and after)
                ctx_start = max(0, start - 40)
                ctx_end = min(len(text), end + 40)
                context = text[ctx_start:ctx_end].replace('\n', ' ').strip()

                suggestions = list(spell.candidates(word) or set())
                suggestions = [s for s in suggestions if s != word.lower()][:5]

                results.append({
                    'word': word,
                    'suggestions': suggestions,
                    'context': f'...{context}...',
                    'position': start,
                })
        return results
    except Exception as e:
        return [{'error': str(e), 'word': '', 'suggestions': [], 'context': ''}]


def check_spelling_in_sections(sections: Dict[str, str]) -> Dict[str, List[Dict]]:
    """Check spelling in each resume section independently."""
    results = {}
    for section, text in sections.items():
        if section == '_header' or not text.strip():
            continue
        errors = check_spelling(text)
        if errors and not errors[0].get('error'):
            results[section] = errors
    return results


def get_spell_check_summary(errors: Dict[str, List[Dict]]) -> Dict:
    """Summarise spell check results."""
    total = sum(len(v) for v in errors.values())
    sections_affected = len(errors)
    return {
        'total_errors': total,
        'sections_affected': sections_affected,
        'is_clean': total == 0,
        'grade': 'A' if total == 0 else 'B' if total <= 2 else 'C' if total <= 5 else 'D',
    }


def is_available() -> bool:
    return SPELL_AVAILABLE
