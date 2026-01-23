import sys
import os
import asyncio
import traceback

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("DEBUG: Starting test script...")
print(f"DEBUG: Current WD: {os.getcwd()}")
print(f"DEBUG: sys.path: {sys.path}")

try:
    from backend.logic.nlu import analyze_text, infer_product_keywords
    print("DEBUG: Successfully imported nlu module.")
except ImportError:
    print("ERROR: Failed to import nlu module.")
    traceback.print_exc()
    sys.exit(1)
except Exception:
    print("ERROR: Unexpected error during import.")
    traceback.print_exc()
    sys.exit(1)

async def test_nlu():
    print("\n--- Testing analyze_text ---")
    try:
        query = "건전지 어디에 있어요?"
        print(f"Input: {query}")
        result = await analyze_text(query)
        print(f"Result: {result}")
        print(f"Slots: {result.slots}")
    except Exception:
        print("ERROR in analyze_text:")
        traceback.print_exc()

    print("\n--- Testing infer_product_keywords ---")
    try:
        query = "멀티탭 코너는 몇 번이에요?"
        print(f"Input: {query}")
        result = await infer_product_keywords(query)
        print(f"Result: {result}")
    except Exception:
        print("ERROR in infer_product_keywords:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_nlu())
