import asyncio
import os
import uuid
from typing import List

from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types


from hermes_agent.tools import (
    route_with_biggest_delay_last_week,
    delay_stats_by_reason,
    warehouses_over_delivery,
    top3_warehouses_by_processing,
    monthly_avg_delay,
    predict_next_week_delay,
)



from hermes_agent.prompt import system_prompt
# app/session constants – nothing fancy
APP_NAME = "hermes_logistics_app"
USER_ID = "Alex" 


def _check_api_key() -> None:
    """
    Quick sanity check to make sure GOOGLE_API_KEY is set.
    ADK refuses to run without it, so we fail early.
    """
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "GOOGLE_API_KEY is missing. "
            "Add it to your env or .env file before running."
        )


# _check_api_key()


# Define the main agent. 
# Model: gemini-2.0-flash (fast + cheap = good for demos).
# Tools: all the logistics analytics stuff from tools.py
root_agent = LlmAgent(
    name="HermesLogisticsAgent",
    model="gemini-2.0-flash",
    instruction=system_prompt,
    tools=[
        route_with_biggest_delay_last_week,
        delay_stats_by_reason,
        warehouses_over_delivery,
        top3_warehouses_by_processing,
        monthly_avg_delay,
        predict_next_week_delay,
    ],
)

# local runner (basically our fake backend)
runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
session_service = runner.session_service


async def _run_once_async(user_message: str) -> str:
    """
    Runs a single-turn interaction with the agent.
    Creates a temp session, sends user's message, and collects the final text.
    """
    session_id = str(uuid.uuid4())

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    output_chunks: List[str] = []

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=user_message)],
        ),
    ):
        # grab the final response when it appears
        if getattr(event, "is_final_response", lambda: False)():
            if event.content and event.content.parts:
                part = event.content.parts[0]
                if hasattr(part, "text") and part.text:
                    output_chunks.append(part.text)

    if not output_chunks:
        # Hermes probably panicked
        return "Hermes wasn't able to come up with an answer this time."

    # cleaning up text because the model sometimes adds random whitespace
    return "\n".join(chunk.strip() for chunk in output_chunks if chunk.strip())


def run_hermes(user_message: str) -> str:
    """
    Sync wrapper because Streamlit doesn't like raw async here.
    """
    return asyncio.run(_run_once_async(user_message))
