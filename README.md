Exchange Data Download System
Overview
This system automatically downloads exchange data files from SFTP servers and saves them to a local Dropbox sync folder with timestamp-based filenames. The system is designed to run daily via Windows Task Scheduler and includes comprehensive logging and error handling.
Features

- Automatic SFTP file download with timestamped filenames
- Primary and backup server support with automatic failover
- Weekend and NYSE holiday detection (skips processing on non-business days)
- Comprehensive logging with daily log files
- Duplicate file prevention (tracks already processed files)
- Secure credential storage using environment variables
- Error handling and recovery mechanisms
- Windows Task Scheduler integration should be done manually

System Requirements

Python 3.7 or higher
Windows 10/11 (for Task Scheduler integration)
Active internet connection
Dropbox desktop application installed and synced

File Structure
C:\Users\dglen\Dropbox\Exchange_Data_International\
├── Options_Pulls\                          # Main directory
│   ├── exchange_data_download.py           # Main Python script
│   ├── run_exchange_download.bat           # Batch file for Task Scheduler
│   ├── [Downloaded ZIP files]             # Timestamped ZIP files
│   └── logs\                              # Logging directory
│       ├── exchange_data_download_YYYYMMDD.log  # Daily log files
│       ├── batch_execution.log            # Batch execution history
│       └── processed_files.txt            # Track processed files
└── EnvScript\
    └── .env                               # SFTP credentials (secure)


Installation & Setup
1. Python Dependencies
bashpip install paramiko python-dotenv holidays
2. File Placement

Place exchange_data_download.py in the Options_Pulls folder
Place .env file in the EnvScript folder
Place run_exchange_download.bat in the Options_Pulls folder

3. Environment Configuration
The .env file contains SFTP server credentials and should be configured as follows:
envSFTP_PRIMARY_HOST=ftp.exchange-data.net
SFTP_PRIMARY_PORT=22
SFTP_BACKUP_HOST=ftp.exchange-data.com
SFTP_BACKUP_PORT=22
SFTP_USERNAME=41115_whc
SFTP_PASSWORD=47kF5BCm
SFTP_PATH=/Deriv/Bespoke/Western_Heritage
Usage
Manual Execution
bashcd "C:\Users\dglen\Dropbox\Exchange_Data_International\Options_Pulls"
python exchange_data_download.py
Automated Execution
The system is designed to run automatically via Windows Task Scheduler at 11:00 PM EDT daily.
Logging & Monitoring
Log Files Location
All logs are stored in: C:\Users\dglen\Dropbox\Exchange_Data_International\Options_Pulls\logs\
Log Types

Daily Script Logs: exchange_data_download_YYYYMMDD.log

Contains detailed execution information
Records file downloads, errors, and status updates
New file created each day


Batch Execution Log: batch_execution.log

Records when the batch file runs
Useful for Task Scheduler troubleshooting


Processed Files Tracker: processed_files.txt

Maintains list of already downloaded files
Prevents duplicate downloads



Sample Log Output
2025-06-09 23:00:01 - INFO - Starting Exchange Data Download Process
2025-06-09 23:00:02 - INFO - Connecting to primary server: ftp.exchange-data.net
2025-06-09 23:00:03 - INFO - Successfully connected to primary server
2025-06-09 23:00:04 - INFO - Found 3 .zip files on server
2025-06-09 23:00:05 - INFO - Downloading ZIP file: data_file.zip -> data_file_20250609_230005.zip
2025-06-09 23:00:07 - INFO -  Successfully downloaded data_file_20250609_230005.zip (15.42 MB)
2025-06-09 23:00:08 - INFO -  Download process completed. Downloaded 1 new ZIP files.
Error Handling
Common Issues & Solutions

SFTP Connection Failed

System automatically tries backup server
Check internet connection and credentials


File Download Errors

Individual file failures don't stop the entire process
Failed downloads are logged and can be retried on next run


Permission Errors

Ensure Dropbox folder has write permissions
Run as administrator if necessary



Holiday/Weekend Handling
The system automatically detects:

Weekends (Saturday & Sunday)
NYSE holidays
Skips processing on these days with appropriate logging

Security Features

Credentials stored in separate .env file
Environment file location specified by client requirements
No hardcoded passwords in main script
Secure SFTP connection with proper authentication

File Naming Convention
Downloaded files are saved with timestamps to prevent overwriting:
Original: data_file.zip
Saved as: data_file_20250609_230005.zip
Format: [filename]_YYYYMMDD_HHMMSS.zip