import os
import time
import csv

FILES_TO_MONITOR = [
    "/etc/proxychains.conf"
]

CSV_FILE = "csv/file_access_log.csv"

last_access = {}
for file in FILES_TO_MONITOR:
    if os.path.exists(file):
        last_access[file] = os.stat(file).st_atime

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "File", "Access Time"])

print(f"Monitoring file access... Logging to {CSV_FILE}. Press Ctrl+C to stop.")

try:
    while True:
        for file in FILES_TO_MONITOR:
            if os.path.exists(file):
                current_atime = os.stat(file).st_atime
                if current_atime != last_access[file]:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    access_time = time.ctime(current_atime)
                    with open(CSV_FILE, mode="a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([timestamp, file, access_time])

                    print(f"[ACCESSED] {file} at {access_time}")
                    last_access[file] = current_atime
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopped monitoring.")
