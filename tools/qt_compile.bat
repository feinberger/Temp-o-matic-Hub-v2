@echo OFF
title python QT ui compile bat file

@echo OFF

::Folder Paths
cd ..\designer\
SET UI_PATH=%cd%\
cd ..\src\ui\
SET PY_PATH=%cd%\

::Screens
SET MAIN_SCREEN=tempomatic

echo Compiling Main Screen...
pyuic5 -x "%UI_PATH%%MAIN_SCREEN%.ui" -o "%PY_PATH%%MAIN_SCREEN%.py"

echo Completed Compilation for QT Creator