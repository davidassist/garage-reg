@echo off
REM Windows batch script to start production server

echo Starting GarageReg API Production Server...

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%\..

REM Change to project directory  
cd /d "%PROJECT_ROOT%"

REM Load environment variables if .env exists
if exist ".env" (
    echo Loading environment from .env
    for /f "usebackq tokens=1,* delims==" %%i in (".env") do (
        if not "%%i"=="" if not "%%i:~0,1%"=="#" set "%%i=%%j"
    )
)

REM Default values
if not defined HOST set HOST=0.0.0.0
if not defined PORT set PORT=8000
if not defined WORKERS set WORKERS=4

echo Starting production server with %WORKERS% workers
echo Server listening on http://%HOST%:%PORT%
echo Health check: http://%HOST%:%PORT%/healthz
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start gunicorn
gunicorn app.main:app --bind %HOST%:%PORT% --workers %WORKERS% --worker-class uvicorn.workers.UvicornWorker --log-level info --access-logfile - --error-logfile -