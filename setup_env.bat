@echo off
REM 跨平台虚拟环境设置脚本 (Windows)
REM 支持 Windows CMD 和 PowerShell

setlocal enabledelayedexpansion

echo ======================================
echo   跨平台虚拟环境设置脚本 (Windows)
echo ======================================
echo.

REM 检查 Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

echo 错误: 未找到 Python。请先安装 Python 3.9+
exit /b 1

:python_found
echo 使用 Python: !PYTHON_CMD!
!PYTHON_CMD! --version
echo.

REM 删除旧的虚拟环境
if exist "venv" (
    echo 检测到已存在的虚拟环境目录
    set /p RECREATE="是否删除并重新创建? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo 正在删除旧的虚拟环境...
        rmdir /s /q venv
    ) else (
        echo 保留现有虚拟环境
        if exist "venv\Scripts\activate.bat" (
            echo 虚拟环境已存在，跳过创建
            goto :install_deps
        ) else (
            echo 现有虚拟环境不完整，请删除后重试
            exit /b 1
        )
    )
)

REM 创建新的虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    !PYTHON_CMD! -m venv venv

    if !errorlevel! equ 0 (
        echo [OK] 虚拟环境创建成功
    ) else (
        echo [ERROR] 虚拟环境创建失败
        exit /b 1
    )
)

:install_deps
REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级 pip
echo 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 安装项目依赖...
if exist "requirements.txt" (
    pip install -r requirements.txt
) else if exist "venv_requirements.txt" (
    pip install -r venv_requirements.txt
) else (
    echo 警告: 未找到 requirements.txt 或 venv_requirements.txt
)

REM 安装 Playwright 浏览器
echo 安装 Playwright 浏览器...
playwright install

echo.
echo ======================================
echo   [OK] 设置完成！
echo ======================================
echo.
echo 使用说明:
echo   1. 激活虚拟环境:
echo      venv\Scripts\activate.bat
echo.
echo   2. 运行测试:
echo      pytest test_case/UI/Test_Katana/test_ui.py -k testT5106
echo.
echo   3. 退出虚拟环境:
echo      deactivate
echo.

endlocal
