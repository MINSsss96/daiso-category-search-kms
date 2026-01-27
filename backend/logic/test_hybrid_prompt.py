
import sys
import os

# Add logic dir to path to import simple_keyword_extractor copy
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function from the module
# Note: The file name has spaces, so we might need to use importlib or rename it temporarily. 
# But for now let's try standard import if possible, or use importlib.
import importlib.util
spec = importlib.util.spec_from_file_location("extractor", "simple_keyword_extractor copy.py")
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)

test_queries = [
    "붙였다 떼도 자국 안 남는 거 뭐 있어요?",  # Target: 몬스터클리어젤
    "물기 금방 마르는 딱딱한 발매트",           # Target: 규조토발매트
    "싱크대 물 튀는거 막아주는 판",             # Target: 싱크대물막이
    "옷장 안에 넣어두는 습기 제거제"            # Target: 제습제 (General)
]

def run_tests():
    print("Running Hybrid Prompt Tests...")
    for q in test_queries:
        print(f"\nQuery: {q}")
        result = extractor.extract_keyword(q)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Keyword: {result['keyword']}")
            # We can't easily see the reasoning unless we modify the extractor to return it, 
            # but currently it only returns the keyword. 
            # Ideally we check if keyword matches expected.

if __name__ == "__main__":
    run_tests()
