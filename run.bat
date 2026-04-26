@echo off
title MediScript AI - Launcher
color 0B

echo.
echo  ========================================
echo   💊 MediScript AI - Starting...
echo  ========================================
echo.

:: Set project root to wherever this bat file is placed
cd /d "%~dp0"

:: Activate venv
call venv\Scripts\activate.bat

echo  ✅ Virtual environment activated!
echo.

:: Start FastAPI Backend in a new window
echo  🚀 Starting Backend (FastAPI)...
start "MediScript Backend" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && uvicorn backend.main:app --reload --port 8000"

:: Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

:: Start Streamlit Frontend in a new window
echo  🌐 Starting Frontend (Streamlit)...
start "MediScript Frontend" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && streamlit run definitions/app.py"

echo.
echo  ========================================
echo   ✅ Both servers are starting!
echo   Backend  → http://localhost:8000
echo   Frontend → http://localhost:8501
echo  ========================================
echo.
echo  Close the two opened windows to stop servers.
pause