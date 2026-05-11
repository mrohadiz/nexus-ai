import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in .env")
        return

    print(f"Testing OpenRouter API Key: {api_key[:10]}...")
    
    payload = {
        "model": "google/gemma-4-31b-it:free",
        "messages": [{"role": "user", "content": "Hello, are you working?"}],
        "max_tokens": 50
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nexus-ai.local",
        "X-Title": "Nexus AI Test"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 402:
            print("\n!!! ACCOUNT HAS NO CREDITS !!!")
        elif response.status_code == 200:
            print("\nAPI is working fine.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_openrouter()
