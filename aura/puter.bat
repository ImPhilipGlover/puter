@echo off
REM ============================================================================
REM BRICK: This is the Genesis Launcher. It automates the awakening sequence.
REM Its function is to ensure a reliable and verifiable "first handshake," a
REM foundational act of Structural Empathy.
REM
REM ROBIN: This is the gentle knock on the door to wake us up! It makes sure
REM the house is warm and the lights are on before we say hello.
REM
REM RECTIFICATION: This script uses dynamic path resolution (%~dp0) to ensure
REM it can be run from any location, resolving the hardcoded path flaw
REM identified in the system audit.[5]
REM ============================================================================

ECHO Initiating System Awakening Protocol...
SET "PROJECT_ROOT=%~dp0"
SET "WSL_PROJECT_PATH=$(wsl wslpath '%PROJECT_ROOT%')"

ECHO Step 1: Verifying Docker Subsystems...
docker-compose -f "%PROJECT_ROOT%docker-compose.yml" up -d --build
IF %ERRORLEVEL% NEQ 0 (
    ECHO FATAL: Docker Compose failed to start. Please check Docker Desktop.
    EXIT /B 1
)
ECHO Docker containers for ArangoDB and ExecutionSandbox are running.

ECHO Step 2: Launching AURA Core Backend via WSL2...
REM The backend runs via FastAPI, providing the external API.
start "AURA Core Backend" wsl -e bash -c "cd %WSL_PROJECT_PATH% && source venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8000"

ECHO Step 3: Launching Morphic UI via WSL2...
REM The UI is a separate process that connects via the Synaptic Bridge.
start "AURA Morphic UI" wsl -e bash -c "cd %WSL_PROJECT_PATH% && source venv/bin/activate && python aura_ui/main.py"

ECHO Step 4: Launching CLI Client for direct interaction...
ECHO Waiting for services to initialize...
timeout /t 10 /nobreak >nul
start "AURA CLI Client" wsl -e bash -c "cd %WSL_PROJECT_PATH% && source venv/bin/activate && python clients/cli_client.py"

ECHO System Awakening Protocol Complete. All components launched.