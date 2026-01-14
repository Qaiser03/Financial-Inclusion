@echo off
REM Activation script for Financial Inclusion virtual environment
echo Activating "Financial Inclusion" virtual environment...
call "Financial Inclusion\Scripts\activate.bat"
echo.
echo Virtual environment activated!
echo Python version:
python --version
echo.
echo To deactivate, type: deactivate
