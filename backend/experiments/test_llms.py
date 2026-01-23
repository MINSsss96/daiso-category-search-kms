import argparse
import torch
import time
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Model Mapping
MODELS = {
    "qwen": {
        "id": "Qwen/Qwen2.5-1.5B-Instruct", # Defaulting to lighter model for CPU safety
        "name": "Qwen 2.5 (1.5B) [Safe for CPU]"
    },
    "qwen-3b": {
        "id": "Qwen/Qwen2.5-3B-Instruct",
        "name": "Qwen 2.5 (3B)"
    },
    "qwen-7b": {
        "id": "Qwen/Qwen2.5-7B-Instruct",
        "name": "Qwen 2.5 (7B)"
    },
    "exaone": {
        "id": "LGAI-EXAONE/EXAONE-3.0-7.8B-Instruct",
        "name": "EXAONE 3.0 (7.8B)"
    },
    "gemma": {
        "id": "google/gemma-2-2b-it",
        "name": "Gemma 2 (2B)"
    }
}

def load_model(model_key, use_4bit=True):
    if model_key not in MODELS:
        print(f"❌ Unknown model: {model_key}")
        return None, None
        
    model_info = MODELS[model_key]
    model_id = model_info["id"]
    print(f"Loading {model_info['name']} ({model_id})...")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    
    # Quantization Config (Only for CUDA)
    quantization_config = None
    if use_4bit and device == "cuda":
        print("Using 4-bit Quantization (BitsAndBytes)...")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16
        )
    elif use_4bit and device == "cpu":
        print("⚠️  Warning: 4-bit quantization requires CUDA (GPU). Falling back to full precision on CPU.")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        
        # Load arguments
        load_args = {
            "trust_remote_code": True,
        }
        
        if device == "cuda":
            load_args["device_map"] = "auto"
            load_args["quantization_config"] = quantization_config
        else:
            # CPU Optimized loading
            load_args["device_map"] = "cpu"
            load_args["torch_dtype"] = torch.float32 # Explicitly use float32 for CPU stability
            
        # Load Model
        model = AutoModelForCausalLM.from_pretrained(model_id, **load_args)
        return tokenizer, model
        
    except ImportError as e:
        if "accelerate" in str(e):
            print("\n❌ Missing Dependency: 'accelerate'")
            print("Please run: pip install accelerate")
        else:
            print(f"❌ Import Error: {e}")
        return None, None
        
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        if "accelerate" in str(e):
             print("Tip: Use 'pip install accelerate' to fix this.")
        return None, None

def generate_response(tokenizer, model, prompt):
    print(f"\nExample Prompt: {prompt}")
    print("-" * 50)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    start_time = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9
        )
    end_time = time.time()
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Clean up the output (remove the prompt part if included)
    response_only = response[len(prompt):].strip()
    
    print(f"Generated Response ({end_time - start_time:.2f}s):")
    print(response_only)
    print("-" * 50)
    return response

def main():
    parser = argparse.ArgumentParser(description="Test Local LLMs")
    parser.add_argument("--model", type=str, choices=MODELS.keys(), default="qwen", help="Model to test")
    parser.add_argument("--no-4bit", action="store_true", help="Disable 4-bit quantization (Use full precision)")
    
    args = parser.parse_args()
    
    prompt = """
    다음 제품을 적절한 카테고리로 분류하고 JSON 형식으로 출력해줘.
    
    제품명: 다이소 욕실 미끄럼방지 매트 (그레이)
    카테고리: 욕실용품
    
    출력 형식: {"item": "제품명", "category": "카테고리", "material": "재질(추론)"}
    """
    
    tokenizer, model = load_model(args.model, use_4bit=not args.no_4bit)
    
    if model:
        generate_response(tokenizer, model, prompt)
    else:
        print("Failed to load model.")

if __name__ == "__main__":
    main()
