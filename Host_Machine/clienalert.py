import os
import time
from shutil import rmtree
import logging

# Set the directory for alert file (shared directory with host)
ALERT_FILE_PATH = "/path/to/alert.txt"  # Shared alert file path

# The file to be deleted (from host) - This will be passed from your detection logic
DETECTED_FILE_PATH = "/path/to/suspicious/file"  # This is the file detected by ransomware

# Logging setup
logging.basicConfig(filename="ransomware_detection.log", level=logging.INFO)

# Function to send an alert to the host
def send_alert_to_host(alert_message):
    try:
        with open(ALERT_FILE_PATH, 'w') as alert_file:
            alert_file.write(alert_message)
        logging.info(f"Alert sent to host: {alert_message}")
        print(f"Alert sent to host: {alert_message}")
    except Exception as e:
        logging.error(f"Failed to send alert to host: {e}")
        print(f"Error sending alert to host: {e}")

# Function to delete the file from the host machine
def delete_file_from_host(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Deleted suspicious file from host: {file_path}")
            print(f"Deleted suspicious file from host: {file_path}")
        else:
            logging.warning(f"File does not exist: {file_path}")
            print(f"File does not exist: {file_path}")
    except Exception as e:
        logging.error(f"Failed to delete file {file_path} from host: {e}")
        print(f"Error deleting file: {e}")

# Main function to handle ransomware detection
def handle_ransomware_detection():
    # Send an alert to the host with the path of the suspicious file
    send_alert_to_host(f"Ransomware detected! Malicious file: {DETECTED_FILE_PATH}")

    # Optionally delete the file on the host machine after detection
    delete_file_from_host(DETECTED_FILE_PATH)

if __name__ == "__main__":
    # Assuming ransomware is detected, run the handler
    handle_ransomware_detection()