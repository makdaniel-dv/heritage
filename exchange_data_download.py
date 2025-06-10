import paramiko
import os
import logging
from datetime import datetime
import holidays
from dotenv import load_dotenv

# Load environment variables
load_dotenv(r'C:\Users\dglen\Dropbox\Exchange_Data_International\EnvScript\.env')

# SFTP credentials from environment variables
SFTP_CREDENTIALS = {
    'primary': {
        'host': os.getenv('SFTP_PRIMARY_HOST'),
        'port': int(os.getenv('SFTP_PRIMARY_PORT', '22')),
        'username': os.getenv('SFTP_USERNAME'),
        'password': os.getenv('SFTP_PASSWORD'),
        'path': os.getenv('SFTP_PATH'),
    },
    'backup': {
        'host': os.getenv('SFTP_BACKUP_HOST'),
        'port': int(os.getenv('SFTP_BACKUP_PORT', '22')),
        'username': os.getenv('SFTP_USERNAME'),
        'password': os.getenv('SFTP_PASSWORD'),
        'path': os.getenv('SFTP_PATH'),
    }
}

# Paths
LOCAL_PATH = r'C:\Users\dglen\Dropbox\Exchange_Data_International\Options_Pulls'
LOG_PATH = r'C:\Users\dglen\Dropbox\Exchange_Data_International\Options_Pulls\logs'

PROCESSED_FILE = os.path.join(LOG_PATH, 'processed_files.txt')

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    
    log_filename = datetime.now().strftime('exchange_data_download_%Y%m%d.log')
    log_filepath = os.path.join(LOG_PATH, log_filename)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    return logging.getLogger(__name__)

# Load processed files to avoid reprocessing
def load_processed_files():
    """Load list of already processed files"""
    if not os.path.exists(PROCESSED_FILE):
        os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
        with open(PROCESSED_FILE, 'w') as f:
            pass
        return set()
    try:
        with open(PROCESSED_FILE, 'r') as f:
            return set(line.strip() for line in f.readlines())
    except Exception as e:
        logger.error(f"Error loading processed files: {e}")
        return set()

# Mark a file as processed
def mark_file_as_processed(filename):
    """Mark a file as processed to avoid redownloading"""
    try:
        with open(PROCESSED_FILE, 'a') as f:
            f.write(filename + '\n')
        logger.info(f"Marked file as processed: {filename}")
    except Exception as e:
        logger.error(f"Error marking file as processed: {e}")

# Establish SFTP connection
def get_sftp_connection(server_type='primary'):
    """Establish SFTP connection to server"""
    try:
        creds = SFTP_CREDENTIALS[server_type]
        if not creds['username'] or not creds['password']:
            logger.error(f"Missing credentials for {server_type} server")
            return None, None, None
            
        logger.info(f"Connecting to {server_type} server: {creds['host']}")
        transport = paramiko.Transport((creds['host'], creds['port']))
        transport.connect(username=creds['username'], password=creds['password'])
        sftp = paramiko.SFTPClient.from_transport(transport)
        logger.info(f"Successfully connected to {server_type} server")
        return sftp, transport, creds['path']
    except Exception as e:
        logger.error(f"Error connecting to {server_type} server: {e}")
        return None, None, None

# List and filter ZIP files
def list_and_filter_zip_files(sftp, sftp_path):
    """List all ZIP files on the server"""
    try:
        sftp.chdir(sftp_path)
        files = sftp.listdir()
        zip_files = [f for f in files if f.endswith('.zip')]
        logger.info(f"Found {len(zip_files)} .zip files on server")
        for f in zip_files:
            logger.info(f"Available file: {f}")
        return zip_files
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return []

