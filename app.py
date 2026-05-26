import json
import streamlit as st
import os
from google import genai
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
load_dotenv()

def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

questions = load_json("data/questions.json")
regulations = load_json("data/regulations.json")

def get_api_key():
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]
    return os.getenv("GOOGLE_API_KEY")

def get_llm_explanation(triggered_regulations, user_answers):
    if not triggered_regulations:
        return "No major regulations were identified based on your answers. However, expert review may still be needed."

    answer_summary = ""
    for q in questions:
        q_id = q["id"]
        answer = "Yes" if user_answers.get(q_id) else "No"
        answer_summary += f"- {q['question']}: {answer}\n"

    prompt = f"""
You are a regulatory assistant for digital health SMEs in Sweden.

The user answered these questions:

{answer_summary}

These regulations apply: {', '.join(triggered_regulations)}

IMPORTANT RULES:
- Respond in English only
- Use a professional but friendly tone
- Do not override the regulations listed above
- Mention all listed regulations naturally
- Keep it short, around 2-3 sentences
"""

    try:
        client = genai.Client(api_key=get_api_key())
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception:
        reg_list = ", ".join(triggered_regulations)
        return f"Based on your answers, review: {reg_list}"

if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
    st.session_state.answers = {}
    st.session_state.conversation = []
    st.session_state.followup_chat = []
    st.session_state.followup_input = ""
    st.session_state.show_results = False
    st.session_state.ai_summary = None
    st.session_state.triggered_regs = []
    st.session_state.show_welcome = True
    st.session_state.session_started = False
    st.session_state.show_about = False

col_title, col_reset, col_about = st.columns([6, 1, 1])

with col_title:
    st.title("💬 Digital Health Regulatory Chatbot")
    st.caption("Helping Swedish SMEs navigate digital health regulations")

with col_reset:
    st.write("")
    if st.button("🔄", help="Start Over - Reset all answers and begin new assessment"):
        for key in [
            "current_q_index", "answers", "conversation", "followup_chat",
            "followup_input", "show_results", "ai_summary", "triggered_regs",
            "show_welcome", "session_started"
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

with col_about:
    st.write("")
    if st.button("ℹ️", help="About this chatbot"):
        st.session_state.show_about = not st.session_state.show_about

if st.session_state.show_about:
    st.info(
        "**ℹ️ About this chatbot**\n\n"
        "• Helps identify EU and Swedish regulations for digital health products\n"
        "• Built with Google Gemini AI\n"
        "• ⚠️ Guidance only - Not legal advice\n\n"
        "*Click the ℹ️ button again to close this message*"
    )

st.info(
    "⚠️ **Guidance only** - Not legal advice. Do not enter patient data, personal data, or trade secrets."
)

if not st.session_state.session_started:
    with st.chat_message("assistant"):
        st.write(
            "👋 Hello! I'm your digital health regulatory assistant.\n\n"
            "I'll ask you a few questions about your product, then tell you "
            "which EU and Swedish regulations may apply.\n\n"
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start Assessment", use_container_width=True):
                st.session_state.session_started = True
                st.rerun()
    st.stop()

if not st.session_state.show_results and st.session_state.current_q_index > 0:
    progress = st.session_state.current_q_index / len(questions)
    st.progress(progress, text=f"Question {st.session_state.current_q_index} of {len(questions)}")

for msg in st.session_state.conversation:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if (
    st.session_state.show_welcome
    and not st.session_state.conversation
    and not st.session_state.show_results
    and st.session_state.session_started
):
    with st.chat_message("assistant"):
        st.write("Let's start with the first question!")
    st.session_state.show_welcome = False

if not st.session_state.show_results:
    if st.session_state.current_q_index < len(questions):
        current_q = questions[st.session_state.current_q_index]

        with st.chat_message("assistant"):
            st.write(current_q["question"])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Yes", key=f"yes_{current_q['id']}", use_container_width=True):
                    st.session_state.answers[current_q["id"]] = True
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": current_q["question"]
                    })
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": "Yes"
                    })
                    st.session_state.current_q_index += 1
                    st.rerun()

            with col2:
                if st.button("No", key=f"no_{current_q['id']}", use_container_width=True):
                    st.session_state.answers[current_q["id"]] = False
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": current_q["question"]
                    })
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": "No"
                    })
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

        st.markdown("### 📋 Regulatory Assessment")
        st.write(st.session_state.ai_summary)

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

    st.markdown("### 💬 Ask a question about your results")
    st.caption("Only ask questions related to the regulations shown above.")

    for msg in st.session_state.followup_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_question = st.text_input(
        "Ask a follow-up question:",
        placeholder="e.g. Why does GDPR apply to my product?",
        key="followup_input"
    )

    if st.button("Send question"):
        if user_question.strip() == "":
            st.warning("Please write a question first.")
        else:
            st.session_state.followup_chat.append({
                "role": "user",
                "content": user_question
            })

            conversation_text = ""
            for msg in st.session_state.followup_chat:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_text += f"{role}: {msg['content']}\n"

            prompt = f"""
You are a regulatory assistant for digital health products.

The user answered:
{st.session_state.answers}

The system identified these relevant regulations:
{', '.join(st.session_state.triggered_regs)}

Conversation so far:
{conversation_text}

Continue the conversation naturally and answer the latest user question.

IMPORTANT:
- Answer only based on the regulations listed above
- Do not introduce new regulations
- Explain in relation to the user's product and previous answers
- Give practical meaning: what the user should review or do next
- Keep the answer short, around 2-3 sentences
- This is guidance only, not legal advice
"""

            try:
                client = genai.Client(api_key=get_api_key())
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                ai_answer = response.text

                st.session_state.followup_chat.append({
                    "role": "assistant",
                    "content": ai_answer
                })

                st.session_state.followup_input = ""
                st.rerun()

            except Exception:
                st.warning("AI is temporarily busy. Please try again in a moment.")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🔄 Start New Assessment", use_container_width=True):
            for key in [
                "current_q_index", "answers", "conversation", "followup_chat",
                "followup_input", "show_results", "ai_summary",
                "triggered_regs", "show_welcome", "session_started"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
