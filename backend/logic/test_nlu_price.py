
import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.logic.nlu import analyze_text

async def test():
    query = "5000원 이하 생일 선물 추천"
    with open("test_result.txt", "w", encoding="utf-8") as f:
        f.write(f"Testing Query: {query}\n")
        
        response = await analyze_text(query)
        
        f.write("\n--- NLU Response ---\n")
        f.write(f"Intent: {response.intent}\n")
        f.write(f"Slots: {response.slots}\n")
        f.write(f"Item: {response.slots.item}\n")
        f.write(f"Query Rewrite: {response.slots.query_rewrite}\n")
        f.write(f"Min Price: {response.slots.min_price}\n")
        f.write(f"Max Price: {response.slots.max_price}\n")
        print("Done writing to file.")

if __name__ == "__main__":
    asyncio.run(test())
