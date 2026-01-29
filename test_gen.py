import os
import google.generativeai as genai
from dotenv import load_dotenv

with open("test_output.txt", "w") as f:
    f.write("Starting...\n")

try:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    with open("test_output.txt", "a") as f:
        f.write(f"API Key present: {bool(api_key)}\n")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    with open("test_output.txt", "a") as f:
        f.write("Generating...\n")
        
    response = model.generate_content("Say hello")
    
    with open("test_output.txt", "a") as f:
        f.write(f"Response: {response.text}\n")
        
except Exception as e:
    with open("test_output.txt", "a") as f:
        f.write(f"Error: {e}\n")
