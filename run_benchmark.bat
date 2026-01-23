@echo off
cd /d c:\Users\301\dev\daiso-category-search
venv\Scripts\python.exe -u backend/experiments/benchmark_performance.py > benchmark_output.log 2>&1
echo Done executing benchmark.
