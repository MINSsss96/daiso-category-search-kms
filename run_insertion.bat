@echo off
echo Starting batch execution... > c:\Users\301\dev\daiso-category-search\backend\database\batch_debug.txt
c:\Users\301\dev\daiso-category-search\venv\Scripts\python.exe c:\Users\301\dev\daiso-category-search\backend\database\insert_mock_data.py >> c:\Users\301\dev\daiso-category-search\backend\database\batch_debug.txt 2>&1
echo Finished execution. >> c:\Users\301\dev\daiso-category-search\backend\database\batch_debug.txt
