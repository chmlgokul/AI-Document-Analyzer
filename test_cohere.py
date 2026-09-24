import os
import cohere
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("COHERE_API_KEY")

print("Key found:", bool(api_key))
print("Key length:", len(api_key) if api_key else 0)
print("Key prefix:", api_key[:8] if api_key else "NONE")

if not api_key:
    raise ValueError("COHERE_API_KEY not found in .env")

try:
    co = cohere.ClientV2(api_key=api_key)

    response = co.chat(
        model="command-a-plus-05-2026",
        messages=[
            {
                "role": "user",
                "content": "Explain what an AI Document Analyzer does in 3 simple points."
            }
        ]
    )

    print("\n--- COHERE RESPONSE ---")

    for content in response.message.content:
        if hasattr(content, "text"):
            print(content.text)

except Exception as e:
    print("\n--- COHERE ERROR ---")
    print(type(e).__name__)
    print(e)