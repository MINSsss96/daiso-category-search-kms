
print("Step 1: Importing builtin modules...")
import os
import sys

print("Step 2: Importing local logic...")
try:
    from backend.logic.nlu import analyze_text
    print("Success: backend.logic.nlu imported")
except Exception as e:
    print(f"Error importing backend.logic.nlu: {e}")

print("Step 3: Importing local api...")
try:
    from backend.api import app
    print("Success: backend.api imported")
except Exception as e:
    print(f"Error importing backend.api: {e}")

print("Debug complete.")
