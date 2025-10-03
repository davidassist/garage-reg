@echo off
REM Windows batch script to start development server

echo Starting GarageReg API Development Server...

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

echo Starting server on http://%HOST%:%PORT%
echo Docs available at: http://%HOST%:%PORT%/docs
echo Health check: http://%HOST%:%PORT%/healthz
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start uvicorn
uvicorn app.main:app --host %HOST% --port %PORT% --reload --log-level info