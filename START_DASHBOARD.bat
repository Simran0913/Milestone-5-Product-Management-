@echo off
cd /d "%~dp0"
echo ============================================
echo Milestone 5 - Frontend Dashboard
echo ============================================
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Creating it...
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Could not create Python 3.12 environment.
    echo Install Python 3.12 or use the VS Code terminal instructions in README_BEGINNER.md.
    pause
    exit /b 1
  )
)
echo Installing/checking project libraries...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Library installation failed. Check your internet connection and Python installation.
  pause
  exit /b 1
)
echo Starting dashboard in your browser...
".venv\Scripts\python.exe" -m streamlit run dashboard.py
pause
