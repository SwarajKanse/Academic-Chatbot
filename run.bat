@echo off
title Intelligent Study Assistant
echo =========================================================
echo    Starting Intelligent Study Assistant (Streamlit)
echo =========================================================
cd /d "%~dp0"
python -m streamlit run app.py --server.port 8501 --server.headless false
pause
