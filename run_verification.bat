@echo off
cd /d c:\Users\301\dev\daiso-category-search
venv\Scripts\python.exe backend\analytics\generate_report_standalone.py > backend\analytics\execution.log 2>&1
echo Done executing script.
