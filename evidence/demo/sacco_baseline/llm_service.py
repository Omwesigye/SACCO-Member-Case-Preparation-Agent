import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from prompts import SYSTEM_PROMPT


load_dotenv()


def get_client():
    """
    Create and return a Gemini API client.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY was not found. "
            "Add it to Streamlit Secrets or your .env file."
        )

    return genai.Client(api_key=api_key)


def prepare_case_with_ai(user_prompt):
    """
    Send the SACCO case information to Gemini
    and return the generated case brief.
    """

    client = get_client()

    # Combine our system instructions with the case.
    complete_prompt = f"""
{SYSTEM_PROMPT}


CURRENT SACCO CASE


{user_prompt}
"""

    interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=complete_prompt
)

    return interaction.output_text