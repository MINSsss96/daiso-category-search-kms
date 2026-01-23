import os
import re

# Embedded Ground Truth Data to avoid import issues
QUESTION_DATA=[
  {"id": 1, "query": "화장실 변기 닦아도 냄새가 안 없어져요.", "expected_intent": "implicit", "ground_truth": ["변기 세정제", "크리너"]},
  {"id": 2, "query": "문 닫을 때마다 쾅쾅 소리 나서 시끄러워요.", "expected_intent": "implicit", "ground_truth": ["문닫힘 방지", "도어 쿠션"]},
  {"id": 3, "query": "바닥 긁히는 소리 안 나게 의자에 끼우는 거 있어요?", "expected_intent": "implicit", "ground_truth": ["의자 발 커버", "소음 방지"]},
  {"id": 4, "query": "싱크대 배수구가 꽉 막혀서 물이 안 내려가요.", "expected_intent": "implicit", "ground_truth": ["배수구 뻥", "뚫어뻥", "배수구 클리너"]},
  {"id": 5, "query": "새로 산 그릇에 스티커 끈끈이가 남아서 안 떼져요.", "expected_intent": "implicit", "ground_truth": ["스티커 제거제"]},
  {"id": 6, "query": "장마철이라 옷장에서 꿉꿉한 냄새가 나요.", "expected_intent": "implicit", "ground_truth": ["제습제", "습기 제거제", "탈취제"]},
  {"id": 7, "query": "초파리가 자꾸 꼬이는데 잡는 트랩 같은 거 있나요?", "expected_intent": "implicit", "ground_truth": ["초파리 트랩", "끈끈이"]},
  {"id": 8, "query": "욕실 타일 틈새에 검은 곰팡이가 꼈어요.", "expected_intent": "implicit", "ground_truth": ["곰팡이 제거제", "곰팡이 젤"]},
  {"id": 9, "query": "와이셔츠 목 때가 세탁기로 빨아도 잘 안 지워져요.", "expected_intent": "implicit", "ground_truth": ["부분 얼룩 제거제", "찌든 때 클리너"]},
  {"id": 10, "query": "강아지 털이 옷에 너무 많이 붙어서 떼고 싶어요.", "expected_intent": "implicit", "ground_truth": ["돌돌이", "테이프 클리너"]},
  {"id": 11, "query": "책상 밑에 전선들이 너무 지저분하게 엉켜 있어요.", "expected_intent": "implicit", "ground_truth": ["케이블 타이", "전선 정리함"]},
  {"id": 12, "query": "방충망에 구멍이 났는데 전체 갈기는 좀 그렇고...", "expected_intent": "implicit", "ground_truth": ["방충망 보수 테이프"]},
  {"id": 13, "query": "요리하다가 기름이 벽에 너무 많이 튀어요.", "expected_intent": "implicit", "ground_truth": ["가스레인지 가드", "기름 튀김 방지"]},
  {"id": 14, "query": "신발장 열 때마다 발 냄새가 너무 심해요.", "expected_intent": "implicit", "ground_truth": ["신발 탈취제", "제습제"]},
  {"id": 15, "query": "유리에 테이프 자국 남은 거 긁어내고 싶어요.", "expected_intent": "implicit", "ground_truth": ["스크래퍼", "스티커 제거제"]},
  {"id": 16, "query": "바지 허리가 너무 커서 줄이고 싶은데 바느질은 못해요.", "expected_intent": "implicit", "ground_truth": ["요술 단추", "수선 테이프"]},
  {"id": 17, "query": "가구 모서리에 애기가 찧을까 봐 걱정돼요.", "expected_intent": "implicit", "ground_truth": ["모서리 보호대", "안전 가드"]},
  {"id": 18, "query": "화장실 거울에 김이 너무 서려서 안 보여요.", "expected_intent": "implicit", "ground_truth": ["김서림 방지제"]},
  {"id": 19, "query": "검은 옷에 먼지가 너무 잘 붙어요.", "expected_intent": "implicit", "ground_truth": ["먼지 제거 브러시", "옷솔"]},
  {"id": 20, "query": "냉장고 안에 김치 국물이 흘러서 굳었어요.", "expected_intent": "implicit", "ground_truth": ["다목적 세정제", "베이킹소다 티슈"]},
  {"id": 21, "query": "벽에 못 안 박고 액자 걸 수 있는 핀 같은 거요.", "expected_intent": "implicit", "ground_truth": ["꼭꼬핀"]},
  {"id": 22, "query": "물만 묻혀서 닦으면 때 지워지는 하얀 스펀지 주세요.", "expected_intent": "implicit", "ground_truth": ["매직블럭", "멜라민 스펀지"]},
  {"id": 23, "query": "치약 끝까지 짜서 쓰게 해주는 플라스틱 있나요?", "expected_intent": "implicit", "ground_truth": ["치약 짜개"]},
  {"id": 24, "query": "전자레인지 안에 넣고 돌려도 되는 밥 보관 용기요.", "expected_intent": "implicit", "ground_truth": ["전자레인지 용기", "밥팩"]},
  {"id": 25, "query": "그물처럼 생겨서 설거지하고 수세미 말리는 거.", "expected_intent": "implicit", "ground_truth": ["수세미 거치대"]},
  {"id": 26, "query": "방 문 뒤에 걸어서 옷 걸 수 있게 하는 거요.", "expected_intent": "implicit", "ground_truth": ["도어 후크", "문걸이 행거"]},
  {"id": 27, "query": "주방 서랍 안에 숟가락 젓가락 칸 나눠주는 통.", "expected_intent": "implicit", "ground_truth": ["수저 분리함", "수저 트레이"]},
  {"id": 28, "query": "여행 갈 때 샴푸랑 린스 조금씩 덜어가는 공병.", "expected_intent": "implicit", "ground_truth": ["리필 용기", "소분 용기"]},
  {"id": 29, "query": "핸드폰 뒤에 붙여서 손가락 끼우는 동그란 거.", "expected_intent": "implicit", "ground_truth": ["그립톡", "스마트톡"]},
  {"id": 30, "query": "비누가 물러서 자꾸 녹는데 안 닿게 해주는 받침대.", "expected_intent": "implicit", "ground_truth": ["규조토 받침", "물빠짐 비누 받침"]},
  {"id": 31, "query": "화분 흙 안 쏟아지게 바닥에 까는 망 같은 거.", "expected_intent": "implicit", "ground_truth": ["깔망"]},
  {"id": 32, "query": "머리카락 배수구에 안 들어가게 걸러주는 스티커.", "expected_intent": "implicit", "ground_truth": ["배수구 거름망 시트"]},
  {"id": 33, "query": "책상 위에 놓고 쓰는 아주 작은 빗자루 세트.", "expected_intent": "implicit", "ground_truth": ["미니 빗자루", "청소포"]},
  {"id": 34, "query": "운동화 끈 안 묶고 그냥 당겨서 조이는 끈.", "expected_intent": "implicit", "ground_truth": ["매듭 없는 신발끈", "실리콘 신발끈"]},
  {"id": 35, "query": "의자 밑에 붙여서 잘 미끄러지게 하는 스티커.", "expected_intent": "implicit", "ground_truth": ["가구 슬라이딩 패드"]},
  {"id": 36, "query": "설거지할 때 옷 젖지 말라고 배에 대는 가림막.", "expected_intent": "implicit", "ground_truth": ["싱크대 물막이"]},
  {"id": 37, "query": "싱크대 구석에 음식물 쓰레기 모아두는 삼각 통.", "expected_intent": "implicit", "ground_truth": ["싱크대 거름통", "삼각 코너"]},
  {"id": 38, "query": "유리창 닦을 때 물기 싹 긁어내리는 고무 달린 막대기.", "expected_intent": "implicit", "ground_truth": ["윈도우 브러시", "스퀴지"]},
  {"id": 39, "query": "긴 컵 닦을 때 쓰는 손잡이 달린 스펀지.", "expected_intent": "implicit", "ground_truth": ["병 세척 솔", "물병 솔"]},
  {"id": 40, "query": "마시다 남은 와인 막아두는 마개.", "expected_intent": "implicit", "ground_truth": ["와인 스토퍼"]},
  {"id": 41, "query": "내일 자취방 처음 들어가는데 청소 필수템 좀 알려주세요.", "expected_intent": "implicit", "ground_truth": ["청소용품", "돌돌이", "물티슈"]},
  {"id": 42, "query": "친구들이랑 홈파티 하는데 벽에 붙일 장식 추천해 줘.", "expected_intent": "implicit", "ground_truth": ["파티 가랜드", "풍선"]},
  {"id": 43, "query": "해외여행 가는데 비행기 안에서 편하게 있을 만한 거.", "expected_intent": "implicit", "ground_truth": ["목베개", "안대", "슬리퍼"]},
  {"id": 44, "query": "강아지랑 산책 갈 때 챙겨야 할 거 뭐 있죠?", "expected_intent": "implicit", "ground_truth": ["배변 봉투", "리드줄"]},
  {"id": 45, "query": "회사 책상이 너무 삭막해서 좀 꾸미고 싶어요.", "expected_intent": "implicit", "ground_truth": ["데스크 테리어", "화분", "달력"]},
  {"id": 46, "query": "집에서 혼자 네일아트 해보려고 하는데 뭐부터 사야 해요?", "expected_intent": "implicit", "ground_truth": ["네일 키트", "네일 파일", "젤 램프"]},
  {"id": 47, "query": "겨울옷 정리해서 넣어두려는데 부피 줄이는 봉투 있나요?", "expected_intent": "implicit", "ground_truth": ["의류 압축팩"]},
  {"id": 48, "query": "차 박 할 때 창문 가리는 용도로 쓸 만한 거.", "expected_intent": "implicit", "ground_truth": ["햇빛 가리개", "자석 커튼"]},
  {"id": 49, "query": "아이들 학교 준비물로 색종이랑 풀 담을 통이 필요해요.", "expected_intent": "implicit", "ground_truth": ["파일 케이스", "수납함"]},
  {"id": 50, "query": "싱크대 상판이 너무 좁아서 공간 활용하고 싶어요.", "expected_intent": "implicit", "ground_truth": ["싱크대 선반", "식기 건조대"]},
  {"id": 51, "query": "캠핑 가서 고기 구워 먹을 때 쓸 일회용 접시 세트.", "expected_intent": "implicit", "ground_truth": ["일회용 그릇", "캠핑 식기"]},
  {"id": 52, "query": "욕실에 샴푸랑 린스 놓을 자리가 없어서 공중부양 시키고 싶어요.", "expected_intent": "implicit", "ground_truth": ["후크", "공중부양 홀더"]},
  {"id": 53, "query": "다이어리 꾸미기 입문하려는데 스티커 추천 좀.", "expected_intent": "implicit", "ground_truth": ["다꾸 스티커", "마스킹 테이프"]},
  {"id": 54, "query": "선생님께 드릴 건데 너무 비싸지 않으면서 포장 예쁜 거.", "expected_intent": "implicit", "ground_truth": ["선물 상자", "쇼핑백", "포장지"]},
  {"id": 55, "query": "비 오는 날 신발 젖는 거 너무 싫은데 방수되는 거 없나요?", "expected_intent": "implicit", "ground_truth": ["방수 스프레이", "신발 커버"]},
  {"id": 56, "query": "조카가 슬라임 만들고 싶다는데 재료 어디 있어요?", "expected_intent": "implicit", "ground_truth": ["슬라임", "클레이", "파츠"]},
  {"id": 57, "query": "유튜브 촬영할 때 핸드폰 고정해 놓을 거.", "expected_intent": "implicit", "ground_truth": ["삼각대", "거치대"]},
  {"id": 58, "query": "독서실에서 쓸 소리 안 나는 슬리퍼.", "expected_intent": "implicit", "ground_truth": ["거실화", "슬리퍼"]},
  {"id": 59, "query": "음식물 쓰레기 냄새 안 나게 밀폐 잘 되는 통.", "expected_intent": "implicit", "ground_truth": ["음식물 쓰레기통", "밀폐 용기"]},
  {"id": 60, "query": "원룸인데 빨래 건조대 놓을 자리가 없어요.", "expected_intent": "implicit", "ground_truth": ["도어 후크 건조대", "미니 건조대"]},
  {"id": 61, "query": "5000원 이하로 중학생 여자애 생일 선물 추천해 줘.", "expected_intent": "implicit", "ground_truth": ["파우치", "핸드크림", "키링"]},
  {"id": 62, "query": "유치원 생일 답례품으로 돌릴 1000원짜리 간식거리.", "expected_intent": "implicit", "ground_truth": ["젤리", "사탕", "과자"]},
  {"id": 63, "query": "만원으로 욕실 청소 용품 풀세트 맞추고 싶어요.", "expected_intent": "implicit", "ground_truth": ["청소솔", "고무장갑", "세제"]},
  {"id": 64, "query": "3000원 안 넘는 선에서 차량용 방향제 있나요?", "expected_intent": "explicit", "ground_truth": ["차량용 방향제", "디퓨저"]},
  {"id": 65, "query": "군인 친구한테 보낼 건데 반입 가능한 화장품.", "expected_intent": "implicit", "ground_truth": ["올인원", "위장 크림", "선크림"]},
  {"id": 66, "query": "어르신들이 좋아할 만한 지압 용품 추천.", "expected_intent": "implicit", "ground_truth": ["지압봉", "효자손", "지압판"]},
  {"id": 67, "query": "AA 건전지 대용량으로 제일 싼 거.", "expected_intent": "explicit", "ground_truth": ["AA 건전지"]},
  {"id": 68, "query": "자취생인데 그릇 세트 말고 딱 하나만 산다면 제일 실용적인 거.", "expected_intent": "implicit", "ground_truth": ["나눔 접시", "덮밥 용기", "라면기"]},
  {"id": 69, "query": "일본 여행 가는데 110v 돼지코 2개만 필요해요.", "expected_intent": "explicit", "ground_truth": ["110v", "돼지코", "어댑터"]},
  {"id": 70, "query": "다이소 꿀템이라고 소문난 거 중에 뷰티 쪽 추천해 줘.", "expected_intent": "implicit", "ground_truth": ["퍼프", "브러시", "기름종이"]},
  {"id": 71, "query": "지금 당장 살 수 있는 할로윈 소품.", "expected_intent": "explicit", "ground_truth": ["할로윈", "머리띠", "바구니"]},
  {"id": 72, "query": "크리스마스 트리 장식 2만 원 안으로 해결하고 싶어.", "expected_intent": "explicit", "ground_truth": ["트리", "전구", "오너먼트"]},
  {"id": 73, "query": "국산 볼펜 중에 제일 잘 써지는 거.", "expected_intent": "explicit", "ground_truth": ["볼펜", "초저점도"]},
  {"id": 74, "query": "유리병 말고 안 깨지는 플라스틱 물병.", "expected_intent": "explicit", "ground_truth": ["물병", "보틀", "트라이탄"]},
  {"id": 75, "query": "색깔 별로 들어있는 고무줄 세트.", "expected_intent": "explicit", "ground_truth": ["고무줄", "머리끈"]},
  {"id": 76, "query": "A4 용지 들어가는 파일 홀더 10개 묶음.", "expected_intent": "explicit", "ground_truth": ["파일", "홀더", "클리어"]},
  {"id": 77, "query": "냄새 안 나는 무향 제습제.", "expected_intent": "explicit", "ground_truth": ["제습제"]},
  {"id": 78, "query": "캐리어에 붙일 만한 큰 스티커.", "expected_intent": "explicit", "ground_truth": ["스티커"]},
  {"id": 79, "query": "전자레인지랑 식기세척기 둘 다 되는 그릇.", "expected_intent": "explicit", "ground_truth": ["그릇", "용기", "도자기"]},
  {"id": 80, "query": "아이폰 충전 케이블인데 줄 긴 거(2m 이상).", "expected_intent": "explicit", "ground_truth": ["케이블", "8핀"]},
  {"id": 81, "query": "약간 카페 같은 분위기 내는 조명 없나?", "expected_intent": "implicit", "ground_truth": ["무드등", "전구", "스탠드"]},
  {"id": 82, "query": "방에서 나는 홀아비 냄새 잡는 거.", "expected_intent": "implicit", "ground_truth": ["디퓨저", "탈취제", "스프레이"]},
  {"id": 83, "query": "그... 뽁뽁이 말고 창문에 붙여서 단열하는 거.", "expected_intent": "implicit", "ground_truth": ["단열 시트", "방풍 비닐"]},
  {"id": 84, "query": "손에 뭐 안 묻히고 과자 집어 먹는 집게 같은 거.", "expected_intent": "implicit", "ground_truth": ["집게", "위생 장갑"]},
  {"id": 85, "query": "화장대 거울에 붙여서 밝게 만드는 전구.", "expected_intent": "implicit", "ground_truth": ["부착형 조명", "LED"]},
  {"id": 86, "query": "냉장고 옆면에 자석으로 붙여서 수납하는 거.", "expected_intent": "implicit", "ground_truth": ["자석", "마그넷", "후크"]},
  {"id": 87, "query": "싱크대 물 튀는 거 막아주는 투명한 판.", "expected_intent": "implicit", "ground_truth": ["물막이"]},
  {"id": 88, "query": "샤워기 물줄기 너무 세서 아픈데 부드럽게 나오는 헤드.", "expected_intent": "implicit", "ground_truth": ["샤워기 헤드", "필터"]},
  {"id": 89, "query": "책 읽을 때 페이지 안 넘어가게 잡아주는 거.", "expected_intent": "implicit", "ground_truth": ["독서대", "페이지 홀더", "북 클립"]},
  {"id": 90, "query": "컴퓨터 키보드 사이사이 먼지 빼내는 젤리 같은 거.", "expected_intent": "implicit", "ground_truth": ["젤리 클리너", "젤"]},
  {"id": 91, "query": "방바닥에 머리카락 굴러다니는 거 싫어서 슥슥 미는 거.", "expected_intent": "implicit", "ground_truth": ["청소포", "밀대", "돌돌이"]},
  {"id": 92, "query": "운동할 때 핸드폰 팔뚝에 차는 거.", "expected_intent": "implicit", "ground_truth": ["암밴드"]},
  {"id": 93, "query": "마스크 오래 쓰면 귀 아픈데 안 아프게 하는 고리.", "expected_intent": "implicit", "ground_truth": ["스트랩", "보호대"]},
  {"id": 94, "query": "후라이팬 코팅 안 벗겨지게 긁는 뒤집개.", "expected_intent": "implicit", "ground_truth": ["실리콘 뒤집개", "나무"]},
  {"id": 95, "query": "니트 옷걸이에 걸면 어깨 튀어나오는데 안 그러는 옷걸이.", "expected_intent": "implicit", "ground_truth": ["논슬립", "라운드 옷걸이"]},
  {"id": 96, "query": "욕실 슬리퍼 물 잘 빠지고 구멍 숭숭 뚫린 거.", "expected_intent": "implicit", "ground_truth": ["물빠짐", "욕실화", "슬리퍼"]},
  {"id": 97, "query": "이어폰 줄 꼬인 거 푸느라 짜증 나는데 감아두는 거.", "expected_intent": "implicit", "ground_truth": ["줄감개", "케이블 타이"]},
  {"id": 98, "query": "택배 송장 번호 개인정보 지우는 도장.", "expected_intent": "implicit", "ground_truth": ["롤러 스탬프", "지우개"]},
  {"id": 99, "query": "비누 거품 잘 나게 하는 망.", "expected_intent": "implicit", "ground_truth": ["거품망"]},
  {"id": 100, "query": "새우 껍질 까기 귀찮은데 쉽게 까는 도구.", "expected_intent": "implicit", "ground_truth": ["껍질 제거기", "쉬림프"]}
]

