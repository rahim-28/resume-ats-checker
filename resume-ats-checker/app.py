import streamlit as st
import pdfplumber
import re
import pandas as pd
from docx import Document
from skills import SKILLS


# ----------------------------
# TEXT EXTRACTION
# ----------------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.lower()


def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text.lower()


# ----------------------------
# CONTACT EXTRACTION
# ----------------------------
def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group() if match else None


def extract_phone(text):
    match = re.search(r"\+?\d[\d\s\-]{8,}\d", text)
    return match.group() if match else None


def extract_links(text):
    github = re.search(r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+", text)
    linkedin = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+", text)

    return {
        "github": github.group() if github else None,
        "linkedin": linkedin.group() if linkedin else None,
    }


# ----------------------------
# SMART SECTION DETECTION
# ----------------------------
SECTION_KEYWORDS = {
    "summary": ["summary", "objective", "profile", "about me"],
    "education": ["education", "academic", "qualification", "university", "college"],
    "projects": ["projects", "project", "academic project", "mini project"],
    "experience": ["experience", "work experience", "internship", "employment"],
    "skills": ["skills", "technical skills", "key skills"],
    "certifications": ["certifications", "certification", "courses", "training"],
}


def check_sections(text):
    detected = {}
    for section, keywords in SECTION_KEYWORDS.items():
        detected[section] = any(word in text for word in keywords)
    return detected


# ----------------------------
# SKILLS EXTRACTION
# ----------------------------
def extract_skills(text):
    found = []
    for skill in SKILLS:
        if skill in text:
            found.append(skill)
    return sorted(set(found))


# ----------------------------
# JOB DESCRIPTION MATCH
# ----------------------------
def job_match(resume_skills, job_desc_text):
    job_desc_text = job_desc_text.lower()
    job_skills = []

    for skill in SKILLS:
        if skill in job_desc_text:
            job_skills.append(skill)

    job_skills = sorted(set(job_skills))

    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]

    if len(job_skills) == 0:
        match_score = 0
    else:
        match_score = int((len(matched) / len(job_skills)) * 100)

    return match_score, matched, missing, job_skills


# ----------------------------
# JOB ROLE SUGGESTIONS
# ----------------------------
def suggest_roles(skills_found):
    skills_found = [s.lower() for s in skills_found]
    roles = []

    if "python" in skills_found and (
        "django" in skills_found or "flask" in skills_found or "fastapi" in skills_found
    ):
        roles.append("Backend Developer (Python)")

    if "react" in skills_found or "javascript" in skills_found:
        roles.append("Frontend Developer")

    if (
        "machine learning" in skills_found
        or "deep learning" in skills_found
        or "tensorflow" in skills_found
        or "pytorch" in skills_found
    ):
        roles.append("Machine Learning Engineer")

    if (
        "pandas" in skills_found
        and "numpy" in skills_found
        and (
            "power bi" in skills_found
            or "tableau" in skills_found
            or "excel" in skills_found
        )
    ):
        roles.append("Data Analyst")

    if "sql" in skills_found and (
        "postgresql" in skills_found or "mysql" in skills_found
    ):
        roles.append("Database Developer")

    if "aws" in skills_found or "docker" in skills_found or "linux" in skills_found:
        roles.append("DevOps / Cloud Engineer (Junior)")

    if not roles:
        roles.append("Software Developer / Intern")

    return roles


