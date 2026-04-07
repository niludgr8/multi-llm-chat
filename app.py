"""Production-ready Streamlit interface for the Multi-LLM chat application."""

from __future__ import annotations

import csv
import io
import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "Multi-LLM Chat") or "Multi-LLM Chat"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from firebase_service import FirebaseAuth, FirebaseDB, initialize_firebase
from llm_functions import DEFAULT_SYSTEM_PROMPT, get_openai_response2, get_response_from_groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT
MAX_QUERY_LENGTH = 5000


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Read environment variables first, then fall back to Streamlit secrets."""
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    try:
        return st.secrets[key]
    except Exception:
        return default

st.markdown(
    """
    <style>
        .main {padding: 2rem;}
        .stButton>button {width: 100%; padding: 0.5rem;}
        .block-container {padding-top: 1.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_database_client() -> Any:
    """Cache the Firebase client across Streamlit reruns."""
    return initialize_firebase()


def initialize_session_state() -> None:
    """Ensure all session state keys exist before the app renders."""
    defaults: Dict[str, Any] = {
        "logged_in": False,
        "user_id": None,
        "user_email": None,
        "user_name": None,
        "chat_history": [],
        "show_signup": False,
        "groq_chat_history": [],
        "openai2_chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def extract_groq_response(message: Dict[str, Any]) -> str:
    """Return the Groq response from current or legacy Firestore records."""
    return str(message.get("groq_response") or message.get("openai_response") or "")


def extract_openai_response(message: Dict[str, Any]) -> str:
    """Return the OpenAI response from current or legacy Firestore records."""
    if message.get("groq_response") is not None:
        return str(message.get("openai_response") or "")
    return str(message.get("gemini_response") or "")


def sync_model_histories() -> None:
    """Rebuild per-model histories from persisted chat history."""
    st.session_state.groq_chat_history = []
    st.session_state.openai2_chat_history = []

    for msg in st.session_state.chat_history:
        user_text = msg.get("user_query")
        groq_text = extract_groq_response(msg)
        openai_text = extract_openai_response(msg)

        if user_text and groq_text:
            st.session_state.groq_chat_history.extend(
                [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": groq_text},
                ]
            )

        if user_text and openai_text:
            st.session_state.openai2_chat_history.extend(
                [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": openai_text},
                ]
            )


def login_user(email: str, password: str) -> bool:
    """Authenticate a user with Firebase and load their chat history."""
    try:
        if not email or not password:
            st.error("Email and password are required.")
            return False

        auth_result = FirebaseAuth.verify_email(email, password)
        if not auth_result.get("success"):
            st.error(auth_result.get("message", "Invalid email or password."))
            return False

        user_id = auth_result.get("user_id")
        user_info = FirebaseAuth.get_user_by_id(user_id) if user_id else None
        display_name = (user_info or {}).get("display_name") or email.split("@")[0]

        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.user_email = email
        st.session_state.user_name = display_name

        if get_database_client() is None:
            st.warning("Firebase is not connected. Chat history will not be saved yet.")
            st.session_state.chat_history = []
        else:
            st.session_state.chat_history = FirebaseDB.get_user_chat_history(user_id)

        sync_model_histories()
        logger.info("User logged in successfully: %s", email)
        st.success(f"Welcome back, {display_name}!")
        return True
    except Exception as exc:
        logger.exception("Login error for %s: %s", email, exc)
        st.error("Login failed. Please try again or contact support.")
        return False


def signup_user(email: str, password: str, name: str) -> bool:
    """Create a new Firebase user account and profile document."""
    try:
        if not all([email, password, name]):
            st.error("All fields are required.")
            return False
        if len(password) < 6:
            st.error("Password must be at least 6 characters.")
            return False

        result = FirebaseAuth.sign_up(email, password, name)
        if not result.get("success"):
            st.error(result.get("message", "Sign-up failed. Please try again."))
            return False

        user_id = result.get("user_id")
        if user_id and get_database_client() is not None:
            FirebaseDB.create_user(user_id, email, name)

        logger.info("User account created for %s", email)
        st.success("Account created successfully! Please log in.")
        st.session_state.show_signup = False
        return True
    except Exception as exc:
        logger.exception("Signup error for %s: %s", email, exc)
        st.error("Sign-up failed. Please try again or contact support.")
        return False


def logout_user() -> None:
    """Clear the current Streamlit session and log the user out."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.chat_history = []
    st.session_state.groq_chat_history = []
    st.session_state.openai2_chat_history = []
    logger.info("User logged out.")
    st.success("Logged out successfully!")


def is_error_response(response: str) -> bool:
    """Detect user-facing error strings returned by provider helper functions."""
    normalized = response.lower().strip()
    return normalized.startswith("error:") or "temporarily unavailable" in normalized or "timed out" in normalized


def get_api_response(api_name: str, request_fn: Callable[[], str]) -> str:
    """Execute a provider call and surface a friendly warning when it fails."""
    response = request_fn()
    if is_error_response(response):
        logger.warning("%s request returned an error response: %s", api_name, response)
        st.warning(f"{api_name} is temporarily unavailable after multiple attempts. Please try again shortly.")
    return response


def build_chat_csv(chat_history: List[Dict[str, Any]]) -> bytes:
    """Serialize chat history to CSV bytes without requiring pandas."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["timestamp", "user_query", "groq_response", "openai_response", "user_choice"],
    )
    writer.writeheader()
    for message in chat_history:
        writer.writerow(
            {
                "timestamp": message.get("timestamp", ""),
                "user_query": message.get("user_query", ""),
                "groq_response": extract_groq_response(message),
                "openai_response": extract_openai_response(message),
                "user_choice": message.get("user_choice", ""),
            }
        )
    return output.getvalue().encode("utf-8")


def display_chat_history(llm_choice: int) -> None:
    """Render the most recent chat messages in the main content area."""
    if not st.session_state.chat_history:
        st.info("No chat history yet. Start a conversation!")
        return

    st.subheader("Chat History")
    for msg in st.session_state.chat_history[-10:]:
        groq_text = extract_groq_response(msg)
        openai_text = extract_openai_response(msg)
        st.write(f"**You:** {msg.get('user_query', '')}")

        if llm_choice == 3:
            col_left, col_right = st.columns(2)
            with col_left:
                st.info(f"**🤖 Groq:**\n\n{groq_text or 'No response'}")
            with col_right:
                st.info(f"**🟢 GPT-4o-mini:**\n\n{openai_text or 'No response'}")
        elif llm_choice == 1:
            st.info(f"**🤖 Groq:** {groq_text or 'No response'}")
        else:
            st.info(f"**🟢 GPT-4o-mini:** {openai_text or 'No response'}")
        st.divider()


def process_user_message(user_query: str, llm_choice: int) -> None:
    """Send the user message to the selected model(s), persist the result, and refresh the UI."""
    if len(user_query) > MAX_QUERY_LENGTH:
        st.error(f"Query too long. Maximum {MAX_QUERY_LENGTH} characters allowed.")
        return

    with st.spinner("🤖 Thinking..."):
        try:
            groq_response = ""
            openai_response = ""

            if llm_choice in (1, 3):
                groq_response = get_api_response(
                    "Groq",
                    lambda: get_response_from_groq(
                        user_query,
                        st.session_state.groq_chat_history,
                        SYSTEM_PROMPT,
                    ),
                )
            if llm_choice in (2, 3):
                openai_response = get_api_response(
                    "OpenAI",
                    lambda: get_openai_response2(
                        user_query,
                        st.session_state.openai2_chat_history,
                        SYSTEM_PROMPT,
                    ),
                )

            payload = {
                "user_query": user_query,
                "groq_response": groq_response,
                "openai_response": openai_response,
                "gemini_response": openai_response,
                "user_choice": llm_choice,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            if get_database_client() is not None and st.session_state.user_id:
                FirebaseDB.save_chat_message(
                    user_id=st.session_state.user_id,
                    user_query=user_query,
                    groq_response=groq_response,
                    openai_response=openai_response,
                    choice=llm_choice,
                    openai_rating=0 if llm_choice in (2, 3) else None,
                    gemini_rating=0 if llm_choice in (2, 3) else None,
                )
                st.session_state.chat_history = FirebaseDB.get_user_chat_history(st.session_state.user_id)
            else:
                st.session_state.chat_history.append(payload)
                st.warning("Firebase is not connected. This message is stored only in the current session.")

            sync_model_histories()
            logger.info("Processed message for user %s", st.session_state.user_email)
            st.success("Message processed successfully.")
            st.rerun()
        except Exception as exc:
            logger.exception("Message processing error: %s", exc)
            st.error("An error occurred while processing your message. Please try again.")


def display_chat_interface() -> None:
    """Render the main authenticated chat interface."""
    st.header(f"💬 {APP_TITLE} — Welcome, {st.session_state.user_name}!")

    with st.sidebar:
        st.subheader("Chat Options")
        st.write(f"**Logged in as:** {st.session_state.user_email}")

        llm_choice = st.radio(
            "Select which LLM to use:",
            [1, 2, 3],
            format_func=lambda x: {1: "🤖 Groq Only", 2: "🟢 GPT-4o-mini", 3: "🔄 Both (Compare)"}[x],
        )

        if st.button("📊 View Chat Statistics"):
            if get_database_client() is None or not st.session_state.user_id:
                st.warning("Chat statistics are unavailable until Firebase is configured.")
            else:
                stats = FirebaseDB.get_chat_statistics(st.session_state.user_id)
                groq_turns = sum(1 for msg in st.session_state.chat_history if extract_groq_response(msg))
                openai_turns = sum(1 for msg in st.session_state.chat_history if extract_openai_response(msg))
                st.write(f"**Total Messages:** {stats['total_messages']}")
                st.write(f"**🤖 Groq turns:** {groq_turns}")
                st.write(f"**🟢 GPT-4o-mini turns:** {openai_turns}")
                if stats["last_interaction"]:
                    st.write(f"**Last Interaction:** {stats['last_interaction']}")

        if st.button("🧹 Clear Chat History"):
            if get_database_client() is not None and st.session_state.user_id:
                if FirebaseDB.clear_user_chat_history(st.session_state.user_id):
                    st.session_state.chat_history = []
                    sync_model_histories()
                    st.success("Chat history cleared!")
            else:
                st.session_state.chat_history = []
                sync_model_histories()
                st.success("Local chat history cleared!")

        if st.button("🚪 Logout"):
            logout_user()
            st.rerun()

    display_chat_history(llm_choice)

    st.subheader("New Message")
    col1, col2 = st.columns([4, 1])
    with col1:
        user_query = st.text_input("Type your question here:", key="user_input")
    with col2:
        send_button = st.button("Send 📤", type="primary")

    st.download_button(
        label="⬇️ Download Chat History as CSV",
        data=build_chat_csv(st.session_state.chat_history),
        file_name="chat_history.csv",
        mime="text/csv",
        disabled=not st.session_state.chat_history,
    )

    if send_button and user_query:
        process_user_message(user_query, llm_choice)


def display_auth_page() -> None:
    """Render the sign-up and login forms."""
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.title(f"🔐 {APP_TITLE}")
        st.write("---")

        if st.session_state.show_signup:
            st.subheader("Create Account")
            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="john@example.com")
                password = st.text_input("Password", type="password", placeholder="At least 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit_button = st.form_submit_button("Create Account", use_container_width=True)

                if submit_button:
                    if not all([name, email, password, confirm_password]):
                        st.error("Please fill in all fields.")
                    elif password != confirm_password:
                        st.error("Passwords do not match.")
                    elif signup_user(email, password, name):
                        st.session_state.show_signup = False

            if st.button("Back to Login"):
                st.session_state.show_signup = False
                st.rerun()
        else:
            st.subheader("Login to Your Account")
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login", use_container_width=True)

                if submit_button:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    elif login_user(email, password):
                        st.rerun()

            st.write("---")
            if st.button("Don't have an account? Sign Up", use_container_width=True):
                st.session_state.show_signup = True
                st.rerun()


def main() -> None:
    """Render the Streamlit application and surface any unexpected errors safely."""
    try:
        initialize_session_state()
        if st.session_state.logged_in:
            display_chat_interface()
        else:
            display_auth_page()
    except Exception as exc:
        logger.exception("Unhandled application error: %s", exc)
        st.markdown(
            """
            <div style="padding: 1rem; border-radius: 0.75rem; background: #3b0d0d; color: #ffffff;">
                <strong>Something went wrong.</strong><br>
                Please refresh the page and try again. The error has been logged.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.error("A system error occurred while loading the application.")


if __name__ == "__main__":
    main()

