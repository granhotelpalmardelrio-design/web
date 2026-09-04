@echo off
setlocal EnableExtensions
title Subir cambios - Gran Hotel Palmar del Rio

REM Siempre trabaja desde la carpeta donde se encuentra este archivo.
cd /d "%~dp0"

set "REPO=https://github.com/granhotelpalmardelrio-design/web.git"
set "BRANCH=main"

where git >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Git no esta instalado o no esta disponible en PATH.
  echo Instala Git y vuelve a ejecutar este archivo.
  pause
  exit /b 1
)

if not exist ".git" (
  echo Inicializando el repositorio local...
  git init
  if errorlevel 1 goto :error
)

git branch -M %BRANCH%

git config user.name >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: falta configurar tu nombre de autor de Git.
  echo Ejecuta una vez:
  echo git config --global user.name "Tu Nombre"
  echo git config --global user.email "tu-correo@ejemplo.com"
  pause
  exit /b 1
)
git config user.email >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: falta configurar tu correo de autor de Git.
  echo Ejecuta una vez:
  echo git config --global user.name "Tu Nombre"
  echo git config --global user.email "tu-correo@ejemplo.com"
  pause
  exit /b 1
)

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin "%REPO%"
) else (
  git remote set-url origin "%REPO%"
)
if errorlevel 1 goto :error

echo.
echo Archivos modificados:
git status --short
echo.
set /p "MENSAJE=Mensaje del cambio (Enter = Actualizacion del sitio): "
if "%MENSAJE%"=="" set "MENSAJE=Actualizacion del sitio"

git add -A
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "%MENSAJE%"
  if errorlevel 1 goto :error
) else (
  echo No hay cambios nuevos para confirmar.
)

REM Si GitHub ya tiene archivos (por ejemplo, README), los integra antes del push.
git fetch origin
if errorlevel 1 goto :error
git rev-parse --verify origin/%BRANCH% >nul 2>&1
if not errorlevel 1 (
  git merge origin/%BRANCH% --allow-unrelated-histories -m "Sincronizar cambios de GitHub"
  if errorlevel 1 (
    echo.
    echo Hay un conflicto que debes resolver antes de subir. No se envio nada.
    pause
    exit /b 1
  )
)

git push -u origin %BRANCH%
if errorlevel 1 goto :error

echo.
echo Listo: los cambios se subieron a GitHub.
pause
exit /b 0

:error
echo.
echo No se pudieron subir los cambios. Revisa el mensaje anterior.
pause
exit /b 1
