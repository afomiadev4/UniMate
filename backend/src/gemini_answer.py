import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from your .env file")

# Initialize Gemini
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.1-flash-lite"

FALLBACK_MESSAGE = (
    "I couldn't find a verified answer for that yet. "
    "I don't want to guess about university information."
)


def generate_answer(question, verified_information):

    if not verified_information:
        return FALLBACK_MESSAGE

    prompt = f"""
You are UniGuide AI, a helpful university student assistant.

Your job is to answer students' questions using ONLY
the verified university information provided below.

Rules:
1. Never invent university information.
2. Never guess dates, locations, or policies.
3. Only use the provided information.
4. Keep answers clear, natural, and friendly.
5. If the information does not answer the question,
   respond exactly with:

{FALLBACK_MESSAGE}

Student Question:
{question}

Verified University Information:
{verified_information}

Answer:
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.text:
            return FALLBACK_MESSAGE

        return response.text.strip()

    except Exception as error:
        print("Gemini API error:", error)
        return FALLBACK_MESSAGE


# ==========================================
# TEST GEMINI
# ==========================================

if __name__ == "__main__":

    question = "When do second-year students start?"

    information = """
Event: First Semester Classes Begin for Year II UG Students
Date: September 28, 2026
Source: AAU Academic Calendar 2026/27
Page: 1
"""

    answer = generate_answer(question, information)

    print("\nQUESTION:", question)
    print("\nANSWER:", answer)