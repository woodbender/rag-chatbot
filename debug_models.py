"""Debug script to test all available Gemini embedding models."""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

# Test all available embedding models
test_models = [
    "gemini-embedding-001",
    "gemini-embedding-2",
    "gemini-embedding-2-preview",
]

print("--- Testing embedding models ---")
for model_name in test_models:
    try:
        resp = client.models.embed_content(
            model=model_name,
            contents="test text"
        )
        dims = len(resp.embeddings[0].values)
        print(f"  {model_name}: SUCCESS - {dims} dims")
    except Exception as e:
        print(f"  {model_name}: FAILED - {type(e).__name__}: {str(e)[:150]}")

# Also test batch embedding with gemini-embedding-001
print("\n--- Testing batch embedding with gemini-embedding-001 ---")
try:
    resp = client.models.embed_content(
        model="gemini-embedding-001",
        contents=["text one", "text two", "text three"]
    )
    print(f"  Batch SUCCESS - {len(resp.embeddings)} embeddings, {len(resp.embeddings[0].values)} dims each")
except Exception as e:
    print(f"  Batch FAILED - {type(e).__name__}: {str(e)[:150]}")