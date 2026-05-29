"""
CV-Craft-Studio - Privacy Page Content
"""

PRIVACY_CONTENT = """
## 🔒 Privacy, Safety & Limitations

### Data Processing

**How your data is processed:**

> CV-Craft-Studio processes all uploaded files and text **entirely within your local browser session**. 
> No data is transmitted to any external server, API, or cloud service.

- ✅ All resume parsing happens locally using Python libraries
- ✅ All scoring and analysis runs on your machine
- ✅ No internet connection required after installation
- ✅ Files are not saved unless you explicitly download/export them
- ✅ Session data is cleared when you close the browser tab

### What We Do NOT Do

- ❌ We do NOT send your resume to OpenAI, Gemini, Claude, or any paid AI API
- ❌ We do NOT store your data on any cloud server
- ❌ We do NOT require account creation or login
- ❌ We do NOT use paid third-party services
- ❌ We do NOT track or profile users

### Recommendation

> **Avoid uploading highly sensitive personal data** (such as government IDs, financial details, 
> or sensitive medical information) unless strictly necessary for your resume.
> Your resume should contain only professional information.

---

### How Scoring Works

The ATS scoring system is **fully rule-based and transparent**:

| Section | Max Points | Method |
|---|---|---|
| Contact Information | 10 | Regex detection of email, phone, LinkedIn |
| Professional Summary | 10 | Presence, length, and action verb check |
| Education | 10 | Degree keywords + date presence |
| Skills | 15 | Skill count + technical tool detection |
| Experience/Projects | 20 | Bullet count, dates, org names |
| Action Verbs | 10 | Match against a curated verb list |
| Quantified Achievements | 10 | Regex patterns for numbers/percentages |
| ATS Formatting | 10 | Section heading detection + symbol check |
| Length & Readability | 5 | Word count range check |

**No AI or machine learning is used for scoring.** All criteria are openly defined.

---

### Job Description Matching

The JD matcher uses:
- **TF-IDF vectorization** + cosine similarity (via scikit-learn)
- **Keyword extraction** from the job description
- **Skill dictionary matching** (100+ skills predefined locally)

**Important**: The app will never tell you to add skills you don't have. 
Missing skills are always labeled as:
- *"Verify before adding"* — confirm you have this skill first
- *"Learn before claiming"* — upskill before listing on resume

---

### Known Limitations

1. **PDF parsing quality** depends on how the PDF was created. Scanned image PDFs will not parse well (no OCR).
2. **Name detection** is heuristic and may not work perfectly for non-standard formatting.
3. **Section detection** depends on recognizable headings. Unconventional headings may not be detected.
4. **Scoring is rule-based** — a human reviewer may evaluate differently.
5. **Bullet improvement** uses templates — always review and verify suggestions before using.
6. The app works best with **English-language resumes**.
7. Complex multi-column PDF layouts may result in mixed-up text order after parsing.

---

### Responsible Use

- ✅ Use suggested improvements only if they reflect your actual experience
- ✅ Replace all `[insert X]` placeholders with your real, verifiable facts
- ✅ Do not claim skills, certifications, or achievements you don't actually have
- ✅ Resume accuracy is your responsibility as the user

---

*CV-Craft-Studio is free, local-first, and operates without paid APIs. No paid APIs, 
no cloud storage, no user tracking.*
"""

LIMITATIONS = [
    "PDF parsing may fail for scanned/image-based PDFs (no OCR support)",
    "Name extraction is heuristic — works best with standard resume formatting",
    "Section detection requires recognizable English section headings",
    "Scoring is rule-based, not AI — results may differ from human evaluation",
    "Bullet improvement uses templates — always verify before using",
    "Best results with English-language resumes in standard formats",
    "Multi-column PDF layouts may produce mixed text order",
]
