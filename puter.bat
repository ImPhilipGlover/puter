:: /puter/puter.bat
@echo off
setlocal

:: RECTIFICATION: Using %~dp0 ensures the script uses the directory it's located in,
:: making it portable and resolving the hardcoded path failure.
set "PROJECT_DIR=%~dp0aura"
set "WSL_PROJECT_DIR=$(wslpath '%PROJECT_DIR%')"

echo ======================================================
echo == AURA GENESIS PROTOCOL LAUNCHER
echo == Project Directory: %PROJECT_DIR%
echo == WSL Path: %WSL_PROJECT_DIR%
echo ======================================================

echo.
echo Checking for running Docker containers...
docker ps -a --filter "name=aura_" --format "{{.Names}}" | findstr "aura_" > nul
if %errorlevel%==0 (
    echo Found existing AURA containers. Stopping and removing...
    docker stop aura_arangodb aura_execution_sandbox > nul
    docker rm aura_arangodb aura_execution_sandbox > nul
    echo Old containers removed.
) else (
    echo No existing AURA containers found.
)

echo.
echo "Starting Docker services (ArangoDB & Execution Sandbox)..."
cd /d "%PROJECT_DIR%"
wsl -e bash -c "cd %WSL_PROJECT_DIR% && docker-compose up -d"
if %errorlevel% neq 0 (
    echo Docker Compose failed to start. Aborting.
    exit /b 1
)
echo Docker services started successfully. Waiting for ArangoDB to initialize...
timeout /t 15 > nul

echo.
echo Running the one-time Genesis script in WSL...
wsl -e bash -c "cd %WSL_PROJECT_DIR% && source venv/bin/activate && python genesis.py"
if %errorlevel% neq 0 (
    echo Genesis script failed. Check WSL environment and Python dependencies. Aborting.
    exit /b 1
)
echo Genesis script completed.

echo.
echo Launching the AURA Core API Server in a new window...
start "AURA Core" cmd /k wsl.exe --cd "%PROJECT_DIR%" bash -c "source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8000"

echo.
echo Launching the CLI Client in a new window...
timeout /t 5 > nul
start "AURA CLI" cmd /k wsl.exe --cd "%PROJECT_DIR%" bash -c "source venv/bin/activate && python clients/cli_client.py"

echo.
echo ======================================================
echo == AURA System Genesis sequence initiated.
echo == Monitor the 'AURA Core' and 'AURA CLI' windows.
echo ======================================================

endlocal