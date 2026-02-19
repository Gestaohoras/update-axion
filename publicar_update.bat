@echo off
title Publicador de AtualizaÃ§Ãµes - Axion

echo ==========================================
echo     PUBLICADOR DE ATUALIZACAO - AXION
echo ==========================================
echo.

:: Confere se esta em um repositorio git
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ERRO: Esta pasta nao e um repositorio Git.
    pause
    exit /b
)

:: Confere arquivos obrigatorios
if not exist Axion.exe (
    echo ERRO: Axion.exe nao encontrado.
    pause
    exit /b
)

if not exist version.json (
    echo ERRO: version.json nao encontrado.
    pause
    exit /b
)

if not exist changelog.json (
    echo ERRO: changelog.json nao encontrado.
    pause
    exit /b
)

echo Arquivos encontrados com sucesso.
echo.

:: Pede a versao
set /p VERSION=Digite a nova versao do Axion (ex: 1.0.4): 

if "%VERSION%"=="" (
    echo ERRO: Versao invalida.
    pause
    exit /b
)

echo.
echo Publicando atualizacao da versao %VERSION%...
echo.

:: Adiciona os arquivos corretos
git add Axion.exe version.json changelog.json

:: Commit
git commit -m "Update Axion para versao %VERSION%"
if errorlevel 1 (
    echo ERRO ao criar commit.
    pause
    exit /b
)

:: Push
git push
if errorlevel 1 (
    echo ERRO ao enviar para o GitHub.
    pause
    exit /b
)

echo.
echo ==========================================
echo  ATUALIZACAO PUBLICADA COM SUCESSO!
echo ==========================================
echo.
pause