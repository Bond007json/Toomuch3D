@echo off
setlocal
cd /d "%~dp0"
echo Toomuch3D diagnostics
echo =====================
echo.
where py
where python
echo.
if exist ".venv\Scripts\python.exe" (
  echo Virtual environment: FOUND
  ".venv\Scripts\python.exe" --version
  ".venv\Scripts\python.exe" -c "import fastapi,uvicorn; print('FastAPI/Uvicorn: OK')"
) else (
  echo Virtual environment: NOT FOUND
)
echo.
echo Checking port 8000...
netstat -ano | findstr ":8000"
echo.
echo If no LISTENING line appears above, the Toomuch3D server is not running.
pause
