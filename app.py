import os
from utils import set_logger
import streamlit as st
from dotenv import load_dotenv

from hermes_agent.agent import run_hermes

load_dotenv()
logger = set_logger()


def ensure_api_key():
    """
    Display an error on the UI if the API key is missing.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error(
            "GOOGLE_API_KEY is not configured.\n"
            "Create a `.env` file in the project root and add:\n\n"
            '`GOOGLE_API_KEY="YOUR_API_KEY"`'
        )
        logger.error("Missing GOOGLE_API_KEY – cannot start Hermes UI.")
        st.stop()


def main():
    st.set_page_config(
        page_title="Hermes Logistics Assistant",
        page_icon="📦",
        layout="wide",
    )

    ensure_api_key()

    st.title("📦 Hermes – Logistics AI Assistant")
    st.markdown(
        "Ask Hermes, e.g.:\n"
        "- `Route with most delays last week`\n"
        "- `Top 3 slowest warehouses`\n"
        "- `Next week's delay forecast`\n"
        "- `Delay count by reason`\n"
        "- `Warehouses with delivery time > 5 days`"
    )


    # store UI chat only (not tied to ADK sessions)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    user_input = st.chat_input("Enter your logistics question...")

    if user_input:
        # log user message
        logger.info(f"User asked: {user_input}")

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Hermes is analyzing your request..."):
                reply = run_hermes(user_input)
                st.markdown(reply)

        # log Hermes response
        logger.info(f"Hermes replied: {reply}")

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )


if __name__ == "__main__":
    main()
