# list_models.py
import os
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

for model in client.models.list():
    if "image" in model.name.lower() or "gemini" in model.name.lower():
        print(f"📌 {model.name}")
