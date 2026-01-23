
import os
import sys

def log(msg):
    with open("startup_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("Step 1: Importing builtin modules...")

log("Step 2: Importing local logic...")
try:
    from backend.logic.nlu import analyze_text
    log("Success: backend.logic.nlu imported")
except Exception as e:
    log(f"Error importing backend.logic.nlu: {e}")

log("Step 3: Importing local api...")
try:
    from backend.api import app
    log("Success: backend.api imported")
except Exception as e:
    log(f"Error importing backend.api: {e}")

log("Debug complete.")