def parse_workflow_output(file_path):
    results = {}
    current_question = None
    current_data = {"intent": None, "extracted_products": [], "generated_keywords": []}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            q_match = re.search(r"--- \[Q\d+\] Customer asks: '(.*)' ---", line)
            if q_match:
                if current_question:
                    results[current_question] = current_data
                current_question = q_match.group(1)
                current_data = {"intent": None, "extracted_products": [], "generated_keywords": []}
                continue
                
            intent_match = re.search(r"-> Determined Intent: (.*)", line)
            if intent_match:
                current_data["intent"] = intent_match.group(1).strip()
                continue
                
            ep_match = re.search(r"-> Extracted Products: \[(.*)\]", line)
            if ep_match:
                content = ep_match.group(1)
                items = [item.strip().strip("'").strip('"') for item in content.split(',')]
                current_data["extracted_products"].extend([i for i in items if i])
                continue
                
            ip_match = re.search(r"-> Inferred Products: \[(.*)\]", line)
            if ip_match:
                content = ip_match.group(1)
                items = [item.strip().strip("'").strip('"') for item in content.split(',')]
                current_data["extracted_products"].extend([i for i in items if i])
                continue

            gk_match = re.search(r"-> Generated Keywords: \[(.*)\]", line)
            if gk_match:
                content = gk_match.group(1)
                items = [item.strip().strip("'").strip('"') for item in content.split(',')]
                current_data["generated_keywords"].extend([i for i in items if i])
                continue

        if current_question:
            results[current_question] = current_data
    except Exception as e:
        print(f"Error parsing log file: {e}")
        
    return results

