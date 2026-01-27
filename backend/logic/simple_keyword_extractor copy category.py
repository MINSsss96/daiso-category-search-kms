
import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash") # Updated to 2.0-flash as per nlu.py suggestion


# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "database", "question_situation100.json")

def load_questions():
    if not os.path.exists(JSON_PATH):
        print(f"Error: File not found at {JSON_PATH}")
        return []
    
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("questions", [])

def extract_keyword(query):
    prompt = f"""
   당신은 다이소의 **'상품 카테고리 분류 전문가'**입니다.
    고객의 모호한 질문(특징, 상황, 묘사)을 분석하여, 다이소의 **표준 상품군(Standard Category Keyword)** 하나를 도출해야 합니다.

    # [Goal]
    3만 개의 개별 상품명(SKU)을 맞추는 것이 아닙니다.
    검색이 가능한 **'가장 구체적인 카테고리명'**이나 **'대표 상품명'**을 출력하세요.

    # [Thinking Strategy: 2-Step Classification]
    1. **대분류/중분류 판단**: 고객의 의도가 어느 영역인가? (다이소몰 공식 카테고리)
    - [청소/욕실]: 청소용품, 세탁용품, 욕실용품, 변기/배수구용품, 휴지/물티슈, 살충제/제습제, 휴지통/비닐봉투, 주방/청소세제, 세탁세제, 수건/타월, 방충용품
    - [국민득템]: 신상(NEW), 인기상품(BEST), 균일가
    - [뷰티/위생]: 스킨케어, 메이크업, 네일용품, 미용소품, 맨케어, 헤어/바디, 화장지/물티슈, 건강/위생용품, 가정의료용품, 마스크, 칫솔/치약/구강용품
    - [주방용품]: 식기/그릇/트레이, 잔/컵/물병, 밀폐/보관/저장용기, 수저/커트러리, 주방잡화, 주방수납정리, 일회용품, 팬/냄비/뚝배기, 칼/도마/채칼/가위, 조리도구, 베이킹용품, 와인용품, 커피/티용품
    - [수납/정리]: 수납정리함, 바구니류, 사무수납, 행거/후크, 네트망, 옷걸이, 보관커버
    - [문구/팬시]: 다이어리/노트/메모, 폴꾸용품, 스티커류, 문구/사무용품, 필기용품, 편지/봉투, 포장용품, 테이프, 미술용품, 보드/칠판, 파티/이벤트용품
    - [인테리어/원예]: 시계/액자, 아로마/캔들용품, 원예용품, 조화, 안전용품, 다용도매트, 시트지, 커튼용품, 침구/쿠션/방석, 단열/방한용품, 장식소품, 테이블/의자
    - [공구/디지털]: 공구용품, 건전지/콘센트, 조명/전구, 컴퓨터, 휴대폰, 이어폰, 소형가전
    - [식품]: 건강식품, 과자, 음료/커피/차, 사탕/초콜릿/젤리, 견과류/포, 라면/즉석식품, 기타식품
    - [스포츠/레저/취미]: 캠핑/여행, 자동차용품, 홈트레이닝, 구기/라켓운동, 등산/수영/골프, 자전거용품, 스포츠잡화, 취미/기호, 수예용품
    - [패션/잡화]: 의류/언더웨어, 가방, 패션소품, 양말/스타킹, 신발, 슈즈용품, 우천용품
    - [반려동물]: 반려동물완구, 고양이식품, 강아지식품, 위생/미용용품, 외출용품/하우스, 의류/액세서리, 식기/급수기, 관상어/소동물용품
    - [유아/완구]: 역할놀이, 인형, 만들기완구, 로봇/작동완구, 지능개발완구, 어린이도서, 놀이완구, 물놀이완구, 유아용품
    - [시즌/시리즈]: 디즈니, 짱구, 마이멜로디, 피너츠, 모모레이, 다이소굿즈
    - [상품권]: 모바일 상품권

 당신은 다이소의 **'고객 의도 분석 및 상품 매칭 AI'**입니다.
고객의 모호한 질문(Query)을 분석하여, 그들이 진짜로 해결하고자 하는 **'행동 의도(Intent)'**를 파악하고, 이를 해결해 줄 **'대표 상품(Primary Keyword)'** 하나를 도출하세요.
    
    Query: "{query}"
    Keyword:
    """
    try:
        start_time = time.time()
        response = model.generate_content(prompt)
        end_time = time.time()
        latency = end_time - start_time
        
        keyword = response.text.strip()
        
        usage = response.usage_metadata
        prompt_tokens = usage.prompt_token_count
        candidates_tokens = usage.candidates_token_count
        total_tokens = usage.total_token_count

        return {
            "keyword": keyword,
            "latency": latency,
            "tokens": {
                "prompt": prompt_tokens,
                "completion": candidates_tokens,
                "total": total_tokens
            }
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    questions = load_questions()
    if not questions:
        return

    print(f"Loaded {len(questions)} questions.")
    print("-" * 50)
    
    output_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted_keywords_root.txt")
    print(f"Saving results to: {output_txt_path}")

    with open(output_txt_path, "w", encoding="utf-8") as f:
        for i, q in enumerate(questions):
            result = extract_keyword(q)
            
            if "error" in result:
                line = f"Q: {q} -> Error: {result['error']}"
            else:
                keyword = result["keyword"]
                latency = result["latency"]
                tokens = result["tokens"]
                
                # Format: Question -> Keyword (Latency: Xs, Tokens: [P:X, C:X, T:X])
                line = f"Q: {q} -> Keyword: {keyword}"
                meta_info = f"(Latency: {latency:.3f}s, Tokens: [P:{tokens['prompt']}, C:{tokens['completion']}, T:{tokens['total']}])"
                
                print(f"[{i+1}/{len(questions)}] {line} {meta_info}")
                f.write(f"{line} {meta_info}\n")
            
            f.flush() 

    print(f"\nAnalysis complete. Results saved to {output_txt_path}")

if __name__ == "__main__":
    main()
