import streamlit as st

# Page Configuration
st.set_page_config(page_title="UAE ATS CV Builder", page_icon="🇦🇪", layout="wide")

st.title("🇦🇪 UAE ATS-Optimized CV Builder")
st.caption("Designed to pass corporate parser algorithms and match high-volume hiring standards.")
st.write("---")

# Layout: Split into sidebar inputs and main preview area
with st.sidebar:
    st.header("👤 Personal Information")
    full_name = st.text_input("Full Name", placeholder="e.g., Aashutosh Badal")
    target_title = st.text_input("Target Job Title", placeholder="e.g., Operations Manager / Compliance Specialist")
    
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("Location", placeholder="e.g., Dubai, UAE")
        email = st.text_input("Email")
    with col2:
        phone = st.text_input("Phone Number", placeholder="e.g., +971 50 XXXXXXX")
        linkedin = st.text_input("LinkedIn URL")

    st.write("---")
    st.header("📝 Professional Summary")
    summary = st.text_area(
        "Write a punchy summary focusing on data-driven results and operational efficiency:",
        placeholder="Result-oriented professional with extensive experience managing high-volume data, scaling operations..."
    )

    st.write("---")
    st.header("🛠️ Core Competencies & Skills")
    skills_input = st.text_input("Enter skills (comma-separated)", placeholder="Data Analysis, CRM Systems, Project Management, Client Relations")

    st.write("---")
    st.header("💼 Work Experience")
    job_title = st.text_input("Job Title", placeholder="e.g., Senior Operations Specialist")
    company = st.text_input("Company & City", placeholder="e.g., Emirates Group, Dubai")
    job_dates = st.text_input("Dates Employed", placeholder="e.g., Jan 2024 - Present")
    job_details = st.text_area(
        "Key Achievements (One per line, start with strong action verbs):",
        placeholder="• Managed high-volume client operations resulting in a 20% efficiency increase.\n• Automated data tracking protocols to enhance reporting accuracy."
    )

# Main Preview Area (The actual ATS-friendly template)
st.subheader("👀 Live ATS Preview")
st.info("💡 Tip: ATS parsers love simple text layouts with zero complex tables, graphics, or columns in the body.")

with st.container(border=True):
    # Header Section
    st.markdown(f"<h1 style='text-align: center; margin-bottom: 0;'>{full_name if full_name else 'YOUR FULL NAME'}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray;'>{target_title if target_title else 'Target Job Title'}</p>", unsafe_allow_html=True)
    
    contact_info = f"📍 {location} | ✉️ {email} | 📞 {phone}"
    if linkedin:
        contact_info += f" | 🔗 [LinkedIn]({linkedin})"
    st.markdown(f"<p style='text-align: center; font-size: 14px;'>{contact_info}</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Summary Section
    if summary:
        st.markdown("### 📋 PROFESSIONAL SUMMARY")
        st.write(summary)
        st.write("---")
        
    # Skills Section
    if skills_input:
        st.markdown("### 🔑 CORE COMPETENCIES")
        skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]
        st.write(" • ".join(skills_list))
        st.write("---")

    # Experience Section
    st.markdown("### 💼 PROFESSIONAL EXPERIENCE")
    if job_title or company:
        col_j1, col_j2 = st.columns([3, 1])
        with col_j1:
            st.markdown(f"**{job_title}** | *{company}*")
        with col_j2:
            st.markdown(f"<p style='text-align: right;'>{job_dates}</p>", unsafe_allow_html=True)
        if job_details:
            st.write(job_details)
    else:
        st.write("*Start typing your experience in the sidebar to populate this section...*")