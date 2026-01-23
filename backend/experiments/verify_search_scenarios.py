import os
import sys
import time
import random
import sqlite3

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from backend.logic.graph import app

DB_PATH = os.path.join(BASE_DIR, 'backend', 'database', 'products.db')
OUTPUT_FILE = os.path.join(BASE_DIR, 'backend', 'database', 'comprehensive_search_report.txt')

# Define Test Scenarios templates (30 per category)
# STRICTLY mapped to existing DB items (insert_mock_data.py)
TEST_SUITES = {
    "1. 기본형 (Basic Noun)": [
        {"query": "컵 있어요?", "target_name_part": "종이컵"},
        {"query": "유리컵 있나요?", "target_name_part": "유리컵"},
        {"query": "멀티탭 찾아요", "target_name_part": "케이블 박스"},
        {"query": "건전지 있어요?", "target_name_part": "건전지"},
        {"query": "가위 어디 있어요?", "target_name_part": "가위"},
        {"query": "방향제 어디 있어요?", "target_name_part": "방향제"},
        {"query": "매트 찾고 있어요", "target_name_part": "미끄럼방지 매트"},
        {"query": "수납 바구니 있어요?", "target_name_part": "수납 바구니"},
        {"query": "청소솔 보여줘", "target_name_part": "청소솔"}, # If not exists, use related
        {"query": "트랩 있어요?", "target_name_part": "냄새 차단 트랩"},
        {"query": "테이프 어디에요?", "target_name_part": "보수 테이프"},
        {"query": "의자 발커버 찾아요", "target_name_part": "의자 발커버"},
        {"query": "패드 있어요?", "target_name_part": "충격 흡수 패드"},
        {"query": "스퀴지 어디 있나요?", "target_name_part": "스퀴지"},
        {"query": "압축봉 찾아요", "target_name_part": "압축봉"},
        {"query": "네트망 있어요?", "target_name_part": "네트망"},
        {"query": "냄비받침 어디에요?", "target_name_part": "냄비받침"},
        {"query": "제습제 찾고 있어요", "target_name_part": "옷장용 제습제"},
        {"query": "걸레 빨아쓰는거 있어요?", "target_name_part": "극세사 걸레"},
        {"query": "정리함 보여줘", "target_name_part": "화장품 정리함"},
        {"query": "앞치마 있어요?", "target_name_part": "방수 앞치마"},
        {"query": "스토퍼 찾아요", "target_name_part": "방지 스토퍼"},
        {"query": "모서리 보호대 있어요?", "target_name_part": "모서리 보호대"},
        {"query": "세정제 위치 어디에요?", "target_name_part": "변기 세정제"},
        {"query": "물막이 찾아요", "target_name_part": "싱크대 물막이"},
        {"query": "S자 고리 있어요?", "target_name_part": "S자 고리"},
        {"query": "단열시트 어디 있나요?", "target_name_part": "단열시트"},
        {"query": "압축팩 찾아요", "target_name_part": "의류 압축팩"},
        {"query": "여행용 용기 있어요?", "target_name_part": "여행용 리필"},
        {"query": "디퓨저 찾고 있어요", "target_name_part": "차량용 디퓨저"}
    ],
    "2. 속성 결합형 (Material/Color/Size)": [
        {"query": "유리컵 있어요?", "target_name_part": "유리컵"},
        {"query": "내열 유리컵 찾아요", "target_name_part": "내열 유리컵"},
        {"query": "도자기 그릇 어디에요?", "target_name_part": "도자기 대접"},
        {"query": "3단 우산 있어요?", "target_name_part": "3단 자동 우산"},
        {"query": "검정색 우산 있어요?", "target_name_part": "3단 자동 우산"},
        {"query": "규조토 제품 있어요?", "target_name_part": "규조토 발매트"},
        {"query": "규조토 발매트 찾아요", "target_name_part": "규조토 발매트"},
        {"query": "투명 논슬립 스티커 있어요?", "target_name_part": "투명 논슬립"},
        {"query": "그레이색 매트 찾아요", "target_name_part": "미끄럼방지 매트"},
        {"query": "젤타입 곰팡이 제거제", "target_name_part": "곰팡이 제거제"},
        {"query": "스텐 거름망 있어요?", "target_name_part": "스텐 배수구"},
        {"query": "실리콘 냄비받침 찾아요", "target_name_part": "실리콘 냄비받침"},
        {"query": "아크릴 정리함 어디에요?", "target_name_part": "화장품 정리함"},
        {"query": "AA 건전지 있어요?", "target_name_part": "알카라인 건전지 AA"},
        {"query": "캡형 물티슈 찾아요", "target_name_part": "물티슈"},
        {"query": "대용량 매직 스펀지", "target_name_part": "매직 스펀지"},
        {"query": "260mm 슬리퍼 있어요?", "target_name_part": "EVA 욕실 슬리퍼"},
        {"query": "체크무늬 마스킹 테이프", "target_name_part": "다이어리 마스킹"},
        {"query": "스테인리스 빨대 찾아요", "target_name_part": "스테인리스 빨대"},
        {"query": "대형 전자레인지 덮개", "target_name_part": "전자레인지용 덮개"},
        {"query": "화이트 압축봉 있어요?", "target_name_part": "압축봉"},
        {"query": "소형 압축봉 찾아요", "target_name_part": "압축봉"},
        {"query": "브라운 의자 발커버", "target_name_part": "의자 발커버"},
        {"query": "중형 수납 바구니", "target_name_part": "다용도 수납 바구니"},
        {"query": "2m 전선 보호 튜브", "target_name_part": "전선 보호 튜브"},
        {"query": "5p 리필 용기", "target_name_part": "여행용 리필"},
        {"query": "1L 배수구 뻥", "target_name_part": "배수구 뻥"},
        {"query": "블랙체리 디퓨저", "target_name_part": "차량용 디퓨저"},
        {"query": "일자형 꼭꼬핀", "target_name_part": "꼭꼬핀"},
        {"query": "4구 칫솔 꽂이", "target_name_part": "4구"}
    ],
    "3. 별칭/은어형 (Alias/Slang)": [
        {"query": "매직블럭 있어요?", "target_name_part": "매직 스펀지"},
        {"query": "샤워볼 있어요?", "target_name_part": "바디 샤워볼"},
        {"query": "포스트잇 찾아요", "target_name_part": "점착 메모지"},
        {"query": "방충망 테이프 있어요?", "target_name_part": "방충망 보수"},
        {"query": "돌돌이 리필 어디에요?", "target_name_part": "롤클리너 리필"},
        {"query": "뽁뽁이 있어요?", "target_name_part": "단열시트"},
        {"query": "뚫어뻥 액체 있어요?", "target_name_part": "배수구 뻥"},
        {"query": "순간접착제 본드 찾아요", "target_name_part": "순간접착제"},
        {"query": "유리창 닦이 있어요?", "target_name_part": "스퀴지"},
        {"query": "밀대 있어요?", "target_name_part": "극세사 걸레"},
        {"query": "옷걸이 봉 찾아요", "target_name_part": "압축봉"},
        {"query": "충전 줄 있어요?", "target_name_part": "충전 케이블"},
        {"query": "핸드폰 줄", "target_name_part": "충전 케이블"},
        {"query": "비닐 랩 있어요?", "target_name_part": "크린랩"},
        {"query": "수세미 있어요?", "target_name_part": "매직 스펀지"},
        {"query": "행주 찾아요", "target_name_part": "걸레"},
        {"query": "칙칙이 방향제", "target_name_part": "제거 스프레이"},
        {"query": "습기 제거제", "target_name_part": "제습제"},
        {"query": "화장실 슬리퍼", "target_name_part": "욕실 슬리퍼"},
        {"query": "욕실 신발", "target_name_part": "욕실 슬리퍼"},
        {"query": "거름망 스텐", "target_name_part": "배수구 거름망"},
        {"query": "날파리 트랩", "target_name_part": "초파리 트랩"},
        {"query": "문 꽝 방지", "target_name_part": "방지 스토퍼"},
        {"query": "애기 모서리 쿵", "target_name_part": "모서리 보호대"},
        {"query": "변기 청소볼", "target_name_part": "변기 세정제"},
        {"query": "머리카락 거름망", "target_name_part": "배수구 냄새 차단"},
        {"query": "케이블 타이", "target_name_part": "케이블 박스"},
        {"query": "끈끈이 제거", "target_name_part": "보수 테이프"}, # Adjusted
        {"query": "주방 세제", "target_name_part": "곰팡이 제거제"}, 
        {"query": "책상 정리함", "target_name_part": "수납 바구니"}
    ],
    "4. 캐릭터/브랜드형 (Character/Brand)": [
        {"query": "키티 빗 찾아요", "target_name_part": "헬로키티"},
        {"query": "헬로키티 제품 있어요?", "target_name_part": "헬로키티"},
        {"query": "카카오 프렌즈 칫솔 있어요?", "target_name_part": "카카오프렌즈"},
        {"query": "라이언 칫솔 있어요?", "target_name_part": "카카오프렌즈"},
        {"query": "크린랩 어디에요?", "target_name_part": "크린랩"},
        # Using existing items with 'Brand-like' or specific queries
        {"query": "3M 스펀지 있나요?", "target_name_part": "매직 스펀지"}, 
        {"query": "다이소 곰팡이 젤", "target_name_part": "곰팡이 제거제"},
        {"query": "다이소 건전지", "target_name_part": "알카라인 건전지"},
        {"query": "다이소 물티슈", "target_name_part": "물티슈"},
        {"query": "아이폰 케이블", "target_name_part": "아이폰"},
        {"query": "갤럭시 충전기", "target_name_part": "고속충전 케이블"}, # 8-pin mock
        # Duplicates/Variations to fill 30 without fake products
        {"query": "키티 캐릭터 용품", "target_name_part": "헬로키티"},
        {"query": "카카오 라이언 칫솔", "target_name_part": "카카오프렌즈"},
        {"query": "크린랩 비닐", "target_name_part": "크린랩"},
        {"query": "크린랩 30cm", "target_name_part": "크린랩"},
        {"query": "헬로키티 빗", "target_name_part": "헬로키티"},
        {"query": "카카오 칫솔", "target_name_part": "카카오프렌즈"},
        {"query": "라이언 구강용품", "target_name_part": "카카오프렌즈"},
        {"query": "아이폰 충전줄", "target_name_part": "아이폰"},
        {"query": "아이폰 8핀", "target_name_part": "아이폰"},
        {"query": "다이소 건전지 AA", "target_name_part": "알카라인 건전지"},
        {"query": "다이소 곰팡이 제거", "target_name_part": "곰팡이 제거제"},
        {"query": "다이소 매직블럭", "target_name_part": "매직 스펀지"},
        {"query": "다이소 뽁뽁이", "target_name_part": "단열시트"},
        {"query": "다이소 압축봉", "target_name_part": "압축봉"},
        {"query": "다이소 네트망", "target_name_part": "네트망"},
        {"query": "다이소 슬리퍼", "target_name_part": "욕실 슬리퍼"},
        {"query": "다이소 변기솔", "target_name_part": "변기 세정제"},
        {"query": "다이소 보수 테이프", "target_name_part": "보수 테이프"},
        {"query": "다이소 걸레", "target_name_part": "극세사 걸레"},
        {"query": "다이소 물막이", "target_name_part": "싱크대 물막이"}
    ],
    "5. 부속/파츠형 (Part/Refill)": [
        {"query": "롤클리너 리필 어디에요?", "target_name_part": "롤클리너 리필"},
        {"query": "칫솔 꽂이 찾는데요", "target_name_part": "칫솔 꽂이"},
        {"query": "비누 받침대 있어요?", "target_name_part": "비누 받침대"},
        {"query": "건전지 AA 사이즈 찾아요", "target_name_part": "알카라인 건전지"},
        {"query": "리필용 용기 있어요?", "target_name_part": "여행용 리필"},
        {"query": "매직블럭 리필", "target_name_part": "매직 스펀지"}, 
        {"query": "테이프 리필", "target_name_part": "보수 테이프"},
        {"query": "방충망 보수용", "target_name_part": "방충망 보수"},
        {"query": "의자 발커버 낱개", "target_name_part": "의자 발커버"},
        {"query": "케이블 정리 홀더", "target_name_part": "케이블 정리"},
        {"query": "냄비 받침", "target_name_part": "냄비받침"},
        {"query": "전자레인지 뚜껑", "target_name_part": "전자레인지용 덮개"},
        {"query": "제습제 리필", "target_name_part": "옷장용 제습제"},
        {"query": "걸레 리필", "target_name_part": "극세사 걸레"},
        {"query": "변기 세정제 리필", "target_name_part": "변기 세정제"},
        {"query": "싱크대 거름망", "target_name_part": "배수구 거름망"},
        {"query": "배수구 뚜껑", "target_name_part": "냄새 차단 트랩"},
        {"query": "청소포 리필", "target_name_part": "극세사 걸레"},
        {"query": "샴푸통 펌프", "target_name_part": "여행용 리필"}, # Similar
        {"query": "압축봉 고무", "target_name_part": "압축봉"},
        {"query": "우산 커버", "target_name_part": "3단 자동 우산"},
        {"query": "디퓨저 리필액", "target_name_part": "차량용 디퓨저"},
        {"query": "리필 용기 5개", "target_name_part": "여행용 리필"},
        {"query": "롤클리너 테이프", "target_name_part": "롤클리너 리필"},
        {"query": "칫솔 걸이", "target_name_part": "칫솔 꽂이"},
        {"query": "비누 곽", "target_name_part": "비누 받침대"},
        {"query": "건전지 리필", "target_name_part": "알카라인 건전지"},
        {"query": "테이프 심", "target_name_part": "보수 테이프"},
        {"query": "의자 양말", "target_name_part": "의자 발커버"},
        {"query": "케이블 박스 뚜껑", "target_name_part": "케이블 정리"}
    ]
}

