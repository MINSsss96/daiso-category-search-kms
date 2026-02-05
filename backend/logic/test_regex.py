import re

line = "Q: 손에 안 묻히고 버리는 거 있어요? -> Keyword: 청소집게 (Gemini Latency: 1.006s, Tokens: [P:2537, C:33, T:2570])"
match = re.search(r'Keyword:\s*([^(]+)\s*\(', line)
with open("debug_regex.txt", "w", encoding="utf-8") as f:
    if match:
        f.write(f"Match: '{match.group(1).strip()}'")
    else:
        f.write("No match")
