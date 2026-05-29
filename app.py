"""
CV-Craft-Studio
Build, score, improve, and export ATS-ready resumes — no paid AI APIs required.
"""

import streamlit as st
import copy
import io
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CV-Craft-Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'CV-Craft-Studio — No-cost, no-API resume builder and ATS scorer.',
    }
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

from modules.parser import parse_resume, extract_keywords, parse_resume_file
from modules.scorer import score_resume
from modules.jd_matcher import match_resume_to_jd, extract_skills_from_text
from modules.bullet_improver import improve_multiple_bullets, analyze_bullet, ACTION_VERBS_BY_DOMAIN
from modules.resume_builder import (
    init_resume_state, get_resume_data, set_resume_data, reset_resume,
    load_sample_resume, generate_summary, render_personal_form,
    render_summary_form, render_skills_form, populate_from_parsed,
    EDUCATION_TEMPLATE, EXPERIENCE_TEMPLATE, PROJECT_TEMPLATE,
    CERTIFICATION_TEMPLATE, PUBLICATION_TEMPLATE, EMPTY_RESUME
)
from modules.templates import render_resume_html, get_template_names, get_template_info, TEMPLATES
from modules.export_utils import export_pdf, export_docx, export_txt, get_export_filename
from modules.report_generator import generate_improvement_report
from modules.ui_components import (
    render_score_gauge, render_score_donut, render_section_scores_chart,
    render_score_card, render_red_flag, render_red_flags_list,
    render_keyword_chips, render_quick_action_card, render_suggestion,
    render_progress_bar, render_jd_match_chart, score_color, score_label,
    render_stat_row, render_section_header, render_info_banner, render_feature_badge
)
from modules.sample_data import (
    SAMPLE_FRESHER_RESUME, SAMPLE_EXPERIENCED_RESUME, SAMPLE_ACADEMIC_CV,
    SAMPLE_JD_DATA_ANALYST, SAMPLE_JD_BUSINESS_ANALYST, SAMPLE_JD_PROFESSOR,
    DEMO_BUILDER_DATA
)
from modules.role_profiles import ROLE_PROFILES, get_all_roles, get_role_profile
from modules.privacy import PRIVACY_CONTENT
from modules.spell_checker import check_spelling_in_sections, get_spell_check_summary, is_available as spell_available
from modules.grammar_checker import get_grammar_score, get_role_writing_tips, check_grammar
from modules.version_history import (
    init_version_history, save_version, get_versions, load_version,
    delete_version, clear_all_versions, export_all_versions_json,
    export_single_version_json, import_versions_json, get_version_count
)
from modules.analytics import (
    compute_text_analytics, compute_section_analytics,
    chart_word_frequency, chart_bullet_quality,
    chart_readability_gauge, chart_section_coverage
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────

def init_session_state():
    init_resume_state()
    init_version_history()
    defaults = {
        'parsed_resume': None,
        'resume_text': '',
        'ats_score': None,
        'jd_text': '',
        'jd_match': None,
        'current_page': 'Home Dashboard',
        'selected_template': 'ats_classic',
        'checklist_state': {},
        'bullet_results': [],
        'spell_results': None,
        'grammar_results': None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────

PAGES = [
    ('🏠', 'Home Dashboard'),
    ('📤', 'Upload & Parse Resume'),
    ('🔨', 'Resume Builder'),
    ('📊', 'ATS Resume Scorer'),
    ('🎯', 'Job Description Matcher'),
    ('✏️', 'Bullet Point Improver'),
    ('🔤', 'Spell & Grammar Check'),
    ('📦', 'Version History'),
    ('📈', 'Resume Analytics'),
    ('🎨', 'Resume Templates'),
    ('👁️', 'Resume Preview & Export'),
    ('✅', 'Resume Quality Checklist'),
    ('🎭', 'Demo Mode'),
    ('🔒', 'Privacy & Limitations'),
    ('👨‍💻', 'About Developer'),
]

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:14px 0 20px;">
        <div style="font-size:38px;margin-bottom:6px;">🧡</div>
        <div style="color:#E67300;font-size:20px;font-weight:900;letter-spacing:-0.5px;">CV-Craft-Studio</div>
        <div style="color:#4B5563;font-size:12px;font-weight:700;letter-spacing:1px;margin-top:2px;">LOCAL RESUME & JD LAB</div>
        <div style="margin-top:10px;">
            <span style="background:#FFF1DB;color:#92400E;border:1px solid #F3D4B0;border-radius:20px;padding:4px 10px;font-size:10px;font-weight:800;letter-spacing:0.5px;">NO API · FREE · OFFLINE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#FFF4E6;margin:0 0 10px;'>", unsafe_allow_html=True)

    selected_page = st.radio(
        "Navigation",
        options=[f"{icon} {name}" for icon, name in PAGES],
        label_visibility="collapsed",
        key="nav_radio"
    )
    page_name = ' '.join(selected_page.split()[1:])

    st.markdown("<hr style='border-color:#FFF4E6;margin:10px 0;'>", unsafe_allow_html=True)

    # Status panel
    resume_data = get_resume_data()
    has_name   = bool(resume_data.get('personal', {}).get('name'))
    has_parsed = st.session_state.parsed_resume is not None
    has_score  = st.session_state.ats_score is not None
    ver_count  = get_version_count()

    st.markdown("""
    <div style="color:#6B7280;font-size:10px;font-weight:700;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:8px;">Session Status</div>
    """, unsafe_allow_html=True)

    def _status_row(label, ok, extra=''):
        dot_color = '#15803D' if ok else '#B91C1C'
        txt_color = '#1F2937' if ok else '#6B7280'
        extra_part = (' <span style="color:#E67300;font-size:11px;">' + extra + '</span>') if extra else ''
        html = (
            '<div style="display:flex;align-items:center;gap:8px;margin:5px 0;">'
            '<div style="width:7px;height:7px;border-radius:50%;background:' + dot_color + ';"></div>'
            '<span style="color:' + txt_color + ';font-size:12.5px;">' + label + extra_part + '</span>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)

    _status_row('Resume Data', has_name, 'Ready' if has_name else '')
    _status_row('Parsed Resume', has_parsed, 'Loaded' if has_parsed else '')
    _status_row('ATS Score', has_score, 'Done' if has_score else '')
    if ver_count:
        st.markdown(
            f'<div style="color:#E67300;font-size:11.5px;margin-top:4px;">'
            f'📦 {ver_count} version(s) saved</div>',
            unsafe_allow_html=True
        )

    st.markdown("<hr style='border-color:#FFF4E6;margin:14px 0 8px;'>", unsafe_allow_html=True)
    st.caption("© Dr Alok Tiwari")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: HOME DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def page_home():
    st.markdown("""
    <div style="text-align: center; padding: 30px 0 20px;">
        <div style="font-size: 56px; margin-bottom: 10px;">🧡</div>
        <h1 style="color: #E67300; font-size: 42px; font-weight: 900; margin: 0;">CV-Craft-Studio</h1>
        <p style="color: #4B5563; font-size: 18px; margin: 8px 0 4px; font-weight:650;">Build · Score · Improve · Export</p>
        <p style="color: #6B7280; font-size: 14px;">ATS-ready resumes without paid AI APIs or external data transfer</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick action cards
    st.markdown("### 🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_quick_action_card('📤', 'Upload Resume',
            'Upload PDF, DOCX, or TXT and instantly parse your existing resume.', '#FF9933')
    with col2:
        render_quick_action_card('🔨', 'Build Resume',
            'Create a new resume from scratch using guided section forms.', '#E67300')
    with col3:
        render_quick_action_card('📊', 'Score Resume',
            'Get a transparent ATS score out of 100 with section breakdown.', '#15803D')
    with col4:
        render_quick_action_card('🎯', 'Match JD',
            'Compare your resume against a job description using TF-IDF matching.', '#B45309')

    st.markdown("<br>", unsafe_allow_html=True)

    # Score summary cards
    st.markdown("### 📊 Your Resume Scorecard")
    score = st.session_state.ats_score
    jd_match = st.session_state.jd_match
    parsed = st.session_state.parsed_resume
    resume_data = get_resume_data()

    # Compute completeness
    sections_filled = sum([
        bool(resume_data.get('personal', {}).get('name')),
        bool(resume_data.get('summary')),
        bool(resume_data.get('education')),
        bool(resume_data.get('experience') or resume_data.get('projects')),
        bool(resume_data.get('skills')),
        bool(resume_data.get('certifications')),
    ])
    completeness = int(sections_filled / 6 * 100)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_score_card('Completeness', completeness, 100, 'Sections filled', '📋')
    with col2:
        ats = score['total_score'] if score else 0
        render_score_card('ATS Score', ats, 100, score['grade'] if score else 'Run scorer', '🤖')
    with col3:
        jd_score = jd_match['fit_score'] if jd_match else 0
        render_score_card('Job-Fit Score', jd_score, 100, 'JD matching', '🎯')
    with col4:
        kw_pct = int(jd_match['keyword_match_pct']) if jd_match else 0
        kw_label = f"{jd_match['keyword_match_count']}/{jd_match['keyword_total']} kw" if jd_match else 'Match JD first'
        render_score_card('Keyword Match', kw_pct, 100, kw_label, '🔍')
    with col5:
        wc = parsed['word_count'] if parsed else 0
        readability = 85 if 300 <= wc <= 700 else 60 if 150 <= wc <= 1000 else 40
        render_score_card('Readability', readability, 100, 'Word count check', '📖')

    st.markdown("<br>", unsafe_allow_html=True)

    # Tips
    st.markdown("### 💡 Getting Started")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Step 1:** Upload your existing resume or build one from scratch using the sidebar navigation.")
        st.info("**Step 2:** Run the ATS Scorer to get your score out of 100 with detailed feedback.")
    with col2:
        st.info("**Step 3:** Paste a job description in the JD Matcher to find keyword gaps.")
        st.info("**Step 4:** Use the Bullet Improver and Quality Checklist to polish your resume.")

    # About
    with st.expander("ℹ️ About CV-Craft-Studio"):
        st.markdown("""
        **CV-Craft-Studio** is a completely free, offline resume tool that uses:
        - 📝 Rule-based ATS scoring (100-point transparent system)
        - 🔍 TF-IDF keyword matching with scikit-learn
        - ✏️ Template-based bullet improvement (no AI hallucination)
        - 📄 PDF/DOCX/TXT parsing with pdfplumber and python-docx
        - 📊 Interactive charts with Plotly
        - 💾 Local export using reportlab and python-docx

        **Zero dependency on:** OpenAI, Gemini, Claude, Anthropic, Groq, or any paid API.
        """)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: UPLOAD & PARSE RESUME
# ─────────────────────────────────────────────────────────────────────────────

def page_upload():
    st.title("📤 Upload & Parse Resume")
    st.caption("Upload your existing resume. Supports PDF, DOCX, and TXT formats.")

    tab1, tab2 = st.tabs(["📁 Upload File", "📋 Paste Text"])

    with tab1:
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'doc', 'txt'],
            key="resume_uploader",
            help="Max 10MB. Scanned PDFs (image-only) cannot be parsed without OCR."
        )
        if uploaded_file:
            with st.spinner("🔍 Parsing resume..."):
                try:
                    file_bytes = uploaded_file.read()
                    parsed = parse_resume(file_bytes, uploaded_file.name)
                    st.session_state.parsed_resume = parsed
                    st.session_state.resume_text = parsed['raw_text']
                    populate_from_parsed(parsed)
                    st.success(f"✅ Resume parsed! Detected {parsed['word_count']} words across {len(parsed['sections'])} sections.")
                except Exception as e:
                    st.error(f"Error parsing file: {e}")
                    return

    with tab2:
        pasted_text = st.text_area(
            "Paste your resume text here",
            height=300,
            placeholder="Paste your resume content here...",
            key="resume_paste_text"
        )
        if st.button("🔍 Parse Pasted Resume", key="parse_paste_btn"):
            if pasted_text.strip():
                with st.spinner("Parsing..."):
                    parsed = parse_resume(pasted_text.encode('utf-8'), 'pasted.txt')
                    st.session_state.parsed_resume = parsed
                    st.session_state.resume_text = parsed['raw_text']
                    populate_from_parsed(parsed)
                    st.success("✅ Resume parsed from pasted text.")
            else:
                st.warning("Please paste your resume text first.")

    # Show parsed results
    parsed = st.session_state.parsed_resume
    if parsed:
        st.markdown("---")
        st.markdown("### 📋 Extracted Information")

        # Contact info
        contact = parsed.get('contact', {})
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**👤 Contact Information**")
            icon_map = {'name': '🪪', 'email': '📧', 'phone': '📞', 'linkedin': '💼', 'github': '🐙'}
            for field, val in contact.items():
                icon = icon_map.get(field, '•')
                if val:
                    st.markdown(f"{icon} **{field.title()}:** {val}")
                else:
                    st.markdown(f"🔴 **{field.title()}:** *Not detected*")

        with col2:
            st.markdown("**📊 Document Stats**")
            st.metric("Word Count", parsed['word_count'])
            detected_secs = len([k for k in parsed['sections'] if k != '_header' and parsed['sections'][k].strip()])
            st.metric("Sections Detected", detected_secs)
            st.metric("Keywords Found", len(parsed['keywords']))

        # Sections
        st.markdown("**📂 Detected Sections**")
        sections = parsed.get('sections', {})
        for section_key, content in sections.items():
            if section_key == '_header' or not content.strip():
                continue
            with st.expander(f"📄 {section_key.replace('_', ' ').title()} ({len(content.split())} words)"):
                new_content = st.text_area(
                    f"Edit {section_key}",
                    value=content,
                    height=120,
                    key=f"edit_section_{section_key}",
                    label_visibility="collapsed"
                )
                if new_content != content:
                    st.session_state.parsed_resume['sections'][section_key] = new_content

        # Keywords
        if parsed.get('keywords'):
            st.markdown("**🔑 Top Keywords Detected**")
            render_keyword_chips(parsed['keywords'][:25], color='#FF9933', label='')

        # Populate builder button
        st.markdown("---")
        if st.button("🔨 Send to Resume Builder", key="send_to_builder", type="primary"):
            populate_from_parsed(parsed)
            st.success("✅ Resume data sent to Resume Builder! Navigate to the builder to edit.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RESUME BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def page_builder():
    st.title("🔨 Resume Builder")
    st.caption("Build your resume section by section. All data stays in your browser session.")

    if st.button("🗑️ Reset All", key="builder_reset", help="Clear all builder data"):
        reset_resume()
        st.rerun()

    tab_personal, tab_summary, tab_edu, tab_exp, tab_intern, tab_proj, tab_skills, tab_certs, tab_ach, tab_pubs = st.tabs([
        "👤 Personal", "📝 Summary", "🎓 Education", "💼 Experience",
        "🏢 Internships", "🚀 Projects", "🛠️ Skills", "📜 Certs", "🏆 Achievements", "📚 Publications"
    ])

    with tab_personal:
        render_personal_form()

    with tab_summary:
        render_summary_form()
        st.markdown("---")
        st.markdown("#### 🤖 Auto-Generate Summary (Rule-Based)")
        st.caption("Fill in the fields below and generate a template-based summary. No AI API used. Verify the output before using.")

        g_col1, g_col2 = st.columns(2)
        with g_col1:
            g_career = st.selectbox("Career Level", [
                'Fresher', 'Student', 'Internship applicant', 'Early-career professional',
                'Mid-career professional', 'Academic applicant', 'Career switcher'
            ], key="gen_career")
            g_domain = st.selectbox("Target Domain", [
                'Data Analytics', 'Business Analytics', 'Finance', 'Marketing',
                'HR', 'Operations', 'Consulting', 'Healthcare Management',
                'IT / Software', 'Research / Academia', 'General Management'
            ], key="gen_domain")
            g_degree = st.text_input("Your Degree", placeholder="MBA, B.Tech CS, etc.", key="gen_degree")
            g_years = st.text_input("Years of Experience", placeholder="3", key="gen_years")
        with g_col2:
            g_skills = st.text_input("Key Skills (comma-separated)", placeholder="Python, SQL, Excel", key="gen_skills")
            g_tools = st.text_input("Key Tools", placeholder="Power BI, Tableau, Jira", key="gen_tools")
            g_projects = st.text_input("Notable Projects (brief)", placeholder="Sales forecasting model", key="gen_projects")
            g_ach = st.text_input("Key Achievement (brief)", placeholder="Reduced cost by 15%", key="gen_ach")

        if st.button("⚡ Generate Summary", key="gen_summary_btn", type="primary"):
            generated = generate_summary(g_career, g_domain, g_degree, g_years,
                                         g_skills, g_projects, g_ach, g_tools)
            st.session_state.resume_data['summary'] = generated
            st.success("Summary generated! Edit it in the Summary tab above.")
            st.info(generated)

    with tab_edu:
        st.markdown("#### 🎓 Education")
        edu_list = st.session_state.resume_data.get('education', [])

        for i, edu in enumerate(edu_list):
            with st.expander(f"🎓 {edu.get('degree', 'Education Entry')} — {edu.get('institution', '')}", expanded=False):
                edu['degree'] = st.text_input("Degree", value=edu.get('degree', ''), key=f"edu_degree_{i}")
                edu['institution'] = st.text_input("Institution", value=edu.get('institution', ''), key=f"edu_inst_{i}")
                edu['year'] = st.text_input("Year(s)", value=edu.get('year', ''), key=f"edu_year_{i}", placeholder="2020–2024")
                edu['grade'] = st.text_input("Grade/CGPA", value=edu.get('grade', ''), key=f"edu_grade_{i}")
                edu['details'] = st.text_input("Details", value=edu.get('details', ''), key=f"edu_details_{i}")
                if st.button(f"🗑️ Remove", key=f"edu_remove_{i}"):
                    st.session_state.resume_data['education'].pop(i)
                    st.rerun()

        if st.button("➕ Add Education", key="add_edu_btn"):
            st.session_state.resume_data['education'].append(copy.deepcopy(EDUCATION_TEMPLATE))
            st.rerun()

    with tab_exp:
        st.markdown("#### 💼 Work Experience")
        exp_list = st.session_state.resume_data.get('experience', [])

        for i, exp in enumerate(exp_list):
            with st.expander(f"💼 {exp.get('title', 'Experience')} @ {exp.get('company', '')}", expanded=False):
                exp['title'] = st.text_input("Job Title", value=exp.get('title', ''), key=f"exp_title_{i}")
                exp['company'] = st.text_input("Company", value=exp.get('company', ''), key=f"exp_company_{i}")
                exp['duration'] = st.text_input("Duration", value=exp.get('duration', ''), key=f"exp_duration_{i}", placeholder="Jan 2022 – Present")
                exp['location'] = st.text_input("Location", value=exp.get('location', ''), key=f"exp_location_{i}")
                st.markdown("**Bullet Points** (one per line)")
                bullets_text = st.text_area(
                    "Bullets",
                    value='\n'.join(exp.get('bullets', [''])),
                    height=120,
                    key=f"exp_bullets_{i}",
                    label_visibility="collapsed"
                )
                exp['bullets'] = [b.strip() for b in bullets_text.split('\n') if b.strip()]
                if st.button(f"🗑️ Remove", key=f"exp_remove_{i}"):
                    st.session_state.resume_data['experience'].pop(i)
                    st.rerun()

        if st.button("➕ Add Experience", key="add_exp_btn"):
            st.session_state.resume_data['experience'].append(copy.deepcopy(EXPERIENCE_TEMPLATE))
            st.rerun()

    with tab_intern:
        st.markdown("#### 🏢 Internships")
        intern_list = st.session_state.resume_data.get('internships', [])

        for i, exp in enumerate(intern_list):
            with st.expander(f"🏢 {exp.get('title', 'Internship')} @ {exp.get('company', '')}", expanded=False):
                exp['title'] = st.text_input("Role", value=exp.get('title', ''), key=f"int_title_{i}")
                exp['company'] = st.text_input("Company", value=exp.get('company', ''), key=f"int_company_{i}")
                exp['duration'] = st.text_input("Duration", value=exp.get('duration', ''), key=f"int_duration_{i}")
                bullets_text = st.text_area(
                    "Bullets",
                    value='\n'.join(exp.get('bullets', [''])),
                    height=100,
                    key=f"int_bullets_{i}",
                    label_visibility="collapsed"
                )
                exp['bullets'] = [b.strip() for b in bullets_text.split('\n') if b.strip()]
                if st.button(f"🗑️ Remove", key=f"int_remove_{i}"):
                    st.session_state.resume_data['internships'].pop(i)
                    st.rerun()

        if st.button("➕ Add Internship", key="add_intern_btn"):
            st.session_state.resume_data['internships'].append(copy.deepcopy(EXPERIENCE_TEMPLATE))
            st.rerun()

    with tab_proj:
        st.markdown("#### 🚀 Projects")
        proj_list = st.session_state.resume_data.get('projects', [])

        for i, proj in enumerate(proj_list):
            with st.expander(f"🚀 {proj.get('title', 'Project')}", expanded=False):
                proj['title'] = st.text_input("Project Title", value=proj.get('title', ''), key=f"proj_title_{i}")
                proj['tech'] = st.text_input("Technologies", value=proj.get('tech', ''), key=f"proj_tech_{i}", placeholder="Python, SQL, Tableau")
                proj['year'] = st.text_input("Year", value=proj.get('year', ''), key=f"proj_year_{i}")
                bullets_text = st.text_area(
                    "Bullets",
                    value='\n'.join(proj.get('bullets', [''])),
                    height=100,
                    key=f"proj_bullets_{i}",
                    label_visibility="collapsed"
                )
                proj['bullets'] = [b.strip() for b in bullets_text.split('\n') if b.strip()]
                if st.button(f"🗑️ Remove", key=f"proj_remove_{i}"):
                    st.session_state.resume_data['projects'].pop(i)
                    st.rerun()

        if st.button("➕ Add Project", key="add_proj_btn"):
            st.session_state.resume_data['projects'].append(copy.deepcopy(PROJECT_TEMPLATE))
            st.rerun()

    with tab_skills:
        render_skills_form()

    with tab_certs:
        st.markdown("#### 📜 Certifications")
        certs = st.session_state.resume_data.get('certifications', [])
        for i, cert in enumerate(certs):
            with st.expander(f"📜 {cert.get('name', 'Certification')}", expanded=False):
                cert['name'] = st.text_input("Certification Name", value=cert.get('name', ''), key=f"cert_name_{i}")
                cert['issuer'] = st.text_input("Issued By", value=cert.get('issuer', ''), key=f"cert_issuer_{i}")
                cert['year'] = st.text_input("Year", value=cert.get('year', ''), key=f"cert_year_{i}")
                if st.button(f"🗑️ Remove", key=f"cert_remove_{i}"):
                    st.session_state.resume_data['certifications'].pop(i)
                    st.rerun()
        if st.button("➕ Add Certification", key="add_cert_btn"):
            st.session_state.resume_data['certifications'].append({'name': '', 'issuer': '', 'year': ''})
            st.rerun()

    with tab_ach:
        st.markdown("#### 🏆 Achievements")
        achievements = st.session_state.resume_data.get('achievements', [])
        ach_text = st.text_area(
            "List achievements (one per line)",
            value='\n'.join(achievements),
            height=150,
            key="ach_textarea",
            placeholder="Ranked top 5% in graduating class\nWinner of National Case Study Competition"
        )
        st.session_state.resume_data['achievements'] = [a.strip() for a in ach_text.split('\n') if a.strip()]

    with tab_pubs:
        st.markdown("#### 📚 Publications")
        pubs = st.session_state.resume_data.get('publications', [])
        for i, pub in enumerate(pubs):
            title_preview = pub.get('title', 'Publication')[:50]
            with st.expander(f"📚 {title_preview}...", expanded=False):
                pub['title'] = st.text_input("Title", value=pub.get('title', ''), key=f"pub_title_{i}")
                pub['journal'] = st.text_input("Journal/Conference", value=pub.get('journal', ''), key=f"pub_journal_{i}")
                pub['year'] = st.text_input("Year", value=pub.get('year', ''), key=f"pub_year_{i}")
                pub['authors'] = st.text_input("Authors", value=pub.get('authors', ''), key=f"pub_authors_{i}")
                if st.button(f"🗑️ Remove", key=f"pub_remove_{i}"):
                    st.session_state.resume_data['publications'].pop(i)
                    st.rerun()
        if st.button("➕ Add Publication", key="add_pub_btn"):
            st.session_state.resume_data['publications'].append({'title': '', 'journal': '', 'year': '', 'authors': ''})
            st.rerun()

    st.markdown("---")
    st.markdown("### 💾 Save & Preview")
    if st.button("💾 Save Resume Data", key="save_resume", type="primary"):
        st.success("✅ Resume data saved in session! Go to Preview & Export to download.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ATS SCORER
# ─────────────────────────────────────────────────────────────────────────────

def page_ats_scorer():
    st.title("📊 ATS Resume Scorer")
    st.caption("Transparent rule-based scoring system. No AI. Max 100 points.")

    score_source = st.radio(
        "Score which resume?",
        ["📋 Use Parsed/Built Resume", "📝 Paste Resume Text"],
        horizontal=True,
        key="score_source"
    )

    parsed_to_score = None

    if score_source == "📋 Use Parsed/Built Resume":
        parsed_to_score = st.session_state.parsed_resume
        if not parsed_to_score:
            resume_data = get_resume_data()
            from modules.export_utils import resume_data_to_text
            text = resume_data_to_text(resume_data)
            if len(text.strip()) > 50:
                parsed_to_score = parse_resume(text.encode('utf-8'), 'builder.txt')
            else:
                st.warning("⚠️ No resume found. Upload a resume or build one first.")
                return
    else:
        score_text = st.text_area(
            "Paste resume text to score",
            height=250,
            key="score_text_input",
            placeholder="Paste your full resume text here..."
        )
        if st.button("🔍 Parse for Scoring", key="parse_for_score"):
            if score_text.strip():
                parsed_to_score = parse_resume(score_text.encode('utf-8'), 'scored.txt')
                st.session_state.parsed_resume = parsed_to_score
            else:
                st.warning("Please paste resume text.")

    if parsed_to_score is None:
        return

    if st.button("⚡ Run ATS Score Analysis", key="run_ats_score", type="primary"):
        with st.spinner("Analyzing resume..."):
            result = score_resume(parsed_to_score)
            st.session_state.ats_score = result
            st.success("✅ Scoring complete!")

    score = st.session_state.ats_score
    if not score:
        st.info("Click 'Run ATS Score Analysis' to score your resume.")
        return

    st.markdown("---")

    # Overall score display
    col_gauge, col_details = st.columns([1, 2])
    with col_gauge:
        render_score_gauge(score['total_score'], "Overall ATS Score")
        grade_color = score_color(score['total_score'])
        st.markdown(f"<div style='text-align:center; color: {grade_color}; font-size: 18px; font-weight: 700;'>{score['grade']}</div>", unsafe_allow_html=True)

    with col_details:
        st.markdown("#### Section-by-Section Breakdown")
        render_section_scores_chart(score['sections'])

    # Section score cards
    st.markdown("---")
    st.markdown("#### 📋 Detailed Section Scores")
    section_display = [
        ('contact_info', '📱 Contact Info', 10),
        ('professional_summary', '📝 Summary', 10),
        ('education', '🎓 Education', 10),
        ('skills', '🛠️ Skills', 15),
        ('experience_projects', '💼 Experience/Projects', 20),
        ('action_verbs', '⚡ Action Verbs', 10),
        ('quantified_achievements', '📈 Quantified Results', 10),
        ('ats_formatting', '🤖 ATS Formatting', 10),
        ('length_readability', '📏 Length & Readability', 5),
    ]
    cols = st.columns(3)
    for idx, (key, label, max_pts) in enumerate(section_display):
        with cols[idx % 3]:
            s = score['sections'][key]['score']
            icon = label.split(' ')[0]
            title = label.split(' ', 1)[1]
            render_score_card(title, s, max_pts, icon)
            st.markdown("<br>", unsafe_allow_html=True)

    # Strengths and Issues
    st.markdown("---")
    col_str, col_iss = st.columns(2)
    with col_str:
        st.markdown("#### ✅ Strengths")
        for strength in score['strengths']:
            render_suggestion(strength, 'success')

    with col_iss:
        st.markdown("#### ⚠️ Issues to Fix")
        for issue in score['issues']:
            severity = 'error' if issue in score['critical_fixes'] else 'warning'
            render_suggestion(issue, severity)

    # Red Flags
    st.markdown("---")
    st.markdown("#### 🚨 Red Flag Analysis")
    render_red_flags_list(score['red_flags'])

    # Improvement plan
    st.markdown("---")
    st.markdown("#### 📋 Improvement Plan")

    if score['critical_fixes']:
        with st.expander("🚨 Critical Fixes (Do These First)", expanded=True):
            for fix in score['critical_fixes']:
                render_suggestion(fix, 'error')

    if score['quick_wins']:
        with st.expander("⚡ Quick Wins", expanded=True):
            for win in score['quick_wins']:
                render_suggestion(win, 'warning')


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: JD MATCHER
# ─────────────────────────────────────────────────────────────────────────────

def page_jd_matcher():
    st.title("🎯 Job Description Matcher")
    st.caption("Compare your resume against a job description using TF-IDF keyword matching. No AI API required.")

    jd_tab1, jd_tab2, jd_tab3 = st.tabs(["📋 Paste JD", "📤 Upload JD", "📁 Sample JDs"])

    with jd_tab1:
        jd_text = st.text_area(
            "Paste Job Description",
            value=st.session_state.jd_text,
            height=250,
            key="jd_text_input",
            placeholder="Paste the full job description here..."
        )
        if jd_text:
            st.session_state.jd_text = jd_text

    with jd_tab2:
        st.caption("Upload a job description in PDF, DOCX, DOC, or TXT format. The text is parsed locally and kept only in this session.")
        jd_upload = st.file_uploader(
            "Upload Job Description",
            type=['pdf', 'docx', 'doc', 'txt'],
            key="jd_file_uploader",
            help="Use this when the JD is saved as a PDF, Word document, or text file."
        )
        if jd_upload is not None:
            try:
                jd_bytes = jd_upload.getvalue()
                jd_uploaded_text = parse_resume_file(jd_bytes, jd_upload.name).strip()
                if jd_uploaded_text:
                    st.session_state.jd_text = jd_uploaded_text
                    st.success(f"✅ Job description uploaded and parsed: {len(jd_uploaded_text.split())} words detected.")
                    with st.expander("Preview uploaded JD text", expanded=False):
                        st.text_area("Uploaded JD Preview", value=jd_uploaded_text[:2500], height=180, disabled=True, label_visibility="collapsed")
                else:
                    st.warning("The uploaded file did not contain readable text. If it is a scanned PDF, please paste the JD text manually.")
            except Exception as exc:
                st.error(f"Could not parse uploaded job description: {exc}")

    with jd_tab3:
        sample_jd = st.selectbox(
            "Choose a sample JD",
            ['Data Analyst JD', 'Business Analyst JD', 'Assistant Professor JD'],
            key="sample_jd_select"
        )
        jd_map = {
            'Data Analyst JD': SAMPLE_JD_DATA_ANALYST,
            'Business Analyst JD': SAMPLE_JD_BUSINESS_ANALYST,
            'Assistant Professor JD': SAMPLE_JD_PROFESSOR,
        }
        if st.button("Load Sample JD", key="load_sample_jd"):
            st.session_state.jd_text = jd_map[sample_jd]
            st.rerun()
        if st.session_state.jd_text:
            preview = st.session_state.jd_text[:400] + ('...' if len(st.session_state.jd_text) > 400 else '')
            st.text_area("Current JD Preview", value=preview, height=80,
                         key="jd_preview", disabled=True, label_visibility="collapsed")

    jd_input = st.session_state.jd_text
    if not jd_input:
        st.info("Paste a job description to start matching.")
        return

    # Get resume
    parsed = st.session_state.parsed_resume
    if not parsed:
        resume_data = get_resume_data()
        from modules.export_utils import resume_data_to_text
        text = resume_data_to_text(resume_data)
        if len(text.strip()) > 50:
            parsed = parse_resume(text.encode('utf-8'), 'builder.txt')
        else:
            st.warning("⚠️ No resume found. Upload or build your resume first.")
            return

    if st.button("🎯 Match Resume to JD", key="run_jd_match", type="primary"):
        with st.spinner("Running TF-IDF analysis..."):
            match_result = match_resume_to_jd(parsed, jd_input)
            st.session_state.jd_match = match_result
            st.success("✅ Matching complete!")

    match = st.session_state.jd_match
    if not match:
        return

    st.markdown("---")

    # Score cards
    col1, col2, col3 = st.columns(3)
    with col1:
        render_score_card('Job-Fit Score', match['fit_score'], 100, score_label(match['fit_score']), '🎯')
    with col2:
        render_score_card('Keyword Match', int(match['keyword_match_pct']), 100,
                          f"{match['keyword_match_count']}/{match['keyword_total']} keywords", '🔍')
    with col3:
        render_score_card('Skill Match', int(match['skill_match_pct']), 100,
                          f"{len(match['matched_skills'])}/{len(match['jd_skills'])} skills", '🛠️')

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    col_a, col_b = st.columns(2)
    with col_a:
        render_jd_match_chart(
            match['keyword_match_count'],
            max(0, match['keyword_total'] - match['keyword_match_count']),
            "Keyword Coverage"
        )
    with col_b:
        render_jd_match_chart(
            len(match['matched_skills']),
            max(0, len(match['missing_skills'])),
            "Skill Coverage"
        )

    # Keywords
    st.markdown("---")
    st.markdown("#### 🔍 Keyword Analysis")
    col_matched, col_missing = st.columns(2)
    with col_matched:
        if match['matched_keywords']:
            render_keyword_chips(match['matched_keywords'], color='#15803D', label='✅ Matched Keywords')
    with col_missing:
        if match['missing_keywords']:
            render_keyword_chips(match['missing_keywords'], color='#B91C1C', label='❌ Missing Keywords')

    # Skills
    st.markdown("#### 🛠️ Skill Analysis")
    col_ms, col_miss = st.columns(2)
    with col_ms:
        if match['matched_skills']:
            render_keyword_chips(match['matched_skills'], color='#15803D', label='✅ Matched Skills')
        else:
            st.info("No skills from the JD found in your resume.")
    with col_miss:
        if match['missing_skills']:
            st.markdown("**❌ Missing Skills** *(Verify before adding)*")
            chips = ''.join([
                f'<span style="background: #2d1b1b; color: #B91C1C; border: 1px solid rgba(185, 28, 28, 0.27); border-radius: 16px; padding: 3px 10px; font-size: 12px; margin: 3px; display: inline-block;">{s} ⚠️</span>'
                for s in match['missing_skills'][:10]
            ])
            st.markdown(f'<div style="line-height: 2.2;">{chips}</div>', unsafe_allow_html=True)

    # Suggestions
    st.markdown("---")
    st.markdown("#### 💡 Improvement Suggestions")
    for suggestion in match['suggestions']:
        render_suggestion(suggestion, 'info')

    st.warning("⚠️ **Honesty Policy**: Only add skills and keywords to your resume that you genuinely possess. Never fabricate experience.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: BULLET IMPROVER
# ─────────────────────────────────────────────────────────────────────────────

def page_bullet_improver():
    st.title("✏️ Bullet Point Improver")
    st.caption("Rule-based improvement using writing patterns. No AI API. All [placeholders] must be replaced with your real facts.")

    col_input, col_verbs = st.columns([2, 1])

    with col_input:
        bullets_input = st.text_area(
            "Paste bullet points to improve (one per line)",
            height=200,
            key="bullet_input",
            placeholder="""Worked on sales data.
Helped the team with reports.
Was responsible for managing projects.
Participated in customer research."""
        )

    with col_verbs:
        domain = st.selectbox("Domain for verb suggestions",
                              list(ACTION_VERBS_BY_DOMAIN.keys()), key="verb_domain")
        st.markdown("**Suggested Action Verbs:**")
        verbs = ACTION_VERBS_BY_DOMAIN.get(domain, ACTION_VERBS_BY_DOMAIN['general'])
        render_keyword_chips(verbs[:15], color='#FF9933', label='')

    if st.button("⚡ Improve Bullets", key="improve_bullets_btn", type="primary"):
        if bullets_input.strip():
            bullets = [b.strip() for b in bullets_input.split('\n') if b.strip()]
            results = improve_multiple_bullets(bullets)
            st.session_state['bullet_results'] = results
        else:
            st.warning("Please paste at least one bullet point.")

    results = st.session_state.get('bullet_results', [])

    if results:
        st.markdown("---")
        st.markdown("### 📋 Results")
        st.warning("⚠️ Replace all **[insert X]** placeholders with your actual, verifiable facts before using.")

        for i, result in enumerate(results, 1):
            analysis = result['analysis']
            q_color = score_color(analysis['score'])

            with st.expander(f"Bullet {i}: {result['original'][:60]}...", expanded=True):
                col_orig, col_imp = st.columns(2)
                with col_orig:
                    st.markdown("**📌 Original:**")
                    st.code(result['original'], language=None)
                    st.markdown(f"Quality Score: **{analysis['score']}/100**")
                    if analysis['issues']:
                        for issue in analysis['issues']:
                            render_suggestion(issue, 'warning')

                with col_imp:
                    st.markdown("**✨ Improved:**")
                    st.text_area(
                        "Improved",
                        value=result['improved'],
                        height=100,
                        key=f"improved_bullet_{i}",
                        label_visibility="collapsed"
                    )
                    if result['is_placeholder_present']:
                        st.warning("⚠️ Contains placeholders — replace with real data")
                    st.markdown("**Why it improved:**")
                    for reason in result['reasoning']:
                        st.caption(f"• {reason}")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RESUME TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────

def page_templates():
    st.title("🎨 Resume Templates")
    st.caption("5 professionally designed, ATS-friendly templates. All exportable to PDF, DOCX, and TXT.")

    template_names = get_template_names()

    for key, name in template_names.items():
        info = get_template_info(key)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{name}**")
            st.caption(f"{info['description']} | Best for: {info['best_for']} | ATS: {info['ats_score']}")
        with col2:
            if st.button(f"Select", key=f"use_tmpl_{key}"):
                st.session_state.selected_template = key
                st.success(f"✅ Template '{name}' selected!")
        st.markdown("---")

    # Comparison table
    st.markdown("### 📋 Template Comparison")
    import pandas as pd
    df = pd.DataFrame([
        {
            'Template': info['name'],
            'Best For': info['best_for'],
            'ATS Score': info['ats_score'],
        }
        for info in TEMPLATES.values()
    ])
    st.dataframe(df, hide_index=True, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PREVIEW & EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def page_preview_export():
    st.title("👁️ Resume Preview & Export")
    st.caption("Preview your resume and download it as PDF, DOCX, or TXT.")

    resume_data = get_resume_data()
    if not resume_data.get('personal', {}).get('name'):
        st.warning("⚠️ Your resume is empty. Please build or upload a resume first.")
        return

    col_settings, col_preview = st.columns([1, 2])

    with col_settings:
        st.markdown("#### ⚙️ Settings")
        template_names = get_template_names()
        tmpl_keys = list(template_names.keys())
        current_idx = tmpl_keys.index(st.session_state.selected_template) if st.session_state.selected_template in tmpl_keys else 0
        selected = st.selectbox(
            "Select Template",
            tmpl_keys,
            format_func=lambda k: template_names[k],
            index=current_idx,
            key="preview_template_select"
        )
        st.session_state.selected_template = selected

        st.markdown("#### 💾 Download")

        # PDF
        if st.button("📄 Generate PDF", key="gen_pdf", type="primary"):
            try:
                with st.spinner("Generating PDF..."):
                    pdf_bytes = export_pdf(resume_data, selected)
                    filename = get_export_filename(resume_data, 'pdf')
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key="download_pdf"
                    )
                    st.success(f"✅ PDF ready!")
            except Exception as e:
                st.error(f"PDF export failed: {e}")

        # DOCX
        if st.button("📝 Generate DOCX", key="gen_docx"):
            try:
                with st.spinner("Generating DOCX..."):
                    docx_bytes = export_docx(resume_data, selected)
                    filename = get_export_filename(resume_data, 'docx')
                    st.download_button(
                        label="⬇️ Download DOCX",
                        data=docx_bytes,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="download_docx"
                    )
                    st.success(f"✅ DOCX ready!")
            except Exception as e:
                st.error(f"DOCX export failed: {e}")

        # TXT (always available)
        txt_bytes = export_txt(resume_data)
        filename_txt = get_export_filename(resume_data, 'txt')
        st.download_button(
            label="📃 Download TXT",
            data=txt_bytes,
            file_name=filename_txt,
            mime="text/plain",
            key="download_txt"
        )

        st.markdown("#### 🧾 Improvement Report")
        report_bytes = generate_improvement_report(
            resume_data,
            st.session_state.get('ats_score'),
            st.session_state.get('jd_match')
        )
        report_name = get_export_filename(resume_data, 'txt').replace('.txt', '_improvement_report.txt')
        st.download_button(
            label="⬇️ Download Improvement Report",
            data=report_bytes,
            file_name=report_name,
            mime="text/plain",
            key="download_improvement_report"
        )

    with col_preview:
        st.markdown("#### 👁️ Live Preview")
        try:
            html = render_resume_html(resume_data, selected)
            st.components.v1.html(html, height=700, scrolling=True)
        except Exception as e:
            st.error(f"Preview error: {e}")
            from modules.export_utils import resume_data_to_text
            st.text(resume_data_to_text(resume_data))


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: QUALITY CHECKLIST
# ─────────────────────────────────────────────────────────────────────────────

def page_checklist():
    st.title("✅ Resume Quality Checklist")
    st.caption("Check off items to track your resume quality. Interactive self-assessment checklist.")

    checklist_items = [
        ("contact", "📱 Contact details are complete (name, email, phone)"),
        ("linkedin", "💼 LinkedIn profile URL is included"),
        ("summary", "📝 Professional summary is clear and focused (40–100 words)"),
        ("skills_match", "🛠️ Skills section matches the target role/JD"),
        ("action_verbs", "⚡ All bullet points start with strong action verbs"),
        ("quantified", "📊 Achievements are quantified where truthfully possible"),
        ("spelling", "✍️ Resume has no spelling or grammar errors"),
        ("no_personal", "🚫 Avoids unnecessary personal details (age, photo, marital status)"),
        ("ats_format", "🤖 ATS version avoids tables, images, and icons"),
        ("length", "📏 Resume length is appropriate (1–2 pages)"),
        ("jd_keywords", "🔍 JD keywords are naturally incorporated"),
        ("dates", "📅 All experience/education entries have dates"),
        ("consistent", "📐 Formatting is consistent throughout"),
        ("no_pronouns", "📌 No first-person pronouns (I, me, my)"),
        ("email_professional", "📧 Email address is professional"),
    ]

    if 'checklist_state' not in st.session_state:
        st.session_state.checklist_state = {}

    checked = 0
    for key, label in checklist_items:
        current = st.session_state.checklist_state.get(key, False)
        value = st.checkbox(label, value=current, key=f"check_{key}")
        st.session_state.checklist_state[key] = value
        if value:
            checked += 1

    completion = int(checked / len(checklist_items) * 100)

    st.markdown("---")
    st.markdown(f"### Completion: {checked}/{len(checklist_items)} ({completion}%)")
    render_progress_bar(completion, f"{completion}% complete", color=score_color(completion))

    if completion == 100:
        st.balloons()
        st.success("🎉 Congratulations! Your resume checklist is 100% complete!")
    elif completion >= 80:
        st.success(f"✅ Great progress! {len(checklist_items) - checked} item(s) remaining.")
    elif completion >= 50:
        st.warning(f"⚠️ Good start. {len(checklist_items) - checked} item(s) still to complete.")
    else:
        st.error(f"🔴 {len(checklist_items) - checked} items still need attention.")

    if st.button("🔄 Reset Checklist", key="reset_checklist"):
        st.session_state.checklist_state = {}
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DEMO MODE
# ─────────────────────────────────────────────────────────────────────────────

def page_demo():
    st.title("🎭 Demo Mode")
    st.caption("Try the app with pre-loaded sample resumes and job descriptions. No file uploads needed.")

    demo_option = st.selectbox(
        "Select a demo profile to load",
        [
            '👩‍💻 Fresher Resume (Priya Sharma — B.Tech CS)',
            '💼 Experienced Professional (Rahul Mehta — Senior Data Analyst)',
            '🎓 Academic CV (Dr. Ananya Krishnan — Assistant Professor)',
            '📋 Demo Builder Data (Arjun Verma — MBA Business Analyst)',
        ],
        key="demo_select"
    )

    jd_option = st.selectbox(
        "Load a sample Job Description",
        ['None', '📊 Data Analyst JD', '📈 Business Analyst JD', '🎓 Assistant Professor JD'],
        key="demo_jd_select"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎭 Load Demo Resume", key="load_demo", type="primary"):
            sample_map = {
                '👩‍💻 Fresher Resume (Priya Sharma — B.Tech CS)': SAMPLE_FRESHER_RESUME,
                '💼 Experienced Professional (Rahul Mehta — Senior Data Analyst)': SAMPLE_EXPERIENCED_RESUME,
                '🎓 Academic CV (Dr. Ananya Krishnan — Assistant Professor)': SAMPLE_ACADEMIC_CV,
                '📋 Demo Builder Data (Arjun Verma — MBA Business Analyst)': None,
            }
            selected_text = sample_map.get(demo_option)

            if selected_text is None:
                load_sample_resume(copy.deepcopy(DEMO_BUILDER_DATA))
                st.success("✅ Demo builder data loaded! Navigate to Resume Builder to see it.")
            else:
                parsed = parse_resume(selected_text.encode('utf-8'), 'demo.txt')
                st.session_state.parsed_resume = parsed
                st.session_state.resume_text = selected_text
                populate_from_parsed(parsed)
                st.success(f"✅ Demo resume loaded: {parsed['contact'].get('name', 'Unknown')}")

    with col2:
        if st.button("📋 Load Sample JD", key="load_demo_jd") and jd_option != 'None':
            jd_map = {
                '📊 Data Analyst JD': SAMPLE_JD_DATA_ANALYST,
                '📈 Business Analyst JD': SAMPLE_JD_BUSINESS_ANALYST,
                '🎓 Assistant Professor JD': SAMPLE_JD_PROFESSOR,
            }
            if jd_option in jd_map:
                st.session_state.jd_text = jd_map[jd_option]
                st.success("✅ Sample JD loaded. Go to JD Matcher to run analysis.")

    # Show loaded resume
    if st.session_state.parsed_resume:
        st.markdown("---")
        st.markdown("### 📄 Loaded Resume Preview")
        parsed = st.session_state.parsed_resume
        contact = parsed.get('contact', {})
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Name", contact.get('name', 'N/A'))
        col_b.metric("Words", parsed.get('word_count', 0))
        col_c.metric("Sections", len([k for k, v in parsed.get('sections', {}).items()
                                       if k != '_header' and v.strip()]))

        with st.expander("📄 Full Resume Text"):
            st.text(st.session_state.resume_text[:3000])

        st.markdown("### ⚡ Quick Actions")
        if st.button("📊 Run ATS Score on Demo", key="demo_score", type="primary"):
            result = score_resume(parsed)
            st.session_state.ats_score = result
            st.success(f"✅ ATS Score: **{result['total_score']}/100** — {result['grade']}")
            render_score_gauge(result['total_score'], "Demo ATS Score")

    # Role profiles
    st.markdown("---")
    st.markdown("### 📚 Role-Specific Guidance")
    roles = get_all_roles()
    selected_role = st.selectbox("Explore role profiles", roles, key="demo_role_select")
    profile = get_role_profile(selected_role)

    if profile:
        col_kw, col_tools = st.columns(2)
        with col_kw:
            st.markdown("**🔑 Recommended Keywords**")
            render_keyword_chips(profile.get('keywords', [])[:12], '#FF9933', '')
        with col_tools:
            st.markdown("**🛠️ Key Tools**")
            render_keyword_chips(profile.get('tools', []), '#E67300', '')

        if profile.get('bullet_examples'):
            st.markdown("**📝 Example Bullet Structures**")
            for example in profile['bullet_examples']:
                st.code(example, language=None)

        if profile.get('common_mistakes'):
            st.markdown("**⚠️ Common Mistakes to Avoid**")
            for mistake in profile['common_mistakes']:
                render_suggestion(mistake, 'warning')

        if profile.get('focus_areas'):
            st.markdown("**🎯 Focus Areas for Your Resume**")
            for area in profile['focus_areas']:
                render_suggestion(area, 'info')


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PRIVACY
# ─────────────────────────────────────────────────────────────────────────────

def page_privacy():
    st.title("🔒 Privacy & Limitations")
    st.markdown(PRIVACY_CONTENT)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ABOUT DEVELOPER
# ─────────────────────────────────────────────────────────────────────────────

def page_about_developer():
    st.title("👨‍💻 About the Developer")
    st.caption("Developer profile and academic context behind CV-Craft-Studio.")

    photo_path = os.path.join(os.path.dirname(__file__), "assets", "developer_photo.jpeg")
    col_photo, col_text = st.columns([1, 2.2])

    with col_photo:
        if os.path.exists(photo_path):
            st.image(photo_path, caption="Dr Alok Tiwari", use_container_width=True)
        else:
            st.info("Developer photo not found in assets folder.")

    with col_text:
        st.subheader("Dr Alok Tiwari")
        st.markdown("""
        **Assistant Professor — Big Data Analytics**  
        **Goa Institute of Management, Goa**

        Dr Alok Tiwari works at the intersection of artificial intelligence, healthcare analytics, medical image analysis, explainable AI, management-focused data science, and GenAI-enabled pedagogy. His work focuses on making advanced analytics more practical, interpretable, and useful for students, researchers, and professionals.
        """)
        st.link_button("🌐 Visit Portfolio", "https://dr-alok-tiwari.github.io/")

    st.divider()
    st.subheader("🔬 Core Areas")
    core_areas = [
        "Healthcare AI and medical image analysis",
        "Explainable and responsible AI",
        "Applied data science for healthcare and business decisions",
        "GenAI-enabled pedagogy and faculty development",
        "MLOps and production-ready AI workflows",
    ]
    for area in core_areas:
        st.info(area)

    st.divider()
    st.subheader("🛠️ Skills & Tools")
    skill_cols = st.columns(3)
    skill_groups = {
        "AI & Analytics": ["Machine Learning", "Deep Learning", "Computer Vision", "NLP", "Explainable AI"],
        "Programming": ["Python", "R", "SQL", "MATLAB", "Streamlit"],
        "Deployment & Teaching": ["MLOps", "Docker", "Power BI", "Orange", "GenAI for Education"],
    }
    for col, (group, skills) in zip(skill_cols, skill_groups.items()):
        with col:
            st.markdown(f"**{group}**")
            for skill in skills:
                st.write(f"• {skill}")

    st.divider()
    st.markdown("**© Dr Alok Tiwari. CV-Craft-Studio is developed as a privacy-friendly, no-paid-API tool for resume building, JD matching, and career-readiness support.**")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE ROUTER
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SPELL & GRAMMAR CHECK
# ─────────────────────────────────────────────────────────────────────────────

def page_spell_grammar():
    st.title("🔤 Spell & Grammar Check")
    st.caption("Rule-based spell and grammar checking. No AI API. Uses pyspellchecker + regex rules.")
    render_feature_badge('Spell Check', is_new=True)

    # Get text to check
    text_source = st.radio(
        "Text to check:",
        ["📋 Use Parsed/Built Resume", "📝 Paste Text"],
        horizontal=True, key="sg_source"
    )

    check_text = ''
    parsed_sections = {}

    if text_source == "📋 Use Parsed/Built Resume":
        parsed = st.session_state.parsed_resume
        if parsed:
            check_text = parsed.get('raw_text', '')
            parsed_sections = {k: v for k, v in parsed.get('sections', {}).items()
                               if k != '_header' and v.strip()}
        else:
            resume_data = get_resume_data()
            from modules.export_utils import resume_data_to_text
            check_text = resume_data_to_text(resume_data).decode('utf-8', errors='replace')
            parsed_sections = {'full_resume': check_text}
        if not check_text.strip():
            st.warning("⚠️ No resume loaded. Upload or build your resume first.")
            return
    else:
        check_text = st.text_area(
            "Paste text to check",
            height=200,
            key="sg_paste",
            placeholder="Paste your resume or bullet points here..."
        )
        parsed_sections = {'pasted': check_text}

    if st.button("🔍 Run Spell & Grammar Check", key="run_sg", type="primary"):
        if check_text.strip():
            with st.spinner("Analysing..."):
                st.session_state.spell_results   = check_spelling_in_sections(parsed_sections)
                st.session_state.grammar_results = get_grammar_score(check_text)
        else:
            st.warning("Please provide some text first.")

    # ── Spell Check Results ──────────────────────────────────────────────────
    spell_res   = st.session_state.spell_results
    grammar_res = st.session_state.grammar_results

    if spell_res is None and grammar_res is None:
        render_info_banner(
            "Click 'Run Spell & Grammar Check' to analyse your resume text.",
            '#FF9933', '🔤'
        )
        return

    st.markdown("---")

    # Summary row
    g_score   = grammar_res['score'] if grammar_res else 100
    g_issues  = grammar_res['total_issues'] if grammar_res else 0
    sp_total  = sum(len(v) for v in (spell_res or {}).values())
    sp_avail  = spell_available()

    render_stat_row([
        {'label': 'Grammar Score', 'value': f"{g_score}/100",  'icon': '📝', 'color': score_color(g_score)},
        {'label': 'Grammar Issues', 'value': g_issues,          'icon': '⚠️', 'color': '#B45309'},
        {'label': 'Spelling Errors', 'value': sp_total if sp_avail else 'N/A', 'icon': '🔤', 'color': '#B91C1C' if sp_total else '#15803D'},
        {'label': 'Grammar Grade',  'value': grammar_res['grade'] if grammar_res else '-', 'icon': '🎓', 'color': '#FF9933'},
    ])

    tab_grammar, tab_spell, tab_tips = st.tabs(["📝 Grammar Issues", "🔤 Spelling", "💡 Writing Tips"])

    with tab_grammar:
        if grammar_res and grammar_res['issues']:
            st.markdown(f"**{len(grammar_res['issues'])} issue(s) found** — {grammar_res['summary']}")
            st.markdown("")
            for issue in grammar_res['issues']:
                sev = issue['severity']
                sev_color = {'high': '#B91C1C', 'medium': '#B45309', 'low': '#2563EB'}.get(sev, '#888')
                st.markdown(f"""
                <div style="background:rgba(30,42,58,0.8);border-left:3px solid {sev_color};
                            border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="color:#ffffff;font-weight:600;font-size:13.5px;">⚠️ {issue['rule_name']}</span>
                        <span style="background:{sev_color}22;color:{sev_color};border:1px solid {sev_color}44;
                                     border-radius:12px;padding:2px 8px;font-size:10px;font-weight:700;"
                        >{sev.upper()}</span>
                    </div>
                    <div style="color:#1F2937;font-size:13px;margin:6px 0;">Matched: <code style="color:#E67300;background:rgba(230,115,0,0.1);padding:1px 6px;border-radius:4px;">{issue['matched_text']}</code></div>
                    <div style="color:#4B5563;font-size:12.5px;margin:4px 0;">{issue['message']}</div>
                    <div style="color:#6B7280;font-size:11.5px;font-style:italic;margin-top:4px;">✏️ {issue['example']}</div>
                    <div style="color:#555;font-size:11px;margin-top:6px;">Context: {issue['context'][:80]}...</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No significant grammar issues found!")

    with tab_spell:
        if not sp_avail:
            st.info("ℹ️ Install pyspellchecker for spell checking: `pip install pyspellchecker`")
        elif spell_res:
            for section, errors in spell_res.items():
                if errors and not errors[0].get('error'):
                    st.markdown(f"**📄 {section.replace('_',' ').title()}** — {len(errors)} possible error(s)")
                    for err in errors:
                        suggestions = ', '.join(err['suggestions'][:3]) if err['suggestions'] else 'No suggestions'
                        st.markdown(f"""
                        <div style="background:rgba(185,28,28,0.08);border-left:2px solid #B91C1C;
                                    border-radius:0 6px 6px 0;padding:8px 14px;margin:4px 0;">
                            <span style="color:#B91C1C;font-weight:600;">{err['word']}</span>
                            <span style="color:#4B5563;font-size:12px;"> → {suggestions}</span>
                            <br><span style="color:#6B7280;font-size:11px;">{err['context'][:70]}</span>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.success("✅ No spelling errors found!")

    with tab_tips:
        roles = get_all_roles()
        tip_role = st.selectbox("Get tips for role:", roles, key="tip_role")
        tips = get_role_writing_tips(tip_role)
        st.markdown(f"**Writing tips for {tip_role}:**")
        for tip in tips:
            render_suggestion(tip, 'info')
        st.markdown("---")
        st.markdown("**📌 Universal Resume Writing Rules**")
        universal = [
            "Start every bullet point with a strong past-tense action verb",
            "Quantify achievements: use numbers, %, $, or K/M where truthful",
            "Avoid first-person pronouns (I, me, my, we, our)",
            "Keep bullets to 1–2 lines; avoid paragraph-style descriptions",
            "Be consistent: either all bullets end with a period or none do",
            "Use the exact keywords from the job description naturally",
            "Proofread once for spelling, once for grammar, once for formatting",
        ]
        for rule in universal:
            render_suggestion(rule, 'success')


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: VERSION HISTORY
# ─────────────────────────────────────────────────────────────────────────────

def page_version_history():
    st.title("📦 Version History")
    st.caption("Save snapshots of your resume, restore previous versions, and export/import as JSON.")
    render_feature_badge('Version History', is_new=True)

    resume_data = get_resume_data()
    col_save, col_exp, col_imp = st.columns([2, 1, 1])

    with col_save:
        ver_label = st.text_input(
            "Version label (optional)",
            placeholder="e.g., 'Before adding ML experience'",
            key="ver_label"
        )
        if st.button("💾 Save Current Version", key="save_ver", type="primary"):
            if resume_data.get('personal', {}).get('name'):
                v = save_version(resume_data, ver_label)
                st.success(f"✅ Saved: **{v['label']}** at {v['timestamp_display']}")
            else:
                st.warning("⚠️ Your resume is empty. Build or upload a resume first.")

    with col_exp:
        if get_version_count() > 0:
            json_bytes = export_all_versions_json()
            st.download_button(
                "⬇️ Export All Versions",
                data=json_bytes,
                file_name="cv_craft_studio_versions.json",
                mime="application/json",
                key="exp_versions"
            )

    with col_imp:
        uploaded_json = st.file_uploader(
            "Import versions JSON",
            type=['json'],
            key="imp_versions_upload",
            label_visibility="collapsed"
        )
        if uploaded_json:
            result = import_versions_json(uploaded_json.read())
            if result['success']:
                st.success(f"✅ Imported {result['count']} version(s)!")
            else:
                st.error(f"Import failed: {result['error']}")

    st.markdown("---")

    versions = get_versions()
    if not versions:
        render_info_banner(
            "No versions saved yet. Build your resume and click 'Save Current Version' to create a snapshot.",
            '#FF9933', '📦'
        )
        return

    st.markdown(f"### 📚 Saved Versions ({len(versions)})")

    for ver in versions:
        summary = ver.get('summary', {})
        name    = summary.get('name', 'Unnamed')
        secs    = summary.get('sections', [])
        sec_str = ' · '.join(secs) if secs else 'No sections'

        with st.expander(
            f"📦 {ver['label']}  —  {ver['timestamp_display']}  |  {name}",
            expanded=False
        ):
            col_info, col_actions = st.columns([3, 1])
            with col_info:
                st.markdown(f"""
                <div style="color:#4B5563;font-size:12.5px;">
                    <div>👤 <strong style="color:#1F2937;">{name}</strong></div>
                    <div style="margin-top:4px;">📋 {sec_str}</div>
                    <div style="margin-top:4px;">🕐 {ver['timestamp_display']}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_actions:
                if st.button("⏮️ Restore", key=f"restore_{ver['id']}", type="primary"):
                    data = load_version(ver['id'])
                    if data:
                        from modules.resume_builder import load_sample_resume
                        load_sample_resume(data)
                        st.success(f"✅ Restored: {ver['label']}")
                        st.rerun()

                # Export single version
                single_json = export_single_version_json(ver['id'])
                if single_json:
                    st.download_button(
                        "⬇️ Export",
                        data=single_json,
                        file_name=f"resume_v{ver['id']}.json",
                        mime="application/json",
                        key=f"exp_{ver['id']}"
                    )

                if st.button("🗑️ Delete", key=f"del_{ver['id']}"):
                    delete_version(ver['id'])
                    st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear All Versions", key="clear_all_ver"):
        clear_all_versions()
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: RESUME ANALYTICS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def page_analytics():
    st.title("📈 Resume Analytics Dashboard")
    st.caption("Deep-dive analytics on your resume content — word frequency, readability, bullet quality, and section coverage.")
    render_feature_badge('Analytics', is_new=True)

    parsed     = st.session_state.parsed_resume
    resume_data = get_resume_data()

    # Get the text
    if parsed:
        text = parsed.get('raw_text', '')
    else:
        from modules.export_utils import resume_data_to_text
        raw = resume_data_to_text(resume_data)
        text = raw.decode('utf-8', errors='replace') if isinstance(raw, bytes) else raw

    if not text.strip() or len(text.split()) < 30:
        st.warning("⚠️ Your resume has insufficient text for analytics. Upload or build a resume first.")
        return

    # Compute analytics
    with st.spinner("Computing analytics..."):
        ta = compute_text_analytics(text)
        sa = compute_section_analytics(resume_data)

    if not ta:
        st.error("Could not compute analytics.")
        return

    # ── Top stat strip ──────────────────────────────────────────────────────
    render_stat_row([
        {'label': 'Total Words',     'value': ta['word_count'],        'icon': '📝', 'color': '#FF9933'},
        {'label': 'Unique Words',    'value': ta['unique_words'],       'icon': '🔤', 'color': '#E67300'},
        {'label': 'Action Verbs',    'value': ta['action_verb_count'],  'icon': '⚡', 'color': '#15803D'},
        {'label': 'Quantified Lines','value': ta['quantified_lines'],   'icon': '📊', 'color': '#B45309'},
        {'label': 'Readability',     'value': ta['readability_label'],  'icon': '📖', 'color': '#2563EB'},
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Word Frequency + Section Coverage ─────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        render_section_header("Top Keywords Used", "Most frequent meaningful words in your resume", "🔑")
        if ta.get('top_words'):
            fig = chart_word_frequency(ta['top_words'])
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        render_section_header("Section Coverage", "How complete is each major resume section", "📋")
        fig2 = chart_section_coverage(resume_data)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Readability + Bullet Quality ──────────────────────────────────
    col3, col4 = st.columns(2)
    with col3:
        render_section_header("Readability Score", "Flesch Reading Ease (higher = easier to read)", "📖")
        fig3 = chart_readability_gauge(ta['flesch_score'])
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("""
        <div style="color:#4B5563;font-size:12px;padding:8px 0;">
            <b style="color:#1F2937;">Ideal range for resumes:</b> 50–70 (Standard to Fairly Easy)<br>
            Very difficult text (score < 35) may alienate ATS and recruiters.
        </div>
        """, unsafe_allow_html=True)
    with col4:
        render_section_header("Bullet Quality by Section", "% bullets that are quantified & start with action verbs", "⚡")
        if sa:
            fig4 = chart_bullet_quality(sa)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Add experience/projects with bullet points to see quality metrics.")

    # ── Detailed metrics ─────────────────────────────────────────────────────
    st.markdown("---")
    render_section_header("Detailed Text Metrics", icon="📊")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Avg Words/Sentence",  ta['avg_words_per_sentence'])
        st.metric("Vocabulary Richness", f"{ta['vocabulary_richness']}%")
    with m_col2:
        st.metric("Action Verb Usage",   f"{ta['action_verb_pct']}%")
        st.metric("Quantification Rate", f"{ta['quantified_pct']}%")
    with m_col3:
        st.metric("Long Sentences (>30w)", ta['long_sentences'])
        st.metric("Flesch Score",          ta['flesch_score'])

    # Recommendations
    st.markdown("---")
    render_section_header("Analytics-Based Recommendations", icon="💡")
    recs = []
    if ta['word_count'] < 250:
        recs.append(('warning', f"Your resume has only {ta['word_count']} words. Aim for 300–700 words."))
    elif ta['word_count'] > 900:
        recs.append(('warning', f"Resume may be too long ({ta['word_count']} words). Consider trimming to under 750."))
    else:
        recs.append(('success', f"Word count ({ta['word_count']}) is in the ideal range (250–750)."))
    if ta['action_verb_pct'] < 3:
        recs.append(('error', f"Only {ta['action_verb_pct']}% of words are action verbs. Target 5%+."))
    else:
        recs.append(('success', f"Good action verb usage: {ta['action_verb_pct']}% of words."))
    if ta['quantified_pct'] < 20:
        recs.append(('warning', f"Only {ta['quantified_pct']}% of lines have numbers/metrics. Add more quantified achievements."))
    else:
        recs.append(('success', f"{ta['quantified_pct']}% of lines are quantified — great!"))
    if ta['vocabulary_richness'] < 50:
        recs.append(('warning', "Low vocabulary richness suggests repetitive language. Use more varied vocabulary."))
    if ta['long_sentences'] > 3:
        recs.append(('warning', f"{ta['long_sentences']} sentences are too long (>30 words). Break them into concise bullets."))
    for sev, msg in recs:
        render_suggestion(msg, sev)



# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ABOUT DEVELOPER
# ─────────────────────────────────────────────────────────────────────────────

def page_about_developer():
    st.title("👨‍💻 About the Developer")
    st.caption("Developer profile and academic context behind CV-Craft-Studio.")

    photo_path = os.path.join(os.path.dirname(__file__), "assets", "developer_photo.jpeg")
    col_photo, col_text = st.columns([1, 2.2])

    with col_photo:
        if os.path.exists(photo_path):
            st.image(photo_path, caption="Dr Alok Tiwari", use_container_width=True)
        else:
            st.info("Developer photo not found in assets folder.")

    with col_text:
        st.subheader("Dr Alok Tiwari")
        st.markdown("""
        **Assistant Professor — Big Data Analytics**  
        **Goa Institute of Management, Goa**

        Dr Alok Tiwari works at the intersection of artificial intelligence, healthcare analytics, medical image analysis, explainable AI, management-focused data science, and GenAI-enabled pedagogy. His work focuses on making advanced analytics more practical, interpretable, and useful for students, researchers, and professionals.
        """)
        st.link_button("🌐 Visit Portfolio", "https://dr-alok-tiwari.github.io/")

    st.divider()
    st.subheader("🔬 Core Areas")
    core_areas = [
        "Healthcare AI and medical image analysis",
        "Explainable and responsible AI",
        "Applied data science for healthcare and business decisions",
        "GenAI-enabled pedagogy and faculty development",
        "MLOps and production-ready AI workflows",
    ]
    for area in core_areas:
        st.info(area)

    st.divider()
    st.subheader("🛠️ Skills & Tools")
    skill_cols = st.columns(3)
    skill_groups = {
        "AI & Analytics": ["Machine Learning", "Deep Learning", "Computer Vision", "NLP", "Explainable AI"],
        "Programming": ["Python", "R", "SQL", "MATLAB", "Streamlit"],
        "Deployment & Teaching": ["MLOps", "Docker", "Power BI", "Orange", "GenAI for Education"],
    }
    for col, (group, skills) in zip(skill_cols, skill_groups.items()):
        with col:
            st.markdown(f"**{group}**")
            for skill in skills:
                st.write(f"• {skill}")

    st.divider()
    st.markdown("**© Dr Alok Tiwari. CV-Craft-Studio is developed as a privacy-friendly, no-paid-API tool for resume building, JD matching, and career-readiness support.**")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE ROUTER
# ─────────────────────────────────────────────────────────────────────────────

PAGE_FUNCTIONS = {
    'Home Dashboard': page_home,
    'Upload & Parse Resume': page_upload,
    'Resume Builder': page_builder,
    'ATS Resume Scorer': page_ats_scorer,
    'Job Description Matcher': page_jd_matcher,
    'Bullet Point Improver': page_bullet_improver,
    'Spell & Grammar Check': page_spell_grammar,
    'Version History': page_version_history,
    'Resume Analytics': page_analytics,
    'Resume Templates': page_templates,
    'Resume Preview & Export': page_preview_export,
    'Resume Quality Checklist': page_checklist,
    'Demo Mode': page_demo,
    'Privacy & Limitations': page_privacy,
    'About Developer': page_about_developer,
}

page_fn = PAGE_FUNCTIONS.get(page_name, page_home)
page_fn()
