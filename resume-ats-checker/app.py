import streamlit as st
import pdfplumber
import re
import pandas as pd
from skills import SKILLS


# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.lower()


# Extract Email
def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group() if match else None


# Extract Phone
def extract_phone(text):
    match = re.search(r"\+?\d[\d\s\-]{8,}\d", text)
    return match.group() if match else None


# Extract GitHub / LinkedIn Links
def extract_links(text):
    github = re.search(r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+", text)
    linkedin = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+", text)

    return {
        "github": github.group() if github else None,
        "linkedin": linkedin.group() if linkedin else None,
    }


# Detect sections
def check_sections(text):
    sections = {
        "education": "education" in text,
        "projects": "project" in text,
        "experience": "experience" in text or "internship" in text,
        "skills": "skills" in text,
        "certifications": "certification" in text,
        "summary": "summary" in text or "objective" in text,
    }
    return sections


# Extract skills
def extract_skills(text):
    found = []
    for skill in SKILLS:
        if skill in text:
            found.append(skill)
    return sorted(set(found))


# Calculate ATS Score
def calculate_ats_score(sections, skills_found, email, phone, github, linkedin):
    score = 0

    # Contact info
    if email:
        score += 10
    if phone:
        score += 10

    # Links scoring
    if github:
        score += 5
    if linkedin:
        score += 5

    # Sections scoring
    if sections["summary"]:
        score += 10
    if sections["education"]:
        score += 15
    if sections["projects"]:
        score += 15
    if sections["experience"]:
        score += 15
    if sections["skills"]:
        score += 10
    if sections["certifications"]:
        score += 5

    # Skills scoring
    if len(skills_found) >= 5:
        score += 10
    if len(skills_found) >= 10:
        score += 10

    return min(score, 100)


# Job Description Match
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


# Generate TXT Report
def generate_report(
    score,
    email,
    phone,
    github,
    linkedin,
    sections,
    skills_found,
    match_score=None,
    matched=None,
    missing=None,
):

    report = f"""
==============================
      RESUME ATS REPORT
==============================

ATS Score: {score}/100

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
    if skills_found:
        report += ", ".join(skills_found) + "\n"
    else:
        report += "No skills detected\n"

    if match_score is not None:
        report += f"\nJob Match Score: {match_score}%\n"

        report += "\nMatched Skills:\n"
        report += ", ".join(matched) + "\n" if matched else "None\n"

        report += "\nMissing Skills:\n"
        report += ", ".join(missing) + "\n" if missing else "None\n"

    report += "\n==============================\n"
    return report


# Streamlit UI
st.set_page_config(page_title="Resume ATS Checker", page_icon="📄")

st.title("📄 Resume ATS Checker (Free AI Project)")
st.write(
    "Upload your resume PDF and optionally paste Job Description to check match score."
)

uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
job_desc = st.text_area("📌 Paste Job Description (Optional)", height=200)

if uploaded_file:
    st.success("Resume uploaded successfully!")

    resume_text = extract_text_from_pdf(uploaded_file)

    st.subheader("📌 Resume Preview (First 1500 characters)")
    st.text_area("Extracted Resume Text", resume_text[:1500], height=200)

    email = extract_email(resume_text)
    phone = extract_phone(resume_text)

    links = extract_links(resume_text)
    github = links["github"]
    linkedin = links["linkedin"]

    sections = check_sections(resume_text)
    skills_found = extract_skills(resume_text)

    score = calculate_ats_score(sections, skills_found, email, phone, github, linkedin)

    st.subheader("✅ ATS Score")
    st.progress(score / 100)
    st.write(f"### ⭐ ATS Score: {score}/100")

    st.subheader("📞 Contact Info Detected")
    st.write("**Email:**", email if email else "❌ Not Found")
    st.write("**Phone:**", phone if phone else "❌ Not Found")

    st.subheader("🔗 Profile Links Detected")
    st.write("**GitHub:**", github if github else "❌ Not Found")
    st.write("**LinkedIn:**", linkedin if linkedin else "❌ Not Found")

    st.subheader("📌 Sections Found")
    for sec, found in sections.items():
        if found:
            st.write(f"✅ {sec.title()}")
        else:
            st.write(f"❌ {sec.title()}")

    st.subheader("🧠 Skills Found")
    if skills_found:
        st.write(", ".join(skills_found))
    else:
        st.write("❌ No skills detected")

    match_score = None
    matched = None
    missing = None

    # Job description match
    if job_desc.strip():
        st.subheader("🎯 Job Description Match Score")

        match_score, matched, missing, job_skills = job_match(skills_found, job_desc)

        st.progress(match_score / 100)
        st.write(f"### 🔥 Match Score: {match_score}%")

        st.write("✅ **Matched Skills:**")
        if matched:
            st.write(", ".join(matched))
        else:
            st.write("❌ No skills matched")

        st.write("⚠️ **Missing Skills:**")
        if missing:
            st.write(", ".join(missing))
        else:
            st.write("🔥 No missing skills. Great match!")

    st.subheader("🚀 Suggestions to Improve ATS Score")
    suggestions = []

    if not email:
        suggestions.append("Add a valid email address.")
    if not phone:
        suggestions.append("Add a phone number.")
    if not github:
        suggestions.append("Add your GitHub profile link.")
    if not linkedin:
        suggestions.append("Add your LinkedIn profile link.")
    if not sections["summary"]:
        suggestions.append("Add a Summary / Objective section.")
    if not sections["education"]:
        suggestions.append("Add Education section.")
    if not sections["projects"]:
        suggestions.append("Add Projects section.")
    if not sections["experience"]:
        suggestions.append("Add Experience / Internship section.")
    if len(skills_found) < 5:
        suggestions.append("Add more relevant technical skills.")
    if not sections["certifications"]:
        suggestions.append("Add Certifications (optional but helpful).")

    if suggestions:
        for s in suggestions:
            st.write("⚠️", s)
    else:
        st.write("🔥 Your resume looks ATS-friendly!")

    # DOWNLOAD SECTION
    st.subheader("📥 Download Report")

    report_text = generate_report(
        score,
        email,
        phone,
        github,
        linkedin,
        sections,
        skills_found,
        match_score,
        matched,
        missing,
    )

    st.download_button(
        label="⬇️ Download Report as TXT",
        data=report_text,
        file_name="resume_ats_report.txt",
        mime="text/plain",
    )

    report_data = {
        "ATS Score": [score],
        "Email Found": [bool(email)],
        "Phone Found": [bool(phone)],
        "GitHub Found": [bool(github)],
        "LinkedIn Found": [bool(linkedin)],
        "Skills Count": [len(skills_found)],
    }

    if job_desc.strip():
        report_data["Job Match Score"] = [match_score]
        report_data["Matched Skills"] = [", ".join(matched)]
        report_data["Missing Skills"] = [", ".join(missing)]

    df_report = pd.DataFrame(report_data)
    csv_data = df_report.to_csv(index=False)

    st.download_button(
        label="⬇️ Download Report as CSV",
        data=csv_data,
        file_name="resume_ats_report.csv",
        mime="text/csv",
    )
