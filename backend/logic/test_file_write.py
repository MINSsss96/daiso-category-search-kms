
try:
    with open(r"c:\Users\301\.gemini\antigravity\brain\a27faff9-e48f-43c0-ae9f-1416794f6234\test_output_check.txt", "w") as f:
        f.write("Python is running and can write to file.")
    print("File written.")
except Exception as e:
    print(f"Error: {e}")
