@echo off
chcp 65001 >nul
cd /d "%~dp0.trae\skills\data-cleaner"
python generate.py %*