# ----------------------------
# ATS SCORING WITH BREAKDOWN (REALISTIC)
# ----------------------------
def calculate_score_breakdown(
    sections, skills_found, email, phone, github, linkedin, match_score=None
):
    breakdown = {
        "Contact Score": 0,
        "Links Score": 0,
        "Section Score": 0,
        "Skills Score": 0,
        "JD Match Bonus": 0,
    }

    # Contact (20 max)
    if email:
        breakdown["Contact Score"] += 10
    if phone:
        breakdown["Contact Score"] += 10

    # Links (10 max)
    if github:
        breakdown["Links Score"] += 5
    if linkedin:
        breakdown["Links Score"] += 5

    # Sections (50 max)
    if sections["summary"]:
        breakdown["Section Score"] += 10
    if sections["education"]:
        breakdown["Section Score"] += 10
    if sections["projects"]:
        breakdown["Section Score"] += 10
    if sections["experience"]:
        breakdown["Section Score"] += 10
    if sections["skills"]:
        breakdown["Section Score"] += 5
    if sections["certifications"]:
        breakdown["Section Score"] += 5

    # Skills Count (10 max)
    if len(skills_found) >= 5:
        breakdown["Skills Score"] += 5
    if len(skills_found) >= 10:
        breakdown["Skills Score"] += 5

    # JD Match Bonus (10 max)
    if match_score is not None:
        if match_score >= 70:
            breakdown["JD Match Bonus"] = 10
        elif match_score >= 40:
            breakdown["JD Match Bonus"] = 5
        else:
            breakdown["JD Match Bonus"] = 0

    total = sum(breakdown.values())
    total = min(total, 100)

    return total, breakdown


# ----------------------------
# REPORT GENERATOR
# ----------------------------
def generate_report(
    score,
    breakdown,
    email,
    phone,
    github,
    linkedin,
    sections,
    skills_found,
    match_score=None,
    matched=None,
    missing=None,
    roles=None,
):

    report = f"""
==============================
     RESUME ATS REPORT (PRO UI)
==============================

Final ATS Score: {score}/100

Score Breakdown:
"""

    for k, v in breakdown.items():
        report += f"- {k}: {v}\n"

    report += f"""

Contact Info:
- Email: {email if email else "Not Found"}
- Phone: {phone if phone else "Not Found"}

Links:
- GitHub: {github if github else "Not Found"}
- LinkedIn: {linkedin if linkedin else "Not Found"}

Sections Found:
"""

    for sec, found in sections.items():
        report += f"- {sec.title()}: {'Yes' if found else 'No'}\n"

    report += "\nSkills Found:\n"
    report += ", ".join(skills_found) + "\n" if skills_found else "No skills detected\n"

    if roles:
        report += "\nSuggested Job Roles:\n"
        for r in roles:
            report += f"- {r}\n"

    if match_score is not None:
        report += f"\nJob Match Score: {match_score}%\n"

        report += "\nMatched Skills:\n"
        report += ", ".join(matched) + "\n" if matched else "None\n"

        report += "\nMissing Skills:\n"
        report += ", ".join(missing) + "\n" if missing else "None\n"

    report += "\n==============================\n"
    return report


# ----------------------------
# STREAMLIT UI
# ----------------------------
st.set_page_config(page_title="Resume ATS Checker PRO", page_icon="📄", layout="wide")

