
import asyncio
import os
import sys

# Add parent directory to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.logic.nlu import analyze_text
from backend.logic.schemas import Intent

async def run_experiment():
    test_cases = [
        # 1. Clear Search
        {"query": "파란색 볼펜 있어?", "expected_intent": Intent.SEARCH, "check_slots": True},
        # 2. Vague Search (Should trigger clarification)
        {"query": "뭐 좋은거 있어?", "expected_intent": Intent.SEARCH, "expect_clarification": True},
        # 3. Price Constraint
        {"query": "3000원짜리 바구니", "expected_intent": Intent.SEARCH, "check_price": True},
        # 4. Chit Chat
        {"query": "안녕 반가워", "expected_intent": Intent.CHIT_CHAT, "expect_clarification": False},
    ]

    print("=== Starting NLU Experiment with Gemini 2.0 Flash ===\n")

    for i, case in enumerate(test_cases, 1):
        query = case["query"]
        print(f"Test #{i}: '{query}'")
        
        try:
            result = await analyze_text(query)
            
            # Print Result Summary
            print(f"  -> Intent: {result.intent}")
            print(f"  -> Clarification Needed: {result.needs_clarification}")
            if result.generated_question:
                print(f"  -> Generated Question: {result.generated_question}")
            print(f"  -> Slots: {result.slots}")

            # Verification Logic
            pass_check = True
            if result.intent != case["expected_intent"]:
                print("  [FAIL] Intent mismatch")
                pass_check = False
            
            if case.get("expect_clarification") is not None:
                if result.needs_clarification != case["expect_clarification"]:
                    print(f"  [FAIL] Clarification mismatch. Expected {case['expect_clarification']}")
                    pass_check = False

            if pass_check:
                print("  [PASS] ✅")
            else:
                print("  [FAIL] ❌")

        except Exception as e:
            print(f"  [ERROR] {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_experiment())
