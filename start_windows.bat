@echo off
setlocal
cd /d "%~dp0"
title Toomuch3D Server
echo.
echo ========================================
echo          Toomuch3D Local Server
echo ========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python was not found.
    echo Install Python 3.10 or 3.11 and enable "Add Python to PATH".
    pause
    exit /b 1
  )
  set "PY=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating Python virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 goto :fail
)

echo [2/4] Activating environment...
call ".venv\Scripts\activate.bat"

echo [3/4] Installing/updating web dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto :fail

if not exist ".env" (
  echo [INFO] No .env file found. The browser will open, but Hi3D generation
  echo        will remain unavailable until the model paths are configured.
)

echo [4/4] Starting Toomuch3D...
echo.
echo Browser: http://127.0.0.1:8000/
echo API docs: http://127.0.0.1:8000/docs
echo.
echo KEEP THIS WINDOW OPEN while using Toomuch3D.
echo Press CTRL+C to stop the server.
echo.

start "" "http://127.0.0.1:8000/"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo Toomuch3D server stopped.
pause
exit /b 0

:fail
echo.
echo ERROR: Toomuch3D setup failed. Read the error above.
pause
exit /b 1
