@echo off
REM Exchange Data Download Script Batch File
REM This batch file runs the Python script for downloading exchange data

REM Change to the script directory
REM cd /d "C:\Users\dglen\Dropbox\Exchange_Data_International\Options_Pulls"

REM Run the Python script
python "./exchange_data_download.py"

REM Log the completion
echo Script completed at %date% %time% >> "logs\batch_execution.log"