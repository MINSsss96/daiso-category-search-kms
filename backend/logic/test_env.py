
import sys

LOG_FILE = r"c:\Users\301\.gemini\antigravity\brain\a27faff9-e48f-43c0-ae9f-1416794f6234\env_test_result.txt"

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")
    except Exception as e:
        print(f"Log fail: {e}")

log("Starting env test...")
log(f"Python version: {sys.version}")

try:
    import openai
    log(f"Imported openai: {openai.__file__}")
except ImportError as e:
    log(f"Failed to import openai: {e}")

try:
    import dotenv
    log(f"Imported dotenv: {dotenv.__file__}")
except ImportError as e:
    log(f"Failed to import dotenv: {e}")

log("Env test complete.")
