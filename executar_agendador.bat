@echo off
title Caixa Forte - Agendador
cd /d "%~dp0"
echo ========================================
echo   CAIXA FORTE - Agendador de Tarefas
echo   Professor Pardal em modo automatico
echo ========================================
echo.

REM Ativa o ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Executa o agendador
python scheduler.py

pause
