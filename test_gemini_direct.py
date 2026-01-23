"""
Standalone script to test Gemini API directly (FIXED - synchronous version).
Run: python test_gemini_direct.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key: {api_key[:10]}..." if api_key else "NO API KEY FOUND")
    
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in .env")
        return
    
    # Configure with REST transport
    genai.configure(api_key=api_key, transport="rest")
    
    # Use gemini-2.0-flash
    model_name = "gemini-2.0-flash"
    print(f"Using model: {model_name}")
    
    model = genai.GenerativeModel(model_name=model_name)
    
    prompt = "Say 'Hello World' in Korean"
    print(f"Sending prompt: {prompt}")
    print("Waiting for response...")
    
    try:
        # Use synchronous generate_content (NOT async)
        response = model.generate_content(prompt)
        print(f"SUCCESS! Response: {response.text}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_gemini()
