@echo off
cd /d "%~dp0"
echo Milestone 5 - Collect reviews and create reports
if not exist ".venv\Scripts\python.exe" (
  echo Please first run START_DASHBOARD.bat to set up the environment.
  pause
  exit /b 1
)
echo.
echo Step 1: Collect public reviews...
".venv\Scripts\python.exe" collect_reviews.py
if errorlevel 1 (
  echo Review collection failed. Read the error above; no fake reviews will be created.
  pause
  exit /b 1
)
echo.
echo Step 2: Analyze and create reports...
".venv\Scripts\python.exe" run_pipeline.py
if errorlevel 1 (
  echo Pipeline stopped. There may be zero usable reviews; check data/reviews.csv.
  pause
  exit /b 1
)
echo.
echo Done. Check the outputs folder, then refresh the dashboard in your browser.
pause