def run_comprehensive_test():
    print("Starting Comprehensive Search Verification (5 Categories)...", flush=True)
    
    report_lines = []
    report_lines.append(f"🧪 Comprehensive Categorized Search Report")
    report_lines.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 110)
    
    total_passed = 0
    total_count = 0
    
    for category_title, tests in TEST_SUITES.items():
        print(f"\nRunning {category_title}...", flush=True)
        report_lines.append(f"\n{category_title}")
        report_lines.append("-" * 110)
        report_lines.append(f"{'Query':<30} | {'Intent':<15} | {'Category':<32} | {'Result'}")
        report_lines.append("-" * 110)
        
        for test in tests:
            query = test['query']
            target_part = test['target_name_part']
            
            # Run Test
            config = {"configurable": {"thread_id": f"comp_{random.randint(1000,9999)}"}}
            
            try:
                response = app.invoke({"query": query}, config=config)
                
                intent = response.get("intent", "unknown")
                final_res = response.get("final_response", "")
                
                # Check if specific target_part keyword was found in response
                passed = target_part in final_res
                
                status = "✅" if passed else "❌"
                if passed: total_passed += 1
                total_count += 1
                
                # Extract category from search results if available
                found_category = "N/A"
                if response.get("search_results") and len(response["search_results"]) > 0:
                    first_item = response["search_results"][0]
                    found_category = f"{first_item['category_major']}/{first_item['category_middle']}"
                
                report_lines.append(f"{query[:30]:<30} | {intent[:15]:<15} | {found_category[:32]:<32} | {status}")
                
            except Exception as e:
                report_lines.append(f"{query[:30]:<30} | ERROR           | Error                            | ❌ Error")
                print(f"  Error on {query}: {e}")

        report_lines.append("-" * 110)
    
    report_lines.append(f"\nTotal Success Rate: {total_passed}/{total_count} ({total_passed/total_count*100:.1f}%)")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("\n" + "="*30)
    print("Test Complete!")
    print(f"Report saved to: {OUTPUT_FILE}")
    print("="*30)

if __name__ == "__main__":
    run_comprehensive_test()
