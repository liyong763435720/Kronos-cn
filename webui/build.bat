@echo off
chcp 65001 >nul
title Kronos WebUI 打包工具

echo ================================================
echo   Kronos WebUI 打包工具
echo ================================================
echo.

:: ── 切换到 webui 目录 ────────────────────────────────────────────────
cd /d "%~dp0"

:: ── 检查 Python ──────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11
    pause & exit /b 1
)

:: ── 检查 PyInstaller ─────────────────────────────────────────────────
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 ( echo [错误] PyInstaller 安装失败 & pause & exit /b 1 )
)

:: ── 检查 Inno Setup（尝试常见安装路径）──────────────────────────────
set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC=C:\Program Files\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set ISCC=C:\Program Files (x86)\Inno Setup 5\ISCC.exe
)

if "%ISCC%"=="" (
    echo [警告] 未找到 Inno Setup，将只生成文件夹版本，不打包成安装程序
    echo         如需安装程序请从 https://jrsoftware.org/isdl.php 下载 Inno Setup
    echo.
    set SKIP_INNO=1
) else (
    set SKIP_INNO=0
    echo [OK] 找到 Inno Setup：%ISCC%
)

echo.
echo ── 步骤 1/3：清理旧的打包输出 ──────────────────────────────────
if exist dist\KronosWebUI ( rmdir /s /q dist\KronosWebUI )
if exist build            ( rmdir /s /q build )
echo [OK] 清理完成

echo.
echo ── 步骤 2/3：PyInstaller 打包（预计 5-15 分钟）────────────────
pyinstaller kronos_webui.spec --noconfirm
if errorlevel 1 (
    echo [错误] PyInstaller 打包失败，请检查上方错误信息
    pause & exit /b 1
)
echo [OK] PyInstaller 打包完成 → dist\KronosWebUI\

echo.
echo ── 步骤 3/3：Inno Setup 打包成安装程序 ─────────────────────────
if "%SKIP_INNO%"=="1" (
    echo [跳过] 未安装 Inno Setup
    echo.
    echo ================================================
    echo   打包完成！
    echo   可运行版本：dist\KronosWebUI\KronosWebUI.exe
    echo   （将整个 dist\KronosWebUI 文件夹复制到目标电脑即可）
    echo ================================================
) else (
    "%ISCC%" installer.iss
    if errorlevel 1 (
        echo [错误] Inno Setup 打包失败
        pause & exit /b 1
    )
    echo.
    echo ================================================
    echo   打包完成！
    echo   安装程序：dist\KronosWebUI_Setup.exe
    echo   （复制此单个文件到目标电脑，双击安装即可）
    echo ================================================
)

echo.
pause