st.markdown(
    """
    <style>
    .main-title {
        font-size: 40px;
        font-weight: bold;
        color: #00b4d8;
    }
    .sub-title {
        font-size: 18px;
        color: #888;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">📄 Resume ATS Checker PRO</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">Upload Resume • Get ATS Score • Match JD • Download Report</div>',
    unsafe_allow_html=True,
)

st.write("")

# Sidebar
st.sidebar.header("📂 Upload Resume")
uploaded_file = st.sidebar.file_uploader(
    "Upload Resume (PDF / DOCX)", type=["pdf", "docx"]
)
job_desc = st.sidebar.text_area("📌 Paste Job Description (Optional)", height=250)

st.sidebar.write("---")
st.sidebar.info("Tip: Add Job Description to get Match Score + Missing Skills.")

if uploaded_file:
    st.success("✅ Resume uploaded successfully!")

    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file format!")
        st.stop()

    # Extract info
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)
    links = extract_links(resume_text)
    github = links["github"]
    linkedin = links["linkedin"]

    sections = check_sections(resume_text)
    skills_found = extract_skills(resume_text)

    match_score = None
    matched = None
    missing = None

    if job_desc.strip():
        match_score, matched, missing, job_skills = job_match(skills_found, job_desc)

    final_score, breakdown = calculate_score_breakdown(
        sections, skills_found, email, phone, github, linkedin, match_score
    )

    roles = suggest_roles(skills_found)

    # Metrics Row
    col1, col2, col3 = st.columns(3)

    col1.metric("⭐ ATS Score", f"{final_score}/100")
    col2.metric("🧠 Skills Found", len(skills_found))
    col3.metric(
        "🎯 JD Match Score", f"{match_score}%" if match_score is not None else "N/A"
    )

    st.write("")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Score Details", "🧠 Skills & Roles", "🎯 JD Match", "📥 Download Report"]
    )

    with tab1:
        st.subheader("📊 Score Breakdown")
        for k, v in breakdown.items():
            st.write(f"✅ **{k}:** {v}")

        st.write("---")

        st.subheader("📞 Contact Info")
        st.write("**Email:**", email if email else "❌ Not Found")
        st.write("**Phone:**", phone if phone else "❌ Not Found")

        st.write("---")

        st.subheader("🔗 Profile Links")
        st.write("**GitHub:**", github if github else "❌ Not Found")
        st.write("**LinkedIn:**", linkedin if linkedin else "❌ Not Found")

        st.write("---")

        with st.expander("📌 Sections Found"):
            for sec, found in sections.items():
                st.write(f"{'✅' if found else '❌'} {sec.title()}")

        with st.expander("📌 Resume Preview (First 1500 characters)"):
            st.text_area("Preview", resume_text[:1500], height=250)

    with tab2:
        st.subheader("🧠 Skills Found")
        if skills_found:
            st.write(", ".join(skills_found))
        else:
            st.write("❌ No skills detected")

        st.write("---")

        st.subheader("💼 Suggested Job Roles")
        for r in roles:
            st.write("✅", r)

    with tab3:
        if job_desc.strip():
            st.subheader("🎯 Job Match Score")
            st.progress(match_score / 100)
            st.write(f"### 🔥 Match Score: {match_score}%")

            st.write("✅ **Matched Keywords:**")
            st.write(", ".join(matched) if matched else "❌ None")

            st.write("⚠️ **Missing Keywords:**")
            st.write(", ".join(missing) if missing else "🔥 None (Perfect Match!)")
        else:
            st.warning(
                "⚠️ Paste a Job Description in the sidebar to see Match Score and Missing Skills."
            )

    with tab4:
        st.subheader("📥 Download Your ATS Report")

        report_text = generate_report(
            final_score,
            breakdown,
            email,
            phone,
            github,
            linkedin,
            sections,
            skills_found,
            match_score,
            matched,
            missing,
            roles,
        )

        st.download_button(
            label="⬇️ Download TXT Report",
            data=report_text,
            file_name="resume_ats_report_pro.txt",
            mime="text/plain",
        )

        report_data = {
            "Final ATS Score": [final_score],
            "Email Found": [bool(email)],
            "Phone Found": [bool(phone)],
            "GitHub Found": [bool(github)],
            "LinkedIn Found": [bool(linkedin)],
            "Skills Count": [len(skills_found)],
            "Suggested Roles": [", ".join(roles)],
        }

        if job_desc.strip():
            report_data["Job Match Score"] = [match_score]
            report_data["Matched Skills"] = [", ".join(matched)]
            report_data["Missing Skills"] = [", ".join(missing)]

        df_report = pd.DataFrame(report_data)
        csv_data = df_report.to_csv(index=False)

        st.download_button(
            label="⬇️ Download CSV Report",
            data=csv_data,
            file_name="resume_ats_report_pro.csv",
            mime="text/csv",
        )

else:
    st.info("👈 Upload a Resume in the sidebar to start analysis.")
