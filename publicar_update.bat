@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ==========================================
echo     PUBLICADOR DE ATUALIZACAO - AXION
echo ==========================================
echo.

REM =============================
REM CONFERE SE ESTA EM UM REPO GIT
REM =============================
git rev-parse --is-inside-work-tree >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Esta pasta nao e um repositorio Git.
    pause
    exit /b
)

echo Arquivos encontrados com sucesso.
echo.

REM =============================
REM PEDIR VERSAO
REM =============================
set /p AXION_VERSION=Digite a nova versao do Axion (ex: 1.0.4): 

if "%AXION_VERSION%"=="" (
    echo Versao invalida.
    pause
    exit /b
)

echo.
echo Publicando atualizacao da versao %AXION_VERSION%...
echo.

REM =============================
REM ATUALIZAR version.json
REM =============================
if exist version.json (
    powershell -Command ^
    "(Get-Content version.json | ConvertFrom-Json | ForEach-Object { $_.axion_release='%AXION_VERSION%'; $_ }) | ConvertTo-Json -Depth 10 | Set-Content version.json"
)

REM =============================
REM ADD (SEM STATUS VERBOSO)
REM =============================
git add . >nul 2>&1

REM =============================
REM COMMIT (SILENCIOSO QUANDO NAO HA MUDANCA)
REM =============================
git diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo Nenhuma alteracao detectada. Nada para commitar.
) else (
    git commit -m "Update Axion para versao %AXION_VERSION%" >nul 2>&1
    echo Commit criado com sucesso.
)

REM =============================
REM PUSH
REM =============================
echo.
echo Enviando para o GitHub...
git push

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO ao enviar para o GitHub.
    echo Execute antes:
    echo   git pull --rebase
    echo e depois rode este BAT novamente.
    pause
    exit /b
)

echo.
echo Publicacao concluida com sucesso.
pause
endlocal
