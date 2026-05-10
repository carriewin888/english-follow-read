@echo off
chcp 65001 >nul
title 英语跟读评分服务
cd /d D:\BN\Future\english
set PATH=%PATH%;D:\BN\Future\english\tools\ffmpeg-master-latest-win64-gpl\bin
echo.
echo ========================================
echo   英语跟读评分服务启动中...
echo   请等待 Whisper 模型加载（约30秒）
echo ========================================
echo.
D:\BN\Future\english\venv\Scripts\python.exe -m uvicorn hf_score_service:app --host 0.0.0.0 --port 8000 --reload
