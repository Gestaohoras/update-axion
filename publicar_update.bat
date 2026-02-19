@echo off
setlocal ENABLEDELAYEDEXPANSION

set LOG_FILE=publish.log

echo ================================ > %LOG_FILE%
echo  PUBLICADOR DE ATUALIZACAO - AXION >> %LOG_FILE%
echo ================================ >> %LOG_FILE%
echo. >> %LOG_FILE%

echo Iniciando publicacao... >> %LOG_FILE%

echo Verificando arquivos... >> %LOG_FILE%
git status >> %LOG_FILE% 2>&1

echo Adicionando arquivos... >> %LOG_FILE%
git add . >> %LOG_FILE% 2>&1

echo Criando commit... >> %LOG_FILE%
git commit -m "Update Axion" >> %LOG_FILE% 2>&1

echo Enviando para repositorio... >> %LOG_FILE%
git push >> %LOG_FILE% 2>&1

echo. >> %LOG_FILE%
echo Publicacao finalizada. >> %LOG_FILE%

endlocal
