@echo off
cd /d "%~dp0"
set PORT=10000
.venv\Scripts\python.exe -m streamlit run app.py --server.port=%PORT% --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
pause
