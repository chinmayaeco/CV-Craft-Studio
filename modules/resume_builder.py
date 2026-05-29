"""
CV-Craft-Studio - Resume Builder
Session-state-backed resume data model with CRUD for all sections.
"""

import streamlit as st
from typing import Dict, List, Optional
import copy


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT RESUME STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────

EMPTY_RESUME = {
    'personal': {
        'name': '',
        'email': '',
        'phone': '',
        'linkedin': '',
        'github': '',
        'location': '',
        'portfolio': '',
    },
    'summary': '',
    'education': [],       # List[Dict]
    'experience': [],      # List[Dict]
    'internships': [],     # List[Dict]
    'projects': [],        # List[Dict]
    'skills': {
        'technical': [],
        'analytical': [],
        'soft': [],
    },
    'certifications': [],  # List[Dict]
    'achievements': [],    # List[str]
    'publications': [],    # List[Dict]
    'languages': [],       # List[str]
    'volunteering': [],    # List[Dict]
    'references': [],      # List[Dict]
}

EDUCATION_TEMPLATE = {
    'degree': '',
    'institution': '',
    'year': '',
    'grade': '',
    'details': '',
}

EXPERIENCE_TEMPLATE = {
    'title': '',
    'company': '',
    'duration': '',
    'location': '',
    'bullets': [''],
}

PROJECT_TEMPLATE = {
    'title': '',
    'tech': '',
    'year': '',
    'bullets': [''],
}

CERTIFICATION_TEMPLATE = {
    'name': '',
    'issuer': '',
    'year': '',
}

PUBLICATION_TEMPLATE = {
    'title': '',
    'journal': '',
    'year': '',
    'authors': '',
    'citations': '',
}


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def init_resume_state():
    """Initialize resume data in session state if not present."""
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = copy.deepcopy(EMPTY_RESUME)


def get_resume_data() -> Dict:
    """Get current resume data from session state."""
    init_resume_state()
    return st.session_state.resume_data


def set_resume_data(data: Dict):
    """Set resume data in session state."""
    st.session_state.resume_data = data


def reset_resume():
    """Reset resume to empty state."""
    st.session_state.resume_data = copy.deepcopy(EMPTY_RESUME)


def load_sample_resume(sample_data: Dict):
    """Load a sample resume into session state."""
    merged = copy.deepcopy(EMPTY_RESUME)
    merged.update(sample_data)
    st.session_state.resume_data = merged


# ─────────────────────────────────────────────────────────────────────────────
# PERSONAL DETAILS
# ─────────────────────────────────────────────────────────────────────────────

def render_personal_form():
    """Render personal details form and save to session state."""
    init_resume_state()
    data = st.session_state.resume_data['personal']

    st.markdown("#### 👤 Personal Details")
    col1, col2 = st.columns(2)
    with col1:
        data['name'] = st.text_input("Full Name *", value=data.get('name', ''),
                                      placeholder="e.g., Priya Sharma", key="pb_name")
        data['email'] = st.text_input("Email Address *", value=data.get('email', ''),
                                       placeholder="priya@email.com", key="pb_email")
        data['phone'] = st.text_input("Phone Number", value=data.get('phone', ''),
                                       placeholder="+91-9876543210", key="pb_phone")
        data['location'] = st.text_input("Location", value=data.get('location', ''),
                                          placeholder="Mumbai, India", key="pb_location")
    with col2:
        data['linkedin'] = st.text_input("LinkedIn URL", value=data.get('linkedin', ''),
                                          placeholder="linkedin.com/in/yourname", key="pb_linkedin")
        data['github'] = st.text_input("GitHub URL", value=data.get('github', ''),
                                        placeholder="github.com/yourhandle", key="pb_github")
        data['portfolio'] = st.text_input("Portfolio / Website", value=data.get('portfolio', ''),
                                           placeholder="yourportfolio.com", key="pb_portfolio")

    st.session_state.resume_data['personal'] = data


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def render_summary_form():
    """Render professional summary form."""
    init_resume_state()
    st.markdown("#### 📝 Professional Summary")
    st.caption("2–4 sentences about your background, key skills, and career goals.")
    summary = st.text_area(
        "Professional Summary",
        value=st.session_state.resume_data.get('summary', ''),
        height=120,
        placeholder="Data-driven professional with X years of experience in...",
        key="pb_summary"
    )
    st.session_state.resume_data['summary'] = summary
    words = len(summary.split()) if summary else 0
    color = "green" if 40 <= words <= 100 else "orange" if words > 0 else "red"
    st.markdown(f"Word count: :{color}[{words}] {'✓ Good length' if 40 <= words <= 100 else '(Target: 40–100 words)'}")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY GENERATOR (RULE-BASED)