def generate_report(output_file):
    parsed_results = parse_workflow_output(output_file)
    total_questions = len(QUESTION_DATA)
    intent_correct = 0
    keyword_match_count = 0
    
    # Pre-calc metrics
    for item in QUESTION_DATA:
        q_text = item["query"]
        expected_intent = item["expected_intent"]
        ground_truth_keywords = [k.replace(" ", "") for k in item["ground_truth"]]
        
        if q_text not in parsed_results:
            continue
            
        result = parsed_results[q_text]
        actual_intent = result["intent"]
        all_found = result["extracted_products"] + result["generated_keywords"]
        all_found_norm = [k.replace(" ", "") for k in all_found]
        
        if actual_intent == expected_intent:
            intent_correct += 1
            
        for gt in ground_truth_keywords:
            match = False
            for found in all_found_norm:
                if gt in found or found in gt:
                    match = True
                    break
            if match:
                keyword_match_count += 1
                break

    intent_accuracy = (intent_correct / total_questions) * 100
    keyword_accuracy = (keyword_match_count / total_questions) * 100

    detailed_report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nlu_detailed_report.txt")
    detailed_lines = []
    detailed_lines.append(f"=== NLU Detailed Performance Report (All Questions) ===")
    detailed_lines.append(f"Total Questions: {total_questions}")
    detailed_lines.append(f"Intent Accuracy: {intent_accuracy:.2f}%")
    detailed_lines.append(f"Keyword Accuracy: {keyword_accuracy:.2f}%")
    detailed_lines.append("="*80)
    detailed_lines.append(f"{'ID':<4} | {'Query':<50} | {'Exp. Intent':<10} | {'Act. Intent':<10} | {'Intent Check':<12} | {'Keyword Check':<12}")
    detailed_lines.append("-" * 120)

    for item in QUESTION_DATA:
        q_id = item["id"]
        q_text = item["query"]
        expected_intent = item["expected_intent"]
        ground_truth_keywords = [k.replace(" ", "") for k in item["ground_truth"]]
        
        q_display = (q_text[:47] + '...') if len(q_text) > 50 else q_text
        
        if q_text not in parsed_results:
             detailed_lines.append(f"{q_id:<4} | {q_display:<50} | {expected_intent:<10} | {'MISSING':<10} | {'FAIL':<12} | {'FAIL':<12}")
             continue

        result = parsed_results[q_text]
        actual_intent = result["intent"]
        all_found_keywords = result["extracted_products"] + result["generated_keywords"]
        all_found_keywords_norm = [k.replace(" ", "") for k in all_found_keywords]

        intent_status = "PASS" if actual_intent == expected_intent else "FAIL"
        
        keyword_status = "FAIL"
        for gt in ground_truth_keywords:
            for found in all_found_keywords_norm:
                if gt in found or found in gt:
                    keyword_status = "PASS"
                    break
            if keyword_status == "PASS":
                break
        
        detailed_lines.append(f"{q_id:<4} | {q_display:<50} | {expected_intent:<10} | {actual_intent:<10} | {intent_status:<12} | {keyword_status:<12}")

        if intent_status == "FAIL" or keyword_status == "FAIL":
             detailed_lines.append(f"   [DETAILS] GT Keywords: {item['ground_truth']}")
             detailed_lines.append(f"   [DETAILS] Extracted:   {all_found_keywords[:6]}...")
             if intent_status == "FAIL":
                  detailed_lines.append(f"   [NOTE] Intent Mismatch: Expected '{expected_intent}' but got '{actual_intent}'")
             detailed_lines.append("-" * 120)

    with open(detailed_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(detailed_lines))
    print(f"DONE: {detailed_report_path}")

if __name__ == "__main__":
    # Hardcoded log path to known location
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logic", "workflow_output copy 3.txt")
    generate_report(log_path)
