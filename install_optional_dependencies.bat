@echo off
REM =====================================================
REM NMAP-AI - Installation des dépendances OPTIONNELLES
REM =====================================================

echo.
echo =====================================================
echo  🚀 Installation des dépendances OPTIONNELLES
echo  (transformers + torch pour meilleurs générateurs)
echo =====================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Python n'est pas trouvé
    pause
    exit /b 1
)

echo ✅ Python détecté
python --version
echo.

REM Mettre à jour pip
echo ⏳ Mise à jour de pip...
python -m pip install --upgrade pip
echo.

REM Installer transformers
echo ⏳ Installation de transformers (pour Medium Generator)...
python -m pip install transformers
if errorlevel 1 (
    echo ⚠️  ERREUR lors de l'installation de transformers
    echo    Continuant quand même...
)
echo ✅ transformers installé
echo.

REM Installer torch
echo ⏳ Installation de torch (pour Hard Generator)...
echo    (Attention: ~2-3 GB de données)
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo ⚠️  ERREUR lors de l'installation de torch
    echo    Continuant quand même...
)
echo ✅ torch installé
echo.

REM Vérifier l'installation
echo =====================================================
echo ✅ VÉRIFICATION
echo =====================================================
echo.

python -c "import transformers; print('✅ transformers OK')" 2>nul
if errorlevel 1 (
    echo ⚠️  transformers: Installation incomplète
) else (
    echo ✅ transformers: Prêt!
)

python -c "import torch; print('✅ torch OK (version: ' + torch.__version__ + ')')" 2>nul
if errorlevel 1 (
    echo ⚠️  torch: Installation incomplète
) else (
    echo ✅ torch: Prêt!
)

echo.
echo =====================================================
echo ✅ INSTALLATION COMPLÈTE!
echo =====================================================
echo.
echo 🎯 Prochaines étapes:
echo    1. Relancer server.py
echo    2. Les générateurs Medium/Hard devraient marcher
echo    3. Testez avec des requêtes MEDIUM et HARD
echo.
pause