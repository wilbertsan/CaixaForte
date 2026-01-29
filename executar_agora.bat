@echo off
title Caixa Forte - Execucao Manual
cd /d "%~dp0"
echo ========================================
echo   CAIXA FORTE - Execucao Manual
echo   Processando emails e PDFs agora...
echo ========================================
echo.

REM Ativa o ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Executa uma vez
python -c "from scheduler import executar_professor_pardal; executar_professor_pardal()"

echo.
echo Execucao concluida!
pause
