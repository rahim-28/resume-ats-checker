import streamlit as st
import pdfplumber
import re
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
def calculate_ats_score(sections, skills_found, email, phone):
    score = 0

    # Contact info
    if email:
        score += 10
    if phone:
        score += 10

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


# Streamlit UI
st.set_page_config(page_title="Resume ATS Checker", page_icon="📄")

st.title("📄 Resume ATS Checker (Free AI Project)")
st.write("Upload your resume PDF and get an ATS-style score with suggestions.")

uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

if uploaded_file:
    st.success("Resume uploaded successfully!")

    resume_text = extract_text_from_pdf(uploaded_file)

    st.subheader("📌 Resume Preview (First 1500 characters)")
    st.text_area("Extracted Resume Text", resume_text[:1500], height=200)

    email = extract_email(resume_text)
    phone = extract_phone(resume_text)

    sections = check_sections(resume_text)
    skills_found = extract_skills(resume_text)

    score = calculate_ats_score(sections, skills_found, email, phone)

    st.subheader("✅ ATS Score")
    st.progress(score / 100)
    st.write(f"### ⭐ ATS Score: {score}/100")

    st.subheader("📞 Contact Info Detected")
    st.write("**Email:**", email if email else "❌ Not Found")
    st.write("**Phone:**", phone if phone else "❌ Not Found")

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

    st.subheader("🚀 Suggestions to Improve ATS Score")
    suggestions = []

    if not email:
        suggestions.append("Add a valid email address.")
    if not phone:
        suggestions.append("Add a phone number.")
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
