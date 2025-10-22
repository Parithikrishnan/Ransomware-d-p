from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import csv
import sys
import signal

MONITOR_DIR = "/home/r1ley/ransom/"   
CSV_FILE = "csv/rename_events.csv"        


class RenameHandler(FileSystemEventHandler):
    def __init__(self, csv_writer_lock=None):
        super().__init__()
        self.csv_writer_lock = csv_writer_lock

    def on_moved(self, event):
        if event.is_directory:
            return

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        src = os.path.abspath(event.src_path)
        dest = os.path.abspath(event.dest_path)
        try:
            with open(CSV_FILE, mode="a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, src, dest])
        except Exception as e:
            print(f"ERROR writing to {CSV_FILE}: {e}", file=sys.stderr)

def ensure_csv_header():
    """Create CSV file with headers if it doesn't already exist."""
    if not os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Source Path", "Destination Path"])
        except Exception as e:
            print(f"ERROR creating {CSV_FILE}: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    if not os.path.isdir(MONITOR_DIR):
        print(f"ERROR: monitor directory does not exist: {MONITOR_DIR}", file=sys.stderr)
        sys.exit(1)

    ensure_csv_header()

    event_handler = RenameHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITOR_DIR, recursive=True)
    observer.start()
    def _signal_handler(signum, frame):
        observer.stop()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        while observer.is_alive():
            time.sleep(1)
    finally:
        observer.join()

if __name__ == "__main__":
    main()
