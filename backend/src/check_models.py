import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("\nAVAILABLE GEMINI MODELS\n")

for model in client.models.list():
    print(model.name)