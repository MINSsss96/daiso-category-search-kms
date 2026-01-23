
import sys
import os
import asyncio

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.logic.nlu_openai import analyze_text
    print("Import successful")
except ImportError as e:
    with open("verify_result.txt", "w") as f:
        f.write(f"Import Error: {e}")
    sys.exit(1)

async def main():
    try:
        query = "파란색 건전지"
        print(f"Testing query: {query}")
        response = await analyze_text(query)
        
        output = f"Intent: {response.intent}\nSlots: {response.slots}\nTokens: {response.token_usage}"
        print(output)
        
        with open("verify_result.txt", "w", encoding="utf-8") as f:
            f.write(output)
            
    except Exception as e:
        with open("verify_result.txt", "w") as f:
            f.write(f"Runtime Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
