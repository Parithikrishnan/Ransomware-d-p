import time
import os
import csv
from datetime import datetime

# Path to the alert file (shared with the VM)
ALERT_FILE_PATH = "results/alert.txt"

# Path to the CSV log file
CSV_LOG_FILE = "csv/alerts_log.csv"

# Function to initialize CSV file with headers (if not exists)
def init_csv():
    if not os.path.exists(CSV_LOG_FILE):
        with open(CSV_LOG_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Alert Message", "File Path", "Action Status"])

# Function to delete file on host machine
def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"Deleted: {file_path}"
        else:
            return f"File not found: {file_path}"
    except Exception as e:
        return f"Error deleting {file_path}: {e}"

# Function to log results into CSV
def log_to_csv(alert_message, detected_file_path, status):
    with open(CSV_LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), alert_message, detected_file_path, status])

# Function to monitor the alert file
def monitor_alert_file():
    init_csv()
    while True:
        if os.path.exists(ALERT_FILE_PATH):
            with open(ALERT_FILE_PATH, "r") as alert_file:
                alert_message = alert_file.read().strip()
                
                if alert_message:
                    # Extract detected file path (simple format: "Alert: /path/to/file")
                    parts = alert_message.split(":", 1)
                    detected_file_path = parts[1].strip() if len(parts) > 1 else "Unknown"

                    # Try deleting the file
                    status = delete_file(detected_file_path)

                    # Log everything into CSV
                    log_to_csv(alert_message, detected_file_path, status)

                    # Remove alert file after processing
                    os.remove(ALERT_FILE_PATH)
        
        # Sleep before next check
        time.sleep(2)  # You can adjust interval

if __name__ == "__main__":
    monitor_alert_file()
