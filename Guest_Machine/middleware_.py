import os
import time
import csv
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# ---------------- CONFIGURATION ---------------- #
LOCAL_DOMAIN = "http://127.0.0.1:8001/"  # The URL that lists the files
DOWNLOAD_DIR = "/home/r1ley/"             # Where to save the files
CSV_LOG_FILE = "csv/file_log.csv"         # CSV to track downloaded files
TEXT_FILE_LOG = "csv/file_list.txt"       # Text file to track new/old files
INTERVAL_SECONDS = 5                     # Interval to check for new files
# ------------------------------------------------ #

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CSV_LOG_FILE), exist_ok=True)

# Ensure CSV file exists with headers
if not os.path.exists(CSV_LOG_FILE):
    with open(CSV_LOG_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "filename"])

# Ensure text file exists
if not os.path.exists(TEXT_FILE_LOG):
    with open(TEXT_FILE_LOG, mode='w') as f:
        f.write("OLD FILES:\n\nNEW FILES:\n\n")

def get_downloaded_files():
    with open(CSV_LOG_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        return set(row["filename"] for row in reader)

def log_file(filename):
    with open(CSV_LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), filename])

def update_text_file(new_files, old_files):
    with open(TEXT_FILE_LOG, mode='w') as f:
        f.write("OLD FILES:\n")
        for file in old_files:
            f.write(f"{file}\n")
        f.write("\nNEW FILES:\n")
        for file in new_files:
            f.write(f"{file}\n")

def fetch_file_list():
    """Fetches file list by parsing HTML from server directory listing"""
    try:
        response = requests.get(LOCAL_DOMAIN, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        files = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href not in ("../", "/"):  # skip parent folder links
                files.append(href.strip("/"))
        return files
    except:
        return []

def download_file(filename):
    file_url = f"{LOCAL_DOMAIN}/{filename}"
    local_path = os.path.join(DOWNLOAD_DIR, filename)
    try:
        r = requests.get(file_url, timeout=10)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
        log_file(filename)
        return True
    except:
        return False

def main():
    while True:
        downloaded_files = get_downloaded_files()
        available_files = fetch_file_list()
        new_files = [f for f in available_files if f not in downloaded_files]
        old_files = list(downloaded_files)

        for f in new_files:
            if download_file(f):
                old_files.append(f)

        update_text_file(new_files=new_files, old_files=old_files)
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
