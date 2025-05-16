@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo =======================================================
echo        YouTube字幕和描述下载工具 - 简单版本
echo =======================================================
echo.

if "%~1"=="" (
    echo 请提供包含YouTube链接的文本文件路径
    echo 用法: download_subtitles.bat [文件路径]
    echo 例如: download_subtitles.bat youtube视频链接/links.txt
    pause
    exit /b
)

if not exist "%~1" (
    echo 错误: 找不到文件 "%~1"
    echo 请确认文件路径是否正确
    pause
    exit /b
)

echo 正在启动下载程序...
echo.

python youtube_subtitle_downloader.py "%~1"

echo.
echo 程序执行完毕。结果保存在 subtitles 文件夹中。
echo.
pause 