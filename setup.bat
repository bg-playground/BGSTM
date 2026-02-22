@echo off
setlocal EnableDelayedExpansion

:: ---------------------------------------------------------------------------
:: BGSTM One-Command Setup Script (Windows)
:: ---------------------------------------------------------------------------

echo.
echo   ██████   ██████  ███████ ████████ ███    ███
echo   ██   ██ ██       ██         ██    ████  ████
echo   ██████  ██   ███ ███████    ██    ██ ████ ██
echo   ██   ██ ██    ██      ██    ██    ██  ██  ██
echo   ██████   ██████  ███████    ██    ██      ██
echo.
echo   BGSTM One-Command Installer
echo   -------------------------------------------------
echo.

:: ---------------------------------------------------------------------------
:: 1. Check requirements: Docker
:: ---------------------------------------------------------------------------
echo [INFO]  Checking requirements...

where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed.
    echo.
    echo   Please install Docker Desktop:
    echo     https://docs.docker.com/desktop/install/windows-install/
    echo.
    pause
    exit /b 1
)

docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker daemon is not running.
    echo   Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

:: Support both 'docker compose' (v2) and 'docker-compose' (v1)
set DC=docker compose
docker compose version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where docker-compose >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Docker Compose is not available.
        echo.
        echo   Please install Docker Desktop ^(which includes Docker Compose^):
        echo     https://docs.docker.com/desktop/install/windows-install/
        echo.
        pause
        exit /b 1
    )
    set DC=docker-compose
)

for /f "tokens=3" %%v in ('docker --version') do (
    set DOCKER_VER=%%v
)
set DOCKER_VER=!DOCKER_VER:,=!
echo [OK]    Docker !DOCKER_VER! and Docker Compose found.

:: ---------------------------------------------------------------------------
:: 2. Copy .env.example -> .env (idempotent)
:: ---------------------------------------------------------------------------
cd /d "%~dp0"

if exist ".env" (
    echo [WARN]  .env already exists -- skipping copy ^(using existing file^).
) else (
    if not exist ".env.example" (
        echo [ERROR] .env.example not found.
        echo   Are you running this script from the BGSTM root directory?
        pause
        exit /b 1
    )
    copy ".env.example" ".env" >nul
    echo [OK]    Created .env from .env.example.
)

:: ---------------------------------------------------------------------------
:: 3. Start all services
:: ---------------------------------------------------------------------------
echo [INFO]  Starting services with Docker Compose...
echo         ^(this may take a few minutes on first run^)
echo.
%DC% up -d --build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose failed to start services.
    echo   Check the output above for details.
    pause
    exit /b 1
)
echo [OK]    Docker Compose services started.

:: ---------------------------------------------------------------------------
:: 4. Health checks
:: ---------------------------------------------------------------------------
set TIMEOUT=120
set INTERVAL=5

echo [INFO]  Waiting for Backend API to be ready...
call :wait_for "http://localhost:8000/health" %TIMEOUT% %INTERVAL%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend API did not become ready within %TIMEOUT%s.
    echo.
    echo   Troubleshooting tips:
    echo     - Check logs:   %DC% logs -f
    echo     - Common cause: port 8000 already in use
    echo     - Try:          %DC% down ^&^& %DC% up -d --build
    pause
    exit /b 1
)
echo [OK]    Backend API is ready.

echo [INFO]  Waiting for Frontend to be ready...
call :wait_for "http://localhost" %TIMEOUT% %INTERVAL%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend did not become ready within %TIMEOUT%s.
    echo.
    echo   Troubleshooting tips:
    echo     - Check logs:   %DC% logs -f
    echo     - Common cause: port 80 already in use
    echo     - Try:          %DC% down ^&^& %DC% up -d --build
    pause
    exit /b 1
)
echo [OK]    Frontend is ready.

:: ---------------------------------------------------------------------------
:: 5. Optional: load sample data
:: ---------------------------------------------------------------------------
echo.
set /p LOAD_SAMPLE="Load sample data? (y/n) "
echo.
if /i "!LOAD_SAMPLE!"=="y" (
    echo [INFO]  Loading sample data...
    %DC% exec backend python -m app.db.sample_data
    if %ERRORLEVEL% NEQ 0 (
        echo [WARN]  Sample data load encountered an error.
        echo         You can try again later with:
        echo           %DC% exec backend python -m app.db.sample_data
    ) else (
        echo [OK]    Sample data loaded.
    )
) else (
    echo [INFO]  Skipping sample data.
)

:: ---------------------------------------------------------------------------
:: 6. Open browser
:: ---------------------------------------------------------------------------
echo [INFO]  Opening browser at http://localhost ...
start "" "http://localhost"

:: ---------------------------------------------------------------------------
:: 7. Summary
:: ---------------------------------------------------------------------------
echo.
echo ================================================
echo   BGSTM is up and running!
echo ================================================
echo.
echo   Frontend:    http://localhost
echo   Backend API: http://localhost:8000
echo   API Docs:    http://localhost:8000/docs
echo.
echo   Stop services:  %DC% down
echo   View logs:      %DC% logs -f
echo.
pause
exit /b 0

:: ---------------------------------------------------------------------------
:: Subroutine: wait_for <url> <timeout_seconds> <interval_seconds>
:: Returns 0 on success, 1 on timeout
:: ---------------------------------------------------------------------------
:wait_for
set _URL=%~1
set _TIMEOUT=%~2
set _INTERVAL=%~3
set _ELAPSED=0

:wait_loop
curl -sf --max-time 3 "%_URL%" >nul 2>&1
if %ERRORLEVEL% EQU 0 exit /b 0
if !_ELAPSED! GEQ %_TIMEOUT% exit /b 1
timeout /t %_INTERVAL% /nobreak >nul
set /a _ELAPSED=!_ELAPSED!+%_INTERVAL%
echo     ... !_ELAPSED!s / %_TIMEOUT%s
goto wait_loop
