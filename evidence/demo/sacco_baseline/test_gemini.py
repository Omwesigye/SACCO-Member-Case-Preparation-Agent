import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("GEMINI_API_KEY not found.")
    exit()


client = genai.Client(api_key=api_key)


interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain what a SACCO is in one short paragraph."
)


print(interaction.output_text)