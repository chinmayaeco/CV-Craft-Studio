"""
CV-Craft-Studio - Resume Templates
HTML template rendering for preview. 5 built-in templates.
"""

from typing import Dict, List


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATES = {
    'ats_classic': {
        'name': '1. ATS Classic (Single Column)',
        'description': 'Clean, ATS-optimized single-column layout. Best for corporate/tech roles.',
        'best_for': 'Corporate, Tech, Finance, Consulting',
        'ats_score': 'Excellent',
    },
    'fresher': {
        'name': '2. Fresher / Student',
        'description': 'Project-focused layout for students and recent graduates.',
        'best_for': 'Students, Freshers, Entry-level',
        'ats_score': 'Very Good',
    },
    'experienced': {
        'name': '3. Experienced Professional',
        'description': 'Experience-first layout with emphasis on career progression.',
        'best_for': 'Mid-career, Senior professionals',
        'ats_score': 'Excellent',
    },
    'academic_cv': {
        'name': '4. Academic CV',
        'description': 'Comprehensive CV layout with publications, research, and teaching.',
        'best_for': 'Faculty, Researchers, PhD candidates',
        'ats_score': 'Good',
    },
    'data_tech': {
        'name': '5. Data Analytics / Tech',
        'description': 'Skills-forward layout highlighting technical tools and projects.',
        'best_for': 'Data Scientists, ML Engineers, Analysts',
        'ats_score': 'Excellent',
    },
}


def get_template_names() -> Dict[str, str]:
    """Return dict of template_key -> display name."""
    return {k: v['name'] for k, v in TEMPLATES.items()}


def get_template_info(template_key: str) -> Dict:
    """Get full info for a template."""
    return TEMPLATES.get(template_key, TEMPLATES['ats_classic'])


# ─────────────────────────────────────────────────────────────────────────────
# HTML GENERATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """HTML-escape text."""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def _skills_html(skills) -> str:
    """Format skills into HTML."""
    if not skills:
        return ''
    if isinstance(skills, dict):
        parts = []
        for cat, lst in skills.items():
            if lst:
                skills_str = ', '.join(_esc(s) for s in lst)
                parts.append(f'<div class="skill-row"><span class="skill-cat">{_esc(cat.title())}:</span> {skills_str}</div>')
        return '\n'.join(parts)
    elif isinstance(skills, list):
        return '<div class="skill-row">' + ', '.join(_esc(s) for s in skills) + '</div>'
    return _esc(str(skills))


def _bullets_html(bullets: List[str]) -> str:
    """Format bullet points."""
    if not bullets:
        return ''
    return '<ul>' + ''.join(f'<li>{_esc(b)}</li>' for b in bullets if b) + '</ul>'


# ─────────────────────────────────────────────────────────────────────────────
# ATS CLASSIC TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

def render_ats_classic(data: Dict, template: str = 'ats_classic') -> str:
    p = data.get('personal', {})
    contact_parts = []
    for f in ['email', 'phone', 'linkedin', 'github', 'location']:
        if p.get(f): contact_parts.append(_esc(p[f]))

    sections_html = ''

    if data.get('summary'):
        sections_html += f'''
        <div class="section">
            <div class="section-title">PROFESSIONAL SUMMARY</div>
            <div class="divider"></div>
            <p class="body-text">{_esc(data["summary"])}</p>
        </div>'''

    if data.get('education'):
        edu_items = ''
        for edu in data['education']:
            edu_items += f'''
            <div class="entry">
                <div class="entry-header">
                    <strong>{_esc(edu.get("degree", ""))}</strong>
                    <span class="entry-date">{_esc(edu.get("year", ""))}</span>
                </div>
                <div class="entry-sub">{_esc(edu.get("institution", ""))}</div>
                {f'<div class="entry-detail">{_esc(edu.get("grade", ""))}</div>' if edu.get("grade") else ""}
            </div>'''
        sections_html += f'''
        <div class="section">
            <div class="section-title">EDUCATION</div>
            <div class="divider"></div>
            {edu_items}
        </div>'''

    if data.get('experience'):
        exp_items = ''
        for exp in data['experience']:
            exp_items += f'''
            <div class="entry">
                <div class="entry-header">
                    <strong>{_esc(exp.get("title", ""))}</strong>
                    <span class="entry-date">{_esc(exp.get("duration", ""))}</span>
                </div>
                <div class="entry-sub">{_esc(exp.get("company", ""))} {("| " + _esc(exp.get("location", ""))) if exp.get("location") else ""}</div>
                {_bullets_html(exp.get("bullets", []))}
            </div>'''
        sections_html += f'''
        <div class="section">
            <div class="section-title">PROFESSIONAL EXPERIENCE</div>
            <div class="divider"></div>
            {exp_items}
        </div>'''

    if data.get('internships'):
        intern_items = ''
        for exp in data['internships']:
            intern_items += f'''
            <div class="entry">
                <div class="entry-header">
                    <strong>{_esc(exp.get("title", ""))}</strong>
                    <span class="entry-date">{_esc(exp.get("duration", ""))}</span>
                </div>
                <div class="entry-sub">{_esc(exp.get("company", ""))}</div>
                {_bullets_html(exp.get("bullets", []))}
            </div>'''
        sections_html += f'''
        <div class="section">
            <div class="section-title">INTERNSHIPS</div>
            <div class="divider"></div>
            {intern_items}
        </div>'''

    if data.get('projects'):
        proj_items = ''
        for proj in data['projects']:
            meta = ' | '.join(filter(None, [proj.get('tech', ''), proj.get('year', '')]))
            proj_items += f'''
            <div class="entry">
                <div class="entry-header">
                    <strong>{_esc(proj.get("title", ""))}</strong>
                    {f'<span class="entry-date">{_esc(meta)}</span>' if meta else ""}
                </div>
                {_bullets_html(proj.get("bullets", []))}
            </div>'''
        sections_html += f'''
        <div class="section">
            <div class="section-title">PROJECTS</div>
            <div class="divider"></div>
            {proj_items}
        </div>'''

    if data.get('skills'):
        sections_html += f'''
        <div class="section">
            <div class="section-title">SKILLS</div>
            <div class="divider"></div>
            {_skills_html(data["skills"])}
        </div>'''

    if data.get('certifications'):
        cert_items = ''.join([
            f'<li>{_esc(c.get("name", ""))} | {_esc(c.get("issuer", ""))} | {_esc(c.get("year", ""))}</li>'
            for c in data['certifications']
        ])
        sections_html += f'''
        <div class="section">
            <div class="section-title">CERTIFICATIONS</div>
            <div class="divider"></div>
            <ul>{cert_items}</ul>
        </div>'''

    if data.get('achievements'):
        ach_items = ''.join([f'<li>{_esc(a)}</li>' for a in data['achievements']])
        sections_html += f'''
        <div class="section">
            <div class="section-title">ACHIEVEMENTS</div>
            <div class="divider"></div>
            <ul>{ach_items}</ul>
        </div>'''

    if data.get('publications'):
        pub_items = ''
        for i, pub in enumerate(data['publications'], 1):
            if isinstance(pub, dict):
                pub_items += f'<div class="entry"><p>{i}. {_esc(pub.get("title",""))} &mdash; {_esc(pub.get("journal",""))} ({_esc(pub.get("year",""))})</p></div>'
            else:
                pub_items += f'<div class="entry"><p>{i}. {_esc(str(pub))}</p></div>'
        sections_html += f'''
        <div class="section">
            <div class="section-title">PUBLICATIONS</div>
            <div class="divider"></div>
            {pub_items}
        </div>'''

    if data.get('languages'):
        langs = data['languages']
        lang_str = ', '.join(langs) if isinstance(langs, list) else str(langs)
        sections_html += f'''
        <div class="section">
            <div class="section-title">LANGUAGES</div>
            <div class="divider"></div>
            <p class="body-text">{_esc(lang_str)}</p>
        </div>'''

    style_profiles = {
        'ats_classic': {
            'font': "'Calibri', 'Arial', sans-serif", 'accent': '#1a1a2e', 'name_align': 'center',
            'name_size': '22pt', 'body_size': '10pt', 'section_margin': '12px 0 0', 'divider': '1.5px solid #1a1a2e',
            'contact_bg': 'transparent', 'contact_pad': '0', 'entry_border': 'none', 'section_letter': '1.5px'
        },
        'fresher': {
            'font': "'Aptos', 'Calibri', sans-serif", 'accent': '#E67300', 'name_align': 'left',
            'name_size': '24pt', 'body_size': '10.2pt', 'section_margin': '14px 0 0', 'divider': '1px solid #FF9933',
            'contact_bg': '#FFF4E6', 'contact_pad': '7px 10px', 'entry_border': 'border-left:3px solid #F3D4B0;padding-left:10px;', 'section_letter': '1px'
        },
        'experienced': {
            'font': "'Georgia', 'Times New Roman', serif", 'accent': '#92400E', 'name_align': 'left',
            'name_size': '25pt', 'body_size': '10pt', 'section_margin': '13px 0 0', 'divider': '2px solid #92400E',
            'contact_bg': '#FFFDF8', 'contact_pad': '6px 0', 'entry_border': 'border-bottom:1px solid #E8D5BC;padding-bottom:6px;', 'section_letter': '1.8px'
        },
        'academic_cv': {
            'font': "'Times New Roman', Georgia, serif", 'accent': '#111827', 'name_align': 'center',
            'name_size': '23pt', 'body_size': '10.5pt', 'section_margin': '15px 0 0', 'divider': '1px solid #111827',
            'contact_bg': 'transparent', 'contact_pad': '0', 'entry_border': 'none', 'section_letter': '1.2px'
        },
        'data_tech': {
            'font': "'Segoe UI', 'Arial', sans-serif", 'accent': '#E67300', 'name_align': 'left',
            'name_size': '24pt', 'body_size': '9.8pt', 'section_margin': '12px 0 0', 'divider': '3px solid #FF9933',
            'contact_bg': '#FFF4E6', 'contact_pad': '8px 10px', 'entry_border': 'border-left:3px solid #FF9933;padding-left:10px;', 'section_letter': '1px'
        },
    }
    cfg = style_profiles.get(template, style_profiles['ats_classic'])

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: {cfg['font']}; font-size: {cfg['body_size']}; color: #1a1a1a; background: #fff; padding: 20px 24px; max-width: 800px; margin: 0 auto; }}
  .name {{ font-size: {cfg['name_size']}; font-weight: 700; text-align: {cfg['name_align']}; color: {cfg['accent']}; letter-spacing: 0.5px; }}
  .contact {{ text-align: {cfg['name_align']}; color: #555; font-size: 9pt; margin: 6px 0 12px; background:{cfg['contact_bg']}; padding:{cfg['contact_pad']}; border-radius:6px; }}
  .contact span {{ margin: 0 6px; }}
  .section {{ margin: {cfg['section_margin']}; }}
  .section-title {{ font-size: 10pt; font-weight: 700; color: {cfg['accent']}; text-transform: uppercase; letter-spacing: {cfg['section_letter']}; }}
  .divider {{ border-top: {cfg['divider']}; margin: 3px 0 8px; }}
  .entry {{ margin-bottom: 10px; {cfg['entry_border']} }}
  .entry-header {{ display: flex; justify-content: space-between; align-items: baseline; }}
  .entry-sub {{ color: #444; font-size: 9.5pt; margin: 2px 0; }}
  .entry-detail {{ color: #666; font-size: 9pt; font-style: italic; }}
  .entry-date {{ color: #555; font-size: 9pt; white-space: nowrap; }}
  ul {{ margin: 4px 0 0 18px; }}
  li {{ margin: 2px 0; font-size: 9.5pt; line-height: 1.5; }}
  .skill-row {{ margin: 2px 0; font-size: 9.5pt; }}
  .skill-cat {{ font-weight: 600; }}
  .body-text {{ font-size: 9.5pt; line-height: 1.6; color: #222; }}
</style>
</head>
<body>
  <div class="name">{_esc(p.get("name", "Your Name"))}</div>
  <div class="contact">
    {''.join(f'<span>{part}</span>' for part in contact_parts)}
  </div>
  {sections_html}
</body>
</html>'''


def render_resume_html(data: Dict, template: str = 'ats_classic') -> str:
    """Render resume data as HTML using the selected template."""
    return render_ats_classic(data, template)
