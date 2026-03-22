import streamlit as st
import PyPDF2
from ai_engine import analyze_resume
from graph_engine import build_knowledge_graph

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Resume Pro", page_icon="📄", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stProgress > div > div > div > div { background-color: #6C63FF; }
    .metric-card { background-color: #262730; padding: 20px; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --- SIDEBAR AUTHENTICATION ---
with st.sidebar:
    st.title("🔐 Login / Setup")
    if not st.session_state.is_logged_in:
        name = st.text_input("Name")
        email = st.text_input("Email")
        api_key = st.text_input("Gemini API Key", type="password", help="Get this from Google AI Studio")

        if st.button("Save & Login"):
            if name and email and api_key:
                st.session_state.api_key = api_key
                st.session_state.name = name
                st.session_state.is_logged_in = True
                st.rerun()
            else:
                st.error("Please fill all fields.")
    else:
        st.success(f"Welcome back, {st.session_state.name}!")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

# --- MAIN APP UI ---
st.title("🚀 AI Resume Analyzer & ATS Scorer")
st.write(
    "Upload your resume, enter your target role, and let AI reveal your strengths, weaknesses, and map your skills!")

if not st.session_state.is_logged_in:
    st.warning("👈 Please login from the sidebar using your Gemini API Key to continue.")
    st.stop()

# --- INPUT SECTION ---
col1, col2 = st.columns([1, 1])
with col1:
    target_role = st.text_input("🎯 Target Job Title (e.g., Data Scientist, Software Engineer)")
with col2:
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

if uploaded_file is not None and target_role:
    if uploaded_file is not None and target_role:
        if st.button("Analyze Resume 🪄", use_container_width=True):
            with st.spinner("Extracting text and analyzing with Gemini 3 Flash Preview..."):
                # Extract PDF Text
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()

                # Call AI (Passing the API key directly to the new engine)
                result = analyze_resume(resume_text, target_role, st.session_state.api_key)

                if "error" in result:
                    st.error(f"Error connecting to AI: {result['error']}. Check your API Key.")
                else:
                    st.session_state.analysis_result = result

# --- RESULTS DASHBOARD ---
if st.session_state.analysis_result:
    res = st.session_state.analysis_result

    st.divider()

    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎯 Gap Analysis", "💡 Suggestions", "🕸️ Knowledge Graph"])

    # TAB 1: DASHBOARD
    with tab1:
        st.subheader("ATS Compatibility")
        score = res.get("ats_score", 0)
        st.progress(score / 100)
        st.markdown(
            f"<h2 style='text-align: center; color: {'#38B2AC' if score > 75 else '#FF6584'};'>{score}/100</h2>",
            unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.success("**✅ Matching Skills**")
            for skill in res.get("matching_skills", []):
                st.write(f"- {skill}")
        with col_b:
            st.error("**❌ Missing Skills (Learn these!)**")
            for skill in res.get("missing_skills", []):
                st.write(f"- {skill}")

    # TAB 2: GAP ANALYSIS
    with tab2:
        st.subheader("Where you are lacking")
        if len(res.get("missing_skills", [])) == 0:
            st.write("You are a perfect match!")
        else:
            st.write(f"To become a top-tier {target_role}, you need to bridge the gap in the following areas:")
            for skill in res.get("missing_skills", []):
                st.warning(f"⚠️ **{skill}**: Consider taking a short course or building a project around this.")

    # TAB 3: SUGGESTIONS
    with tab3:
        st.subheader("Actionable Improvements")
        for suggestion in res.get("suggestions", []):
            st.info(f"💡 {suggestion}")

    # TAB 4: KNOWLEDGE GRAPH
    with tab4:
        st.subheader("Your Professional Identity Map")
        st.write("Drag nodes around to interact with your professional profile.")
        build_knowledge_graph(res.get("graph_data", {}), res.get("candidate_name", "User"))