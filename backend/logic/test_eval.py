
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

def test_eval():
    question = "붙였다 떼도 자국 안 남는 거 뭐 있어요?"
    intention = "무자국 후크 / 제거형 양면테이프 구매"
    keyword = "몬스터클리어젤"

    prompt = f"""
    Role: You are a judge evaluating search keywords for Daiso products.
    Task: Determine if the 'Extracted Keyword' is a valid search term for the 'Target Intention'.

    [Daiso Knowledge Base]
    - **Monster Clear Gel (몬스터클리어젤)**: A strong, residue-free double-sided adhesive gel tape. Matches "Remove residue", "Strong fixation".
    - **Kkokkopin (꼭꼬핀)**: A hook for wallpaper that doesn't leave needle marks. Matches "Wall hook", "No trace".
    - **Magic Block (매직블럭)**: A melamine sponge for cleaning. Matches "Cleaner", "Stain remover".
    - **Diatomaceous Earth Mat (규조토발매트)**: A hard, stone-like bath mat that dries instantly. Matches "Quick dry", "Mat".
    - **Door Stopper (도어스토퍼)**: Prevents door slamming. Matches "Noise reduction", "Door safety".

    [Evaluation Rules]
    1. **Specific is Good**: If the User Intention is generic (e.g., "Double-sided tape") but the Keyword is a specific famous product (e.g., "Monster Clear Gel"), this is a **MATCH**.
       - Example: Intention="Remove residue", Keyword="Sticker Remover" -> MATCH
       - Example: Intention="Strong hook", Keyword="Kkokkopin" -> MATCH
    2. **Broad is Okay**: If the keyword acts as a category that contains the target product, it is a MATCH.
    3. **Category Consistency**: If the Keyword is a totally different category (e.g., "Scrubber" for "Mat"), it is a MISMATCH.
    4. **Function over Form**: If the keyword solves the *core problem* described in the intention, it is a MATCH.

    [Input]
    Question: "{question}"
    Target Intention: "{intention}"
    Extracted Keyword: "{keyword}"
    
    Is this keyword a reasonably good search term to fulfill the intention?
    - If the keyword helps find the product described in the intention, say MATCH.
    - If the keyword is wrong or irrelevant, say MISMATCH.
    
    Output format: MATCH | <Reasoning> or MISMATCH | <Reasoning>
    """
    
    print("Sending prompt...")
    response = model.generate_content(prompt)
    result = response.text.strip()
    print(f"Result: {result}")
    
    with open("test_result.txt", "w", encoding="utf-8") as f:
        f.write(result)

if __name__ == "__main__":
    test_eval()
