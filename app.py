import streamlit as st
import PyPDF2
from ai_engine import analyze_resume, chat_with_resume
from graph_engine import build_knowledge_graph

# --- PAGE CONFIG ---
st.set_page_config(page_title="Resumax AI", page_icon="👀", layout="wide")

# --- PRODUCTION CSS INJECTION ---
st.markdown("""
<style>
    /* Global Spacing and Fonts */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #111827; font-family: 'Inter', sans-serif; }

    /* Custom Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover { 
        transform: translateY(-4px); 
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }

    .metric-value { 
        font-size: 2.8rem; 
        font-weight: 700; 
        color: #2563EB; 
        margin-bottom: 5px; 
    }

    .metric-label { 
        font-size: 0.9rem; 
        color: #6B7280; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
    }

    /* Styling Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 16px; 
        border-bottom: 1px solid #E5E7EB;
    }

    .stTabs [data-baseweb="tab"] { 
        height: 45px; 
        white-space: pre-wrap; 
        background-color: transparent; 
        border-radius: 6px 6px 0px 0px; 
        padding: 10px 16px;
        color: #6B7280;
    }

    .stTabs [aria-selected="true"] {
        color: #2563EB;
        border-bottom: 2px solid #2563EB;
        font-weight: 600;
    }

    /* Suggestion Buttons */
    div[data-testid="column"] button {
        width: 100%; 
        border-radius: 12px; 
        background-color: #FFFFFF; 
        color: #111827; 
        border: 1px solid #E5E7EB;
        transition: all 0.2s ease;
    }

    div[data-testid="column"] button:hover { 
        border-color: #2563EB; 
        color: #2563EB; 
        background-color: #F9FAFB;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "analysis_result" not in st.session_state: st.session_state.analysis_result = None
if "resume_text" not in st.session_state: st.session_state.resume_text = ""
if "chat_messages" not in st.session_state: st.session_state.chat_messages = []

# --- SIDEBAR AUTHENTICATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135679.png", width=80)
    st.title("Settings")
    if not st.session_state.is_logged_in:
        st.markdown("Enter your details to unlock AI features.")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        api_key = st.text_input("Gemini API Key", type="password")

        if st.button("Authenticate & Login", use_container_width=True):
            if name and email and api_key:
                st.session_state.api_key = api_key
                st.session_state.name = name
                st.session_state.is_logged_in = True
                st.rerun()
            else:
                st.error("Please fill all fields.")
    else:
        st.success(f"Logged in as **{st.session_state.name}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# --- HERO SECTION ---
st.markdown("<h1 style='text-align: center;'>Resumax</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #A0AEC0; font-size: 1.2rem;'>Transform your resume, boost your ATS score, and land your dream job.</p>",
    unsafe_allow_html=True)
st.write("---")

if not st.session_state.is_logged_in:
    st.info("Please authenticate in the sidebar to begin.")
    st.stop()

# --- INPUT SECTION ---
col1, col2 = st.columns([1, 1], gap="large")
with col1:
    target_role = st.text_input("Target Job Title", placeholder="e.g., Senior Data Scientist")
with col2:
    uploaded_file = st.file_uploader("📄 Upload your Resume (PDF)", type=["pdf"])

if uploaded_file and target_role:
    if st.button("Analyze Resume & Build Profile 🪄", type="primary", use_container_width=True):
        with st.spinner("Extracting data and running AI analysis..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            resume_text = "".join(page.extract_text() for page in pdf_reader.pages)
            st.session_state.resume_text = resume_text  # Save for chat

            result = analyze_resume(resume_text, target_role, st.session_state.api_key)

            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.session_state.analysis_result = result
                st.session_state.chat_messages = []  # Reset chat on new upload

# --- RESULTS DASHBOARD ---
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    st.write("---")

    # Modern Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Overview & Scoring", "Knowledge Graph", "Gap Analysis", "AI Career Coach"])

    # TAB 1: DASHBOARD
    with tab1:
        st.write("### Profile Overview")
        score = res.get("ats_score", 0)
        color = "#38B2AC" if score >= 75 else ("#ED8936" if score >= 50 else "#FF6584")

        # Custom Metric Card layout
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {color};">{score}%</div>
                <div class="metric-label">ATS Match Score</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(res.get("matching_skills", []))}</div>
                <div class="metric-label">Skills Matched</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #FF6584;">{len(res.get("missing_skills", []))}</div>
                <div class="metric-label">Crucial Skills Missing</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("✅ Strengths (Matched)")
            for skill in res.get("matching_skills", []):
                st.markdown(f"- **{skill}**")
        with col_b:
            st.subheader("⚠️ Weaknesses (Missing)")
            for skill in res.get("missing_skills", []):
                st.markdown(f"- {skill}")

        # TAB 2: KNOWLEDGE GRAPH
        with tab2:
            st.subheader("Interactive Professional Profile")
            st.markdown("Hover over nodes for details. Use the **+ / -** buttons on the bottom right to zoom.")
            with st.container(border=True):
                # We now pass `target_role` to the builder
                build_knowledge_graph(res.get("graph_data", {}), res.get("candidate_name", "User"), target_role)

    # TAB 3: GAP ANALYSIS & SUGGESTIONS
    with tab3:
        st.subheader("How to improve your resume")
        for suggestion in res.get("suggestions", []):
            st.info(f"🚀 **Action Item:** {suggestion}")

    # TAB 4: CHAT INTERFACE
    with tab4:
        st.subheader("Chat with your AI Career Coach")
        st.caption("Ask questions about your resume, ask it to write cover letters, or re-write bullet points.")

        # Pre-suggestions Chips
        st.write("**Suggested Questions:**")
        sug1, sug2, sug3 = st.columns(3)


        def set_chat_input(prompt):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.spinner("AI is typing..."):
                resp = chat_with_resume(prompt, st.session_state.resume_text, st.session_state.chat_messages[:-1],
                                        st.session_state.api_key)
                st.session_state.chat_messages.append({"role": "assistant", "content": resp})


        if sug1.button("How can I improve my ATS score?"): set_chat_input(
            "How can I improve my ATS score based on my current resume?")
        if sug2.button("Write a short summary for me"): set_chat_input(
            f"Write a 3-sentence professional summary for my resume targeting a {target_role} role.")
        if sug3.button("Rewrite my recent experience"): set_chat_input(
            "Rewrite my most recent job experience bullet points to sound more impactful and quantifiable.")

        st.divider()

        # Display Chat History
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Chat Input Bar
        if prompt := st.chat_input("Ask anything about your resume..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chat_with_resume(prompt, st.session_state.resume_text,
                                                st.session_state.chat_messages[:-1], st.session_state.api_key)
                    st.write(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})