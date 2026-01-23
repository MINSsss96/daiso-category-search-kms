import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_available_models():
    """List available models that support generation"""
    print("Checking available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
        print("Please set your API key in .env file or environment.")
        print("Get key here: https://aistudio.google.com/app/apikey")
        return

    # Configure the library
    genai.configure(api_key=api_key)
    
    # List models to confirm connection and model names
    list_available_models()
    
    print("-" * 50)
    print("Testing Generation with 'gemini-2.0-flash-exp' (or similar available)...")
    
    # Try using a standard model name. 
    # Note: 'gemma-2' might be available via Vertex AI or specific endpoints, 
    # but 'gemini-pro' or 'gemini-1.5-flash' are standard for AI Studio.
    # We will try 'gemini-1.5-flash' as a fast/cheap proxy, or check if specific gemma checkpoints are listed.
    # Actually, for "Gemma 2 API" specifically via Google, it's often via Vertex AI or specific integrations.
    # But for general "Google AI Studio" usage, the Gemini models are the main offering.
    # If the user specifically wants "Gemma 2", we might need HuggingFace API.
    # However, let's assume they want the "Google AI Studio" experience which provides Gemini 
    # (which is often what people mean when they say "Google API").
    # *Correction*: The user explicitly asked for "Gemma 2 (2B) API".
    # Google AI Studio *does* support Gemma 2 open models in some contexts, but primarily it's Gemini.
    # Let's try to access 'google/gemma-2-2b-it' via Hugging Face API if Google AI Studio doesn't list it.
    # WAIT, the user prompt said: "Google AI Studio (free tier) OR Hugging Face Inference API".
    # Let's stick to Google AI Studio first as requested. 
    # If Google AI Studio only exposes Gemini, we can explain that.
    # Actually, Google's "Vertex AI" supports Gemma. "AI Studio" is mostly Gemini.
    # Let's try to use the `gemini-1.5-flash` as a fallback or check specifically for gemma.
    
    # Updated to use a model confirmed to be available from the user's list
    model_name = 'gemini-2.0-flash' 
    
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = """
        다음 제품을 적절한 카테고리로 분류하고 JSON 형식으로 출력해줘.

        제품명: 다이소 욕실 미끄럼방지 매트 (그레이)
        카테고리: 욕실용품

        출력 형식: {"item": "제품명", "category": "카테고리", "material": "재질(추론)"}
        """
        
        print(f"Prompt: {prompt.strip()}")
        print("-" * 50)
        
        response = model.generate_content(prompt)
        print("Generated Response:")
        print(response.text)
        print("-" * 50)
        print("✅ API Test Successful!")
        
    except Exception as e:
        print(f"❌ Generation Error: {e}")

if __name__ == "__main__":
    main()
