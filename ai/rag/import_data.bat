@echo off
echo ===============================================
echo    Import Knowledge Graph NMAP-AI
echo ===============================================
echo.

REM Verifier Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker non installe !
    pause
    exit /b 1
)

echo [1] Docker trouve

REM Verifier fichier existe
if not exist "NMAP_AI_NEO4J_DATA.zip" (
    echo [ERREUR] NMAP_AI_NEO4J_DATA.zip non trouve !
    pause
    exit /b 1
)

echo [2] Fichier backup trouve

REM Dezipper
echo [3] Decompression...
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe Expand-Archive -Path NMAP_AI_NEO4J_DATA.zip -DestinationPath . -Force

echo [4] Lancement Neo4j...
docker-compose up -d

echo [5] Attente demarrage (30 sec)...
ping 127.0.0.1 -n 31 >nul

echo [6] Arret pour import...
docker-compose stop

echo [7] Copie donnees...
docker cp neo4j_data/. nmap-ai-neo4j:/data/

echo [8] Redemarrage...
docker-compose up -d

echo [9] Attente (20 sec)...
ping 127.0.0.1 -n 21 >nul

echo.
echo ===============================================
echo     IMPORT TERMINE !
echo ===============================================
echo.
echo Interface : http://localhost:7474
echo Username  : neo4j
echo Password  : nmap_ai_2024
echo.
pause