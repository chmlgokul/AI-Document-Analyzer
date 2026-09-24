import os

from dotenv import load_dotenv
import cohere


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# READ COHERE API KEY
# =========================================================

API_KEY = os.getenv("COHERE_API_KEY")


# =========================================================
# TEST COHERE CONNECTION
# =========================================================

def test_cohere_api():

    assert API_KEY, "COHERE_API_KEY not found in .env"

    client = cohere.ClientV2(
        api_key=API_KEY
    )

    response = client.chat(
        model="command-a-plus-05-2026",
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Cohere API test successful"
            }
        ]
    )

    assert response is not None

    print("\nCohere API response received successfully.")


# =========================================================
# OPTIONAL MANUAL CHECK
# =========================================================

if __name__ == "__main__":

    if not API_KEY:

        print("COHERE_API_KEY not found in .env")

    else:

        client = cohere.ClientV2(
            api_key=API_KEY
        )

        response = client.chat(
            model="command-a-plus-05-2026",
            messages=[
                {
                    "role": "user",
                    "content": "Reply with exactly: Cohere API test successful"
                }
            ]
        )

        print("\nCohere test response:")
        print(response)