# ─────────────────────────────────────────────────────────────────────────────

SUMMARY_TEMPLATES = {
    'Fresher': {
        'Data Analytics': "Recent {degree} graduate with hands-on experience in {skills}. Completed {projects} demonstrating ability to {action}. Seeking entry-level Data Analyst role to apply analytical skills in a business environment.",
        'Business Analytics': "Recent {degree} graduate with strong foundation in {skills}. {achievement}. Seeking Business Analyst role to leverage data-driven problem-solving skills.",
        'IT / Software': "Recent {degree} graduate proficient in {skills}. Built {projects} demonstrating end-to-end development skills. Eager to contribute technical expertise in a professional software environment.",
        'General Management': "Motivated {degree} graduate with exposure to {skills}. {achievement}. Seeking management trainee role to develop business acumen and contribute to organizational growth.",
        'Finance': "Recent {degree} graduate with strong foundation in {skills}. {achievement}. Seeking Finance Analyst role to apply quantitative and analytical skills.",
        'Marketing': "Creative {degree} graduate with skills in {skills}. {achievement}. Seeking Marketing Analyst role to drive data-informed campaign decisions.",
        'HR': "{degree} graduate with knowledge of {skills}. {achievement}. Seeking HR Analyst role to support people analytics and talent management initiatives.",
        'Operations': "{degree} graduate with knowledge of {skills} and process improvement methodologies. {achievement}. Seeking Operations Analyst role to improve organizational efficiency.",
        'Consulting': "Analytical {degree} graduate with strong {skills} skills. {achievement}. Seeking consulting role to apply structured problem-solving to business challenges.",
        'Healthcare Management': "{degree} graduate with interest in healthcare analytics and knowledge of {skills}. {achievement}. Seeking Healthcare Analyst role to support data-driven patient care decisions.",
        'Research / Academia': "{degree} graduate with research experience in {skills}. {achievement}. Seeking Research position to contribute to evidence-based academic and applied research.",
    },
    'Mid-career professional': {
        'Data Analytics': "Data Analyst with {years} years of experience delivering insights from complex datasets. Expert in {skills}. Proven record of {achievement}. Seeking to leverage expertise in a high-impact analytics role.",
        'Business Analytics': "Business Analyst with {years} years of experience in {skills}. Proven ability to {achievement}. Looking for a challenging BA role to drive strategic business improvements.",
        'IT / Software': "Software Engineer with {years} years of experience building {skills} solutions. Delivered {achievement}. Seeking senior engineering role to architect and scale production systems.",
        'Finance': "Finance professional with {years} years of experience in {skills}. Proven track record of {achievement}. Seeking Finance Manager role to drive financial performance.",
        'General Management': "Management professional with {years} years of experience leading teams and {skills}. {achievement}. Seeking leadership role to drive organizational growth.",
        'Marketing': "Marketing professional with {years} years of experience in {skills}. {achievement}. Seeking senior marketing role to lead growth initiatives.",
        'HR': "HR professional with {years} years of experience in {skills}. {achievement}. Seeking HRBP/HR Manager role to lead people strategy.",
        'Operations': "Operations professional with {years} years of experience in {skills} and process optimization. {achievement}. Seeking Operations Manager role to drive efficiency at scale.",
        'Consulting': "Consultant with {years} years of experience delivering {skills} solutions for clients across industries. {achievement}. Seeking Senior Consultant role to lead strategic engagements.",
        'Healthcare Management': "Healthcare professional with {years} years of experience in {skills}. {achievement}. Seeking senior healthcare analytics role to improve patient and operational outcomes.",
        'Research / Academia': "Researcher with {years} years of experience in {skills}. {achievement}. Seeking senior research or faculty position to lead impactful research.",
    }
}

