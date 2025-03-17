import pybase64
import io
import os
import time
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
import streamlit as st
from PIL import Image
import PyPDF2 as pdf
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --------------------------
# Core Functionality (Unchanged)
# --------------------------
def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(input_text)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    return "".join(page.extract_text() or '' for page in reader.pages)

# --------------------------
# UI Configuration
# --------------------------
st.set_page_config(
    page_title="GrowON",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open("styles/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Background image with overlay
def set_background(image_path):
    with open(image_path, "rb") as file:
        encoded_image = pybase64.b64encode(file.read()).decode()
    
    background_style = f"""
    <style>
    .stApp {{
        background: linear-gradient(
            rgba(0, 0, 0, 0.6),
            rgba(0, 0, 0, 0.6)
        ), url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)

set_background("bg.jpg")  # Set your background image

# --------------------------
# Sidebar Configuration
# --------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>📥 Input Details</h2>
    </div>
    """, unsafe_allow_html=True)
    
    role = st.text_input("Job Role", placeholder="e.g., Marketing Manager")
    jd = st.text_area("Job Description", height=200,
                     placeholder="Paste full job description here...")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

# --------------------------
# Main Content Area
# --------------------------
st.markdown("""
<div class="main-header">
    <h1>GrowON: ATS Optimization Suite</h1>
    <h3>Cross the ATS Hurdle with AI-Powered Precision</h3>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class="intro-card">
    <p>🔍 Powered by Google Gemini Pro, GrowON provides:</p>
    <ul>
        <li>ATS Compliance Analysis</li>
        <li>Keyword Optimization</li>
        <li>Skills Gap Identification</li>
        <li>Personalized Interview Prep</li>
    </ul>
    <div class="disclaimer">
        ⚠️ Note: Always validate suggestions with human review
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------
# Analysis Tools
# --------------------------
st.markdown("### 🔍 Analysis Tools")
button_cols = st.columns(5)
with button_cols[0]:
    submit1 = st.button("Resume Analysis", use_container_width=True)
with button_cols[1]:
    submit2 = st.button("Match Percentage", use_container_width=True)
with button_cols[2]:
    submit3 = st.button("Skill Development", use_container_width=True)
with button_cols[3]:
    submit4 = st.button("Customization Tips", use_container_width=True)
with button_cols[4]:
    submit5 = st.button("Interview Prep", use_container_width=True)

# --------------------------
# Validation & Processing
# --------------------------
def validate_inputs():
    errors = []
    if not role.strip():
        st.error("❗ Please specify a job role")
        errors.append("role")
    if not jd.strip():
        st.error("❗ Please provide job description")
        errors.append("jd")
    if not uploaded_file:
        st.error("❗ Please upload your resume")
        errors.append("resume")
    return len(errors) == 0

def create_response_card(title, content):
    return f"""
    <div class="response-card">
        <h4>{title}</h4>
        <div class="response-content">{content}</div>
    </div>
    """

# Handle button actions
def handle_analysis(prompt_template, title):
    if validate_inputs():
        text = input_pdf_text(uploaded_file)
        with st.spinner('🔍 Analyzing documents...'):
            try:
                prompt = prompt_template.format(
                    role=role,
                    text=text,
                    jd=jd
                )
                response = get_gemini_response(prompt)
                st.markdown(create_response_card(title, response),
                          unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error processing request: {str(e)}")

# Process button clicks
if submit1:
    if len(role) > 0:
        if uploaded_file is not None:
            text = input_pdf_text(uploaded_file)
            if len(jd) > 0:
                with st.spinner('Please Wait..'):
                    prompt1 = f"""
                    You are a professional and experienced ATS(Application Tracking System) with a deep understanding of {role} fields. Analyze the provided resume and job description (JD). Provide a detailed analysis (200-300 words) of how the resume aligns with the JD, highlighting key areas of strength, relevant experiences, and qualifications. Discuss any notable achievements or skills that are particularly well-matched to the job requirements.
                    
                    Here is the resume content : {text}
                    Here is the job description : {jd}
                    Your Response Should have the following structure
                    Example:
                    
                    Note: Only Mention and Analyze the content of the provided resume text. Make sure Nothing additional is added outside the provided text 
                    
                    Resume Analysis and Alignment with Job Description:

                    Overview: 
                    The resume presents a strong background in software engineering, with a particular emphasis on full-stack development and cloud technologies.
                    
                    Strengths:
                    - Technical Proficiency: Proficient in key programming languages such as Python, JavaScript, and Java, aligning well with the job's technical requirements.
                    - Project Experience: Showcases several projects that demonstrate the ability to design, develop, and deploy scalable software solutions, mirroring the JD's emphasis on hands-on experience.
                    
                    Relevant Experiences: (Highlight only the things that are present in the resume.)
                    - Lead Developer Role: Led a team in developing a SaaS application using microservices architecture, directly relevant to the job's focus on leadership and microservices.
                    - Cloud Solutions Architect: Experience in designing cloud infrastructure on AWS, aligning with the JD's requirement for cloud computing skills.
                    
                    """

                    response = get_gemini_response(prompt1)
                st.write(response)  # Use st.write to display the response
            else:
                st.error("No job description provided.")
            
        else:
            st.error("No job description provided.")
            st.error("Resume Not Uploaded.")
    else:
        st.error("No Job Role Specified")
        st.error("No job description provided.")
        st.error("Resume Not Uploaded.")
        

if submit2:
    if len(role) > 0:
        if uploaded_file is not None:
            text = input_pdf_text(uploaded_file)
            if len(jd) > 0:
                with st.spinner('Please Wait..'):
                    prompt2 = f"""
                    You are a professional and experienced ATS(Application Tracking System) focused exclusively on the {role} field. Your task is to evaluate the resume strictly based on the provided job description and resume content. It is critical to only identify and list the keywords and phrases that have a direct match between the resume and the JD. Highlight any crucial keywords or skills required for the job that are absent in the resume. Based on your analysis, provide a percentage match.

                    Important: Your analysis must strictly adhere to the content provided below. Do not infer or add any keywords, skills, or technologies not explicitly mentioned in these texts. Re-evaluate the texts to ensure accuracy. Recheck before you provide your response

                    Resume Content: {text}
                    Job Description: {jd}
                    
                    Never provide anything which is neither present in resume content nor job description.
                    
                    Output should strictly follow this structure:

                    Percentage Match: [Provide percentage]

                    Matched Keywords:
                    - Skills: [List only the matched skills found in both the job description and resume content. recheck before you provide your response]
                    - Technologies: [List only the matched technologies found in both the job description and resume. Recheck before you provide your response]
                    - Methodologies: [List only the matched methodologies found in both the job description and resume. Recheck before you provide your response]

                    Missing Keywords:
                    - [List the skills or technologies crucial for the role found in the job description but not in the resume. Recheck before you provide your response]

                    Final Thoughts:
                    - [Provide a brief assessment focusing on the alignment, matched keywords, missing elements, and percentage match. Reinforce the instruction to only mention elements present in the provided texts. Recheck before you provide your response]

                    
                    """

                    response = get_gemini_response(prompt2)
                st.subheader("Percentage Match Analysis")
                st.write(response)  # Use st.write to display the response
            else:
                st.error("No job description provided.")
            
        else:
            st.error("No job description provided.")
            st.error("Resume Not Uploaded.")
    else:
        st.error("No Job Role Specified")
        st.error("No job description provided.")
        st.error("Resume Not Uploaded.")

if submit3:
    if len(role) > 0:
        if uploaded_file is not None:
            text = input_pdf_text(uploaded_file)
            if len(jd) > 0:
                with st.spinner('Please Wait..'):
                    prompt3 = f"""
                    You are a professional and experienced ATS(Application Tracking System) with a deep understanding of {role} fields. Based on the analysis of the resume and the job description, suggest specific improvements and additions to the candidate's skill set (200-300 words). Identify areas where the candidate falls short and recommend actionable steps or resources for acquiring or enhancing the necessary skills. Highlight the importance of these skills in the context of the targeted job role.
                    
                    Here is the resume content : {text}
                    Here is the job description : {jd}
                    Your Response Should have the following structure
                    Example:
                    
                    Note: Only Mention and Analyze the content of the provided resume text. Make sure Nothing additional is added outside the provided text 
                    
                    Skills Improvement and Addition Suggestions:

                    To further align your resume with the job requirements and the evolving trends in software engineering, consider the following improvements:

                    Expand Knowledge in Emerging Technologies:
                    - Dive into Machine Learning and Big Data Analytics; consider online courses or projects that demonstrate practical application.
                    - Familiarize yourself with Blockchain Technology, given its growing impact on secure and decentralized systems.
                    
                    Enhance Cloud Computing Skills:
                    - Gain deeper expertise in cloud services beyond AWS, such as Microsoft Azure or Google Cloud Platform, to showcase versatility.
                    - Strengthen Soft Skills:
                    Leadership and project management skills are highly valued; consider leading more projects or taking courses in Agile and Scrum methodologies.
                    """

                    response = get_gemini_response(prompt3)
                st.subheader("Skills Improvement Suggestions")
                st.write(response)
            else:
                st.error("No job description provided.")
        else:
            st.error("No job description provided.")
            st.error("Resume Not Uploaded.")
    else:
        st.error("No Job Role Specified")
        st.error("No job description provided.")
        st.error("Resume Not Uploaded.")

if submit4:
    if len(role) > 0:
        if uploaded_file is not None:
            text = input_pdf_text(uploaded_file)
            if len(jd) > 0:
                with st.spinner('Please Wait..'):
                    prompt4 = f"""
                    You are a professional and experienced ATS(Application Tracking System) with a deep understanding of {role} fields. Review the resume's bullet points in light of the job description. Provide targeted suggestions on how to edit existing bullet points to better align with the job requirements. Focus on enhancing clarity, relevance, and impact by incorporating keywords from the JD and emphasizing achievements and skills that are most pertinent to the job.
                    
                    Here is the resume content : {text}
                    Here is the job description : {jd}
                    Your Response Should have the following structure
                    Example:
                    
                    Note: Only Mention and Analyze the content of the provided resume text. Make sure Nothing additional is added outside the provided text 
                    
                    Resume Customization Tips for Better Alignment with Job Description:

                    Tailor Bullet Points:
                    - Current: "Developed a web application using React and Node.js."
                    - Revised: "Engineered a scalable web application using React and Node.js, incorporating microservices architecture to enhance modularity and deployability, directly supporting team objectives in agile development environments."
                    
                    Highlight Specific Achievements:
                    - Current: "Designed cloud infrastructure for various projects."
                    - Revised: "Strategically designed and deployed robust cloud infrastructure on AWS for 3 enterprise-level projects, achieving a 20% improvement in deployment efficiency and cost reduction."
                    
                    Incorporate Missing Keywords:
                    If you have experience with Machine Learning, add a bullet point like: "Implemented machine learning    algorithms to automate data processing tasks, resulting in a 30% reduction in processing times."
                    """

                    response = get_gemini_response(prompt4)
                st.subheader("Customization Tips")
                st.write(response)
            else:
                st.error("No job description provided.")
        else:
            st.error("No job description provided.")
            st.error("Resume Not Uploaded.")
    else:
        st.error("No Job Role Specified")
        st.error("No job description provided.")
        st.error("Resume Not Uploaded.")

if submit5:
    if len(role) > 0:
        if uploaded_file is not None:
            text = input_pdf_text(uploaded_file)
            if len(jd) > 0:
                with st.spinner('Please Wait..'):
                    prompt5 = f"""
                    You are a professional and experienced ATS(Application Tracking System) with a deep understanding of {role} fields. Analyze the provided resume and job description (JD). Generate a set of interview questions and suggested answers tailored to this specific context. The questions should be designed to explore the candidate's technical skills, experiences, and personal attributes relevant to the role, as described in the JD and evidenced in the resume. Provide 5 technical interview questions (1 easy question, 2 medium questions, 3 hard questions) focusing on the key skills and technologies mentioned in the JD and resume. The technical questions should sound specific and technical. Additionally, provide 5 HR interview questions (1 easy question, 2 medium questions, 3 hard questions) that probe into the candidate's behavioral traits, problem-solving abilities, and cultural fit for the organization. For each question, include a detailed sample answer that highlights how the candidate can effectively showcase their relevant skills, experiences, and achievements from their resume in response to the job requirements outlined in the JD."

                    Here is the resume content : {text}
                    Here is the job description : {jd}
                    Instructions for Response:

                    Technical Questions:
                    Create questions that are directly related to the technical skills and experiences mentioned in the JD and resume.
                    Ensure questions cover a range of difficulties (easy, medium, hard) and are relevant to real-world scenarios the candidate might face in the role.
                    
                    HR Questions:
                    Formulate questions that assess cultural fit, teamwork, leadership, and resilience.
                    Questions should invite responses that allow the candidate to demonstrate their problem-solving approach, adaptability, and growth mindset.
                    
                    Suggested Answers:
                    Provide comprehensive sample answers for each question, guiding the candidate on how to integrate their specific experiences and achievements from the resume.
                    Highlight how each answer can align with the expectations set forth in the JD, showcasing the candidate's suitability for the role.
                    
                    Your Response Should have the following structure
                    
                    Technical Interview Questions:
                    
                    Question1: (Question here)
                    
                    Answer1: (Answer here)
                    
                    Similarly all other questions.
                    
                    HR Interview Questions:
                    
                    Question1: (Question here)
                    
                    Answer1: (Answer here)
                    
                    Similarly all other questions.
                    """

                    response = get_gemini_response(prompt5)
                st.subheader("Interview Preperation Guide ")
                st.write("Here are some sample Technical and HR interview questions which will help you in answering different questions faced in the interviews.")
                st.write(response)
            else:
                st.error("No job description provided.")
        else:
            st.error("No job description provided.")
            st.error("Resume Not Uploaded.")
    else:
        st.error("No Job Role Specified")
        st.error("No job description provided.")
        st.error("Resume Not Uploaded.")
# --------------------------
# Footer
# --------------------------
st.markdown("""
<div class="footer">
    <hr>
    <p>Built with ❤️ by TE AI&DS B Students</p>
</div>
""", unsafe_allow_html=True)