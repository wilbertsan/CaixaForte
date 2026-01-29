@echo off
title Caixa Forte - Telegram Bot
echo ========================================
echo    Caixa Forte - Bot do Telegram
echo ========================================
echo.

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [AVISO] Virtual environment nao encontrado, usando Python global
)

echo Iniciando bot...
echo Pressione Ctrl+C para parar.
echo.

python telegram_bot.py

pause