# Download ZIP file with timestamp (no processing)
def download_zip_file_with_timestamp(sftp, remote_file_path, filename):
    """Download ZIP file as-is and save with timestamp"""
    try:
        # Create timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1]
        timestamped_filename = f"{base_name}_{timestamp}{extension}"
        
        local_file_path = os.path.join(LOCAL_PATH, timestamped_filename)
        
        # Ensure local directory exists
        os.makedirs(LOCAL_PATH, exist_ok=True)
        
        # Download ZIP file directly (no processing)
        logger.info(f"Downloading ZIP file: {filename} -> {timestamped_filename}")
        sftp.get(remote_file_path, local_file_path)
        
        # Verify file was downloaded and get file size
        if os.path.exists(local_file_path):
            file_size = os.path.getsize(local_file_path)
            file_size_mb = file_size / (1024 * 1024)  # Convert to MB
            logger.info(f"SUCCESS: Downloaded {timestamped_filename} ({file_size_mb:.2f} MB)")
            return True
        else:
            logger.error(f"ERROR: File not found after download: {local_file_path}")
            return False
            
    except Exception as e:
        logger.error(f"ERROR: Error downloading {filename}: {e}")
        return False

# Check if today is a weekend or NYSE holiday
def is_weekend_or_nyse_holiday():
    """Check if today is a weekend or NYSE holiday"""
    try:
        us_holidays = holidays.US(prov=None, state=None, observed=True)
        today = datetime.today().date()
        is_weekend = today.weekday() >= 5  # Saturday = 5, Sunday = 6
        is_holiday = today in us_holidays
        
        if is_weekend:
            logger.info("Today is a weekend")
        if is_holiday:
            logger.info(f"Today is a NYSE holiday: {us_holidays.get(today)}")
            
        return is_weekend or is_holiday
    except Exception as e:
        logger.error(f"Error checking holiday status: {e}")
        return False

# Main download function
def download_exchange_data():
    """Main function to download exchange data files"""
    logger.info("=" * 50)
    logger.info("Starting Exchange Data Download Process")
    logger.info("=" * 50)
    
    # Check if today is a weekend or holiday
    if is_weekend_or_nyse_holiday():
        logger.info("Today is a weekend or NYSE holiday. Exiting without processing.")
        return
    
    # Try primary server first, then backup
    sftp, transport, sftp_path = get_sftp_connection('primary')
    
    if sftp is None:
        logger.warning("Primary server failed, trying backup server...")
        sftp, transport, sftp_path = get_sftp_connection('backup')
    
    if sftp is None:
        logger.error("Could not connect to any server. Exiting.")
        return
    
    try:
        # Load processed files
        processed_files = load_processed_files()
        
        # Get list of ZIP files
        zip_files = list_and_filter_zip_files(sftp, sftp_path)
        
        if not zip_files:
            logger.warning("No ZIP files found on server")
            return
        
        # Download new files
        downloaded_count = 0
        for zip_file in zip_files:
            if zip_file in processed_files:
                logger.info(f"Skipping already processed file: {zip_file}")
                continue
            
            remote_file_path = f"{sftp_path}/{zip_file}"
            logger.info(f"Processing {zip_file}...")
            
            # Download ZIP file directly (no processing needed)
            success = download_zip_file_with_timestamp(sftp, remote_file_path, zip_file)
            
            if success:
                mark_file_as_processed(zip_file)
                downloaded_count += 1
            else:
                logger.error(f"ERROR: Failed to download {zip_file}")
        
        logger.info(f"COMPLETED: Download process finished. Downloaded {downloaded_count} new ZIP files.")
        
        if downloaded_count == 0:
            logger.info("INFO: No new files to download (all files already processed)")
        else:
            logger.info(f"LOCATION: Files saved to: {LOCAL_PATH}")
        
    except Exception as e:
        logger.error(f"Error during download process: {e}")
    finally:
        # Close connections
        try:
            sftp.close()
            transport.close()
            logger.info("SFTP connections closed")
        except:
            pass

if __name__ == "__main__":
    # Setup logging
    logger = setup_logging()
    
    try:
        download_exchange_data()
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
    
    logger.info("Script execution completed")