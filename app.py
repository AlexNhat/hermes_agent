import os
import time
import uuid
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from utils import set_logger
from hermes_agent.agent import run_hermes
from db import init_db, insert_interaction

load_dotenv()
logger = set_logger()


def ensure_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error(
            "GOOGLE_API_KEY is missing.\n"
            "Create a `.env` file in the project root and add:\n\n"
            'GOOGLE_API_KEY="YOUR_API_KEY"'
        )
        logger.error("Missing GOOGLE_API_KEY – Hermes cannot start.")
        st.stop()


def main():
    st.set_page_config(
        page_title="Hermes Logistics Assistant",
        page_icon="📦",
        layout="wide",
    )

    ensure_api_key()
    init_db()

    st.title("📦 Hermes – Logistics AI Assistant")
    st.markdown(
        "Examples:\n"
        "- `Route with the most delays last week`\n"
        "- `Top 3 slowest warehouses`\n"
        "- `Next week's delay forecast`\n"
        "- `Delay count by reason`\n"
        "- `Warehouses with delivery time > 5 days`"
    )

    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Enter your logistics question...")

    if user_input:
        user_id = st.session_state.user_id
        user_ts = datetime.utcnow().isoformat()

        logger.info("User [%s] asked: %s", user_id, user_input)

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)

        start = time.perf_counter()
        with st.chat_message("assistant"):
            with st.spinner("Hermes is processing..."):
                reply = run_hermes(user_input)
                st.markdown(reply)
        end = time.perf_counter()

        assistant_ts = datetime.utcnow().isoformat()
        response_ms = (end - start) * 1000.0

        logger.info(
            "Hermes replied to [%s] in %.2f ms: %s",
            user_id,
            response_ms,
            reply,
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

        model_name = "Hermes/gemini-2.0-flash"
        insert_interaction(
            user_id=user_id,
            user_message=user_input,
            assistant_message=reply,
            user_timestamp=user_ts,
            assistant_timestamp=assistant_ts,
            response_time_ms=response_ms,
            model_name=model_name,
        )


if __name__ == "__main__":
    main()
