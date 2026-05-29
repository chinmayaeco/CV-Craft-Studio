# CV-Craft-Studio Changelog

## Build prepared on 2026-05-29

### Branding
- Renamed the product to **CV-Craft-Studio** across app title, README, privacy text, verification output, and visible labels.

### UI/UX
- Replaced the previous dark purple/teal interface with a clean saffron professional UI.
- Removed custom UI gradients that could reduce text readability.
- Improved contrast for cards, buttons, tabs, inputs, metrics, alerts, sidebar, and chips.
- Updated Streamlit theme configuration to light saffron mode.

### Features
- Added a local **Resume Improvement Report** generator.
- Added report download from the Preview & Export page.
- Report includes ATS score, JD fit score, strengths, issues, red flags, missing keywords, missing skills, and priority actions.

### Fixes
- Fixed bullet-improver logic that could create awkward outputs such as “Developed analyzed...”.
- Preserved the no-API/offline approach.
- Removed generated cache files from the packaged release.

### Verification
- `python verify.py`: passed
- `python -m pytest tests/ -v`: 40 passed
- Streamlit launch was not run inside the sandbox because Streamlit is not installed in the execution environment; it remains listed in `requirements.txt` for normal installation.

## 2026-05-29 - Gauge compatibility hotfix
- Replaced Plotly-incompatible 8-digit hex threshold color (`#ffffff55`) with valid RGBA syntax in the ATS score gauge.
- Replaced one 8-digit HTML border color with RGBA for broader compatibility.
- Re-ran verification, tests, and Python compilation checks successfully.

## 2026-05-29 - Streamlit Cloud stability and JD upload update
- Added **Upload JD** support in Job Description Matcher for PDF, DOCX, DOC, and TXT files.
- Added **About Developer** page with developer profile, photo, portfolio link, core areas, and skills/tools.
- Added sidebar copyright line: © Dr Alok Tiwari.
- Replaced deprecated image parameter with `use_container_width=True`.
- Converted custom divider alpha colors to `rgba(...)` syntax to avoid raw HTML/CSS rendering issues.
- Added `runtime.txt` with Python 3.11 for Streamlit Cloud compatibility.
- Kept `.streamlit/config.toml` cloud-safe with `headless = true`; local auto-open is handled through `start_app.bat` and `start_app.sh`.
- Updated resume template preview so different template selections visibly change the preview layout.
- Smoke-tested Streamlit server startup successfully in headless mode.
