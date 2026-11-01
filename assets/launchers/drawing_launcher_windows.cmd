@echo off
set /p "exe_path=" < "%LOCALAPPDATA%\Rysko\exe_path.txt"
start "" "%exe_path%" "%~1"