@echo off
REM =====================================================
REM NMAP-AI - Installation des dépendances
REM =====================================================

echo.
echo =====================================================
echo  🚀 NMAP-AI - Installation des dépendances
echo =====================================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Python n'est pas installé ou pas dans le PATH
    echo    Installez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python détecté
python --version
echo.

REM Upgrade pip
echo ⏳ Mise à jour de pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  Attention: pip ne s'est pas mis à jour correctement
)
echo.

REM Installer les dépendances principales
echo ⏳ Installation des dépendances principales...
echo.

echo [1/5] Installation de mcp (Model Context Protocol)...
python -m pip install mcp>=0.6.0
if errorlevel 1 (
    echo ❌ ERREUR lors de l'installation de mcp
    pause
    exit /b 1
)
echo ✅ mcp installé

echo.
echo [2/5] Installation de FastAPI et Uvicorn...
python -m pip install fastapi>=0.104.0 uvicorn>=0.24.0
if errorlevel 1 (
    echo ⚠️  ERREUR partiel
)
echo ✅ FastAPI/Uvicorn installés

echo.
echo [3/5] Installation de pydantic et httpx...
python -m pip install pydantic>=2.0.0 httpx>=0.24.0
if errorlevel 1 (
    echo ⚠️  ERREUR partiel
)
echo ✅ pydantic/httpx installés

echo.
echo [4/5] Installation de Flask et CORS...
python -m pip install Flask>=3.0.0 flask-cors>=4.0.0
if errorlevel 1 (
    echo ⚠️  ERREUR partiel
)
echo ✅ Flask installé

echo.
echo [5/5] Installation des autres dépendances...
python -m pip install scikit-learn pandas numpy joblib spacy requests
if errorlevel 1 (
    echo ⚠️  ERREUR partiel
)
echo ✅ Autres dépendances installées

echo.
echo =====================================================
echo ✅ INSTALLATION COMPLÈTE!
echo =====================================================
echo.
echo 🎯 Prochaines étapes:
echo    1. Vérifier que tout fonctionne
echo    2. Lancer: python server.py
echo    3. En autre terminal: python app_flask.py
echo    4. Ouvrir: http://localhost:5000
echo.
pause