# Default template for unmapped combinations
DEFAULT_TEMPLATE = "{career_level} professional with background in {domain}. Skilled in {skills}. {achievement}. Seeking a role where I can apply expertise to deliver business value."


def generate_summary(career_level: str, domain: str, degree: str, years: str,
                     skills: str, projects: str, achievements: str, tools: str) -> str:
    """Generate a professional summary using templates. Never invents facts."""
    # Pick template
    template = ""
    if career_level in SUMMARY_TEMPLATES:
        domain_templates = SUMMARY_TEMPLATES[career_level]
        template = domain_templates.get(domain, DEFAULT_TEMPLATE)
    else:
        template = DEFAULT_TEMPLATE

    # Prepare substitutions
    action = f"apply {tools or skills} to solve real business problems" if tools or skills else "apply analytical skills"

    result = template.format(
        degree=degree or "relevant degree",
        skills=skills or "[your key skills]",
        projects=projects or "academic/personal projects",
        achievement=achievements or "[add your achievement]",
        action=action,
        years=years or "X",
        career_level=career_level,
        domain=domain,
        tools=tools or skills or "[tools]",
    )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# EDUCATION
# ─────────────────────────────────────────────────────────────────────────────

def add_education_entry(entry: Dict):
    init_resume_state()
    st.session_state.resume_data['education'].append(entry)

def remove_education_entry(index: int):
    init_resume_state()
    st.session_state.resume_data['education'].pop(index)


# ─────────────────────────────────────────────────────────────────────────────
# SKILLS
# ─────────────────────────────────────────────────────────────────────────────

def render_skills_form():
    """Render skills section form."""
    init_resume_state()
    st.markdown("#### 🛠️ Skills")
    skills = st.session_state.resume_data.get('skills', {})
    if isinstance(skills, list):
        skills = {'technical': skills, 'analytical': [], 'soft': []}

    col1, col2, col3 = st.columns(3)
    with col1:
        tech = st.text_area("Technical Skills",
                            value=', '.join(skills.get('technical', [])),
                            placeholder="Python, SQL, Excel, Tableau...",
                            key="pb_skills_tech", height=100)
        skills['technical'] = [s.strip() for s in tech.split(',') if s.strip()]
    with col2:
        analytical = st.text_area("Analytical Skills",
                                  value=', '.join(skills.get('analytical', [])),
                                  placeholder="Data Analysis, Statistical Modeling...",
                                  key="pb_skills_analytical", height=100)
        skills['analytical'] = [s.strip() for s in analytical.split(',') if s.strip()]
    with col3:
        soft = st.text_area("Soft Skills",
                            value=', '.join(skills.get('soft', [])),
                            placeholder="Communication, Leadership...",
                            key="pb_skills_soft", height=100)
        skills['soft'] = [s.strip() for s in soft.split(',') if s.strip()]

    st.session_state.resume_data['skills'] = skills


# ─────────────────────────────────────────────────────────────────────────────
# RESUME FROM PARSED TEXT
# ─────────────────────────────────────────────────────────────────────────────

def populate_from_parsed(parsed: Dict):
    """Populate resume builder from a parsed resume dict."""
    init_resume_state()
    resume = st.session_state.resume_data

    contact = parsed.get('contact', {})
    resume['personal']['name'] = contact.get('name', '')
    resume['personal']['email'] = contact.get('email', '')
    resume['personal']['phone'] = contact.get('phone', '')
    resume['personal']['linkedin'] = contact.get('linkedin', '')
    resume['personal']['github'] = contact.get('github', '')

    sections = parsed.get('sections', {})
    resume['summary'] = sections.get('summary', '')
    resume['_raw_education'] = sections.get('education', '')
    resume['_raw_experience'] = sections.get('experience', '')
    resume['_raw_skills'] = sections.get('skills', '')
    resume['_raw_projects'] = sections.get('projects', '')
    resume['_raw_certifications'] = sections.get('certifications', '')
    resume['_raw_achievements'] = sections.get('achievements', '')

    # Parse skills
    raw_skills = sections.get('skills', '')
    if raw_skills:
        skill_items = [s.strip() for s in
                       raw_skills.replace('\n', ',').split(',') if len(s.strip()) > 1]
        resume['skills']['technical'] = skill_items[:20]

    st.session_state.resume_data = resume
