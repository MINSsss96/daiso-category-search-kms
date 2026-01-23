
import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure backend logic matches
try:
    from backend.logic.nlu import analyze_text
    from backend.logic.schemas import Intent
except ImportError:
    # Fallback if run from root
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from backend.logic.nlu import analyze_text
    from backend.logic.schemas import Intent

load_dotenv()

async def run_experiment():
    output_file = "nlu_experiment_results.txt"
    
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

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== Starting NLU Experiment with Gemini 2.0 Flash ===\n\n")

        for i, case in enumerate(test_cases, 1):
            query = case["query"]
            f.write(f"Test #{i}: '{query}'\n")
            print(f"Running Test #{i}: '{query}'")
            
            try:
                result = await analyze_text(query)
                
                # Print Result Summary
                f.write(f"  -> Intent: {result.intent}\n")
                f.write(f"  -> Clarification Needed: {result.needs_clarification}\n")
                if result.generated_question:
                    f.write(f"  -> Generated Question: {result.generated_question}\n")
                f.write(f"  -> Slots: {result.slots}\n")

                # Verification Logic
                pass_check = True
                if result.intent != case["expected_intent"]:
                    f.write(f"  [FAIL] Intent mismatch. Expected {case['expected_intent']}\n")
                    pass_check = False
                
                if case.get("expect_clarification") is not None:
                    if result.needs_clarification != case["expect_clarification"]:
                        f.write(f"  [FAIL] Clarification mismatch. Expected {case['expect_clarification']}\n")
                        pass_check = False

                if pass_check:
                    f.write("  [PASS] ✅\n")
                else:
                    f.write("  [FAIL] ❌\n")

            except Exception as e:
                f.write(f"  [ERROR] {e}\n")
            
            f.write("-" * 50 + "\n")
    
    print(f"Experiment complete. Results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(run_experiment())
