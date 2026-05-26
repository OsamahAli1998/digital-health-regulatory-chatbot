import json
import streamlit as st
import os
from dotenv import load_dotenv
from logic.decision_engine import evaluate_regulations

st.set_page_config(
    page_title="Digital Health Regulatory Chatbot",
    page_icon="💬",
    layout="centered"
)

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("style.css not found")

load_css()

# Load API key from .env file
load_dotenv()


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


questions = load_json("data/questions.json")
regulations = load_json("data/regulations.json")

# Function to get LLM explanation using Google Gemini 
def get_llm_explanation(triggered_regulations, user_answers):
    if not triggered_regulations:
        return "No major regulations were identified based on your answers. However, expert review may still be needed."
    
    # Build answer summary
    answer_summary = ""
    for q in questions:
        q_id = q["id"]
        answer = "Yes" if user_answers.get(q_id) else "No"
        answer_summary += f"- {q['question']}: {answer}\n"
    
    prompt = f"""
You are a regulatory assistant for digital health SMEs in Sweden.

The user answered these questions:

{answer_summary}

These regulations DO apply: {', '.join(triggered_regulations)}

IMPORTANT RULES:
- Respond in ENGLISH only
- Use professional but friendly tone
- The regulations listed above DEFINITELY apply. Do NOT question or override this.
- Mention all regulations naturally in a sentence, not as a list
- Do NOT repeat what's in the detailed view

Write a short, friendly explanation (2-3 sentences) telling the user:
1. Which regulations apply and why (list ALL of them)
2. What they should do next

Keep it simple, be conversational and friendly
"""
    
    try:
        # Create client inside the function
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
           model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text
    except Exception as e:
        reg_list = ", ".join(triggered_regulations) if triggered_regulations else "no specific regulations"
        return f"Based on your answers, review: {reg_list}"


# Initialize session state
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
    st.session_state.answers = {}
    st.session_state.conversation = []
    st.session_state.show_results = False
    st.session_state.ai_summary = None
    st.session_state.triggered_regs = []
    st.session_state.show_welcome = True
    st.session_state.session_started = False 
    st.session_state.show_about = False


# TOP BAR MENU 
col_title, col_reset, col_about = st.columns([6, 1, 1])

with col_title:
    st.title("💬 Digital Health Regulatory Chatbot")
    st.caption("Helping Swedish SMEs navigate digital health regulations")

with col_reset:
    st.write("")  
    if st.button("🔄", help="Start Over - Reset all answers and begin new assessment"):
        for key in ["current_q_index", "answers", "conversation", "show_results", "ai_summary", "triggered_regs", "show_welcome", "session_started"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

with col_about:
    st.write("")  
    if st.button("ℹ️", help="About this chatbot"):
        st.session_state.show_about = not st.session_state.show_about

# Show about information 
if st.session_state.show_about:
    st.info(
        "**ℹ️ About this chatbot**\n\n"
        "• Helps identify EU and Swedish regulations for digital health products\n"
        "• Built with Google Gemini 2.5 Flash-Lite\n"
        "• ⚠️ Guidance only - Not legal advice\n\n"
        "*Click the ℹ️ button again to close this message*"
    )

# Information banner
st.info(
    "⚠️ **Guidance only** - Not legal advice. Do not enter patient data, personal data, or trade secrets."
)

# Welcome message with Start button
if not st.session_state.session_started:
    with st.chat_message("assistant"):
        st.write(
            "👋 Hello! I'm your digital health regulatory assistant.\n\n"
            "I'll ask you a few questions about your product, then tell you "
            "which EU and Swedish regulations may apply.\n\n"
        )
        # Start button centered
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start Assessment", use_container_width=True):
                st.session_state.session_started = True
                st.rerun()
    
    st.stop()

# Conversation area
if not st.session_state.show_results and st.session_state.current_q_index > 0:
    progress = st.session_state.current_q_index / len(questions)
    st.progress(progress, text=f"Question {st.session_state.current_q_index} of {len(questions)}")

# Display conversation history
for msg in st.session_state.conversation:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Welcome message 
if st.session_state.show_welcome and not st.session_state.conversation and not st.session_state.show_results and st.session_state.session_started:
    with st.chat_message("assistant"):
        st.write("Let's start with the first question!")
    st.session_state.show_welcome = False

# Main chatbot logic
if not st.session_state.show_results:
    if st.session_state.current_q_index < len(questions):
        current_q = questions[st.session_state.current_q_index]
        
        # Show current question
        with st.chat_message("assistant"):
            st.write(current_q["question"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes", key=f"yes_{current_q['id']}", use_container_width=True):
                    st.session_state.answers[current_q["id"]] = True
                    st.session_state.conversation.append({"role": "assistant", "content": current_q["question"]})
                    st.session_state.conversation.append({"role": "user", "content": " Yes"})
                    st.session_state.current_q_index += 1
                    st.rerun()
            with col2:
                if st.button(" No", key=f"no_{current_q['id']}", use_container_width=True):
                    st.session_state.answers[current_q["id"]] = False
                    st.session_state.conversation.append({"role": "assistant", "content": current_q["question"]})
                    st.session_state.conversation.append({"role": "user", "content": " No"})
                    st.session_state.current_q_index += 1
                    st.rerun()
    else:
        st.session_state.show_results = True
        st.rerun()
else:
    with st.chat_message("assistant"):
        if st.session_state.ai_summary is None:
            with st.spinner("📋 Analyzing your responses..."):
                st.session_state.triggered_regs = evaluate_regulations(st.session_state.answers)
                st.session_state.ai_summary = get_llm_explanation(
                    st.session_state.triggered_regs, 
                    st.session_state.answers
                )
        
        # Display AI summary
        st.markdown("### 📋 Regulatory Assessment")
        st.write(st.session_state.ai_summary)
        
        # Detailed regulations in expander
        if st.session_state.triggered_regs:
            with st.expander("🔍 View detailed regulation information", expanded=False):
                for reg_id in st.session_state.triggered_regs:
                    reg = regulations[reg_id]
                    st.markdown(f"**📜 {reg['name']}**")
                    st.write(f"*Why:* {reg['why']}")
                    st.write(f"*Next steps:* {reg['next_steps']}")
                    st.divider()
        else:
            st.info("No major regulations were triggered based on your answers.")
    
    # Start over button 
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Start New Assessment", use_container_width=True):
            for key in ["current_q_index", "answers", "conversation", "show_results", "ai_summary", "triggered_regs", "show_welcome", "session_started"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # 🔵 Optional AI follow-up question
st.markdown("### 💬 Ask a follow-up question")

user_question = st.text_area(
    "Ask a question about the regulations shown above:",
    placeholder="e.g. What does GDPR mean for my product?"
)

if st.button("Get AI explanation"):
    if user_question.strip() == "":
        st.warning("Please write a question first.")
    else:
        # Build safe prompt
        prompt = f"""
You are a regulatory assistant.

The user already received these regulations:
{', '.join(st.session_state.triggered_regs)}

User question:
{user_question}

IMPORTANT:
- Only answer questions related to these regulations
- Do NOT introduce new regulations
- Keep answer short and clear (2-3 sentences)
"""

        try:
            client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            st.write(response.text)
        except:
            st.write("Could not generate response. Please try again.")
