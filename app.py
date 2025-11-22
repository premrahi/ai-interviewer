import streamlit as st
import os
from utils import get_ai_question, transcribe_audio, evaluate_interview, save_session
from streamlit_mic_recorder import mic_recorder
from dotenv import load_dotenv

load_dotenv()

# Page Config
st.set_page_config(page_title="AI Virtual Interviewer", layout="wide", page_icon="🎙️")

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # List of (Question, Answer) tuples
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "evaluation" not in st.session_state:
    st.session_state.evaluation = None

# Sidebar Configuration
with st.sidebar:
    try:
        st.image("assets/logo.jpg", width=150)
    except:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        
    st.title("Interview Settings")
    
    # Dark Mode Toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    # Hardcoded to Gemini
    api_provider = "Gemini"
    api_key = os.getenv("GOOGLE_API_KEY")
    
    st.info(f"Using **{api_provider}** AI Model")
    
    st.divider()
    
    job_profile = st.selectbox(
        "Select Job Profile",
        ["Software Engineer", "Data Scientist", "Product Manager", "Marketing Specialist", "HR Manager", 
         "Web Developer", "Quality Analyst", "Data Engineer"]
    )
    
    st.divider()
    
    if st.button("Start Interview", use_container_width=True):
        if not api_key:
            st.error(f"GOOGLE_API_KEY not found in .env file.")
        else:
            st.session_state.interview_active = True
            st.session_state.chat_history = []
            st.session_state.question_count = 0
            st.session_state.evaluation = None
            # Generate first question
            with st.spinner("🤖 AI is preparing your interview..."):
                q = get_ai_question(job_profile, [], api_key, api_provider)
                print(f"DEBUG: Generated Question: {q}") # Debug logging
                st.session_state.current_question = q
            st.rerun()

# Dynamic CSS based on Dark Mode
if dark_mode:
    # Dark Theme Colors
    bg_gradient = "#000000" # Pitch Black
    sidebar_bg = "#121212" # Very dark gray
    text_color = "#ffffff"
    card_bg = "#1e1e1e"
    user_msg_bg = "#1e3a8a" 
    user_border = "#3b82f6"
    assistant_msg_bg = "#2d2d2d"
    assistant_border = "#a855f7"
    header_color = "#ffffff"
    shadow = "rgba(255,255,255,0.05)"
else:
    # Light Theme Colors
    bg_gradient = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
    sidebar_bg = "#ffffff"
    text_color = "#000000"
    card_bg = "#ffffff"
    user_msg_bg = "#e3f2fd"
    user_border = "#2196f3"
    assistant_msg_bg = "#ffffff"
    assistant_border = "#673ab7"
    header_color = "#1a237e"
    shadow = "rgba(0,0,0,0.05)"

st.markdown(f"""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {text_color};
    }}

    /* Gradient Background */
    .stApp {{
        background: {bg_gradient};
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid rgba(0,0,0,0.1);
    }}
    
    /* Card-like containers */
    .chat-message {{
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px {shadow};
        background-color: {card_bg};
        color: {text_color};
    }}
    .user-message {{
        background-color: {user_msg_bg};
        border-left: 5px solid {user_border};
    }}
    .assistant-message {{
        background-color: {assistant_msg_bg};
        border-left: 5px solid {assistant_border};
    }}
    
    /* Custom Card Class for non-chat items */
    .custom-card {{
        background-color: {card_bg};
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px {shadow};
        color: {text_color};
    }}

    /* Button Styling */
    .stButton button {{
        background: linear-gradient(90deg, #673ab7 0%, #512da8 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}

    /* Headers */
    h1, h2, h3 {{
        color: {header_color} !important;
        font-weight: 700;
    }}
    
    /* Progress Bar */
    .stProgress > div > div > div > div {{
        background-color: #673ab7;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {card_bg};
        color: {text_color};
    }}
</style>
""", unsafe_allow_html=True)

# Main Interface
st.title("🎙️ AI Virtual Interviewer")
st.markdown("#### Master your interview skills with real-time AI feedback")

if st.session_state.evaluation:
    st.balloons()
    st.success("Interview Completed Successfully!")
    
    st.markdown("### 📝 Comprehensive Evaluation Report")
    st.markdown(f"""
    <div class="custom-card">
        {st.session_state.evaluation}
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("View Full Transcript"):
        for i, (q, a) in enumerate(st.session_state.chat_history):
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 AI (Q{i+1}):</strong><br>{q}
            </div>
            <div class="chat-message user-message">
                <strong>👤 You:</strong><br>{a}
            </div>
            """, unsafe_allow_html=True)
            
    if st.button("Start New Interview"):
        st.session_state.interview_active = False
        st.session_state.evaluation = None
        st.rerun()

elif st.session_state.interview_active:
    # Progress
    progress = st.session_state.question_count / 7
    st.progress(progress, text=f"Question {st.session_state.question_count + 1} of 7")
    
    # Display Question
    st.markdown(f"""
    <div class="chat-message assistant-message">
        <h3>🤖 Question {st.session_state.question_count + 1}</h3>
        <p style="font-size: 1.2rem;">{st.session_state.current_question}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("### 🎤 Record your answer")
    
    # Audio Recording
    c1, c2 = st.columns([1, 3])
    with c1:
        audio = mic_recorder(
            start_prompt="Start Recording",
            stop_prompt="Stop Recording", 
            key='recorder'
        )
    
    if audio:
        st.audio(audio['bytes'])
        
        if st.button("Submit Answer", type="primary"):
            with st.spinner("Transcribing audio..."):
                text = transcribe_audio(audio['bytes'], api_key=api_key)
            
            st.success("Response recorded!")
            st.markdown(f"**You said:** _{text}_")
            
            # Save to history
            st.session_state.chat_history.append((st.session_state.current_question, text))
            st.session_state.question_count += 1
            
            # Check if interview is done
            if st.session_state.question_count >= 7:
                with st.spinner("🧠 Analyzing your responses and generating report..."):
                    report = evaluate_interview(job_profile, st.session_state.chat_history, api_key, api_provider)
                    st.session_state.evaluation = report
                    save_session(job_profile, st.session_state.chat_history, report)
                st.rerun()
            else:
                # Generate next question
                with st.spinner("🤔 Thinking of the next question..."):
                    next_q = get_ai_question(job_profile, st.session_state.chat_history, api_key, api_provider)
                    st.session_state.current_question = next_q
                st.rerun()

else:
    # Hero Section with Image
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
        <div class="custom-card">
            <h2>👋 Welcome to your AI Interview Prep</h2>
            <p style="opacity: 0.8; font-size: 1.1rem;">
                Select your target role from the sidebar and start practicing. 
                Our AI will ask you relevant questions, listen to your answers, and provide detailed feedback.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        try:
            st.image("assets/hero.jpg", use_container_width=True)
        except:
            pass
    
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🎯 Role Specific")
        st.write("Questions tailored to your selected job profile.")
    with c2:
        st.markdown("### 🗣️ Voice Interaction")
        st.write("Speak naturally, just like a real interview.")
    with c3:
        st.markdown("### 📊 Detailed Feedback")
        st.write("Get scored on content, clarity, and confidence.")
