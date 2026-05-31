@echo off
REM Pornire din sursa (varianta de dezvoltare, necesita Python + dependinte instalate).
REM Pentru utilizatorul final foloseste executabilul: dist\evaluare-anevar.exe
cd /d "%~dp0"
python -m evaluare
pause
