#!/usr/bin/env python3
"""
Silent file monitor + HTTP server with built-in settings
"""

import os
import time
import shutil
import csv
import stat
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer
from datetime import datetime

# ---------------- CONFIGURATION ----------------
INCOMING_DIR = "/home/r1ley/coming"      # folder to watch
SERVED_DIR   = "/home/r1ley/suspecious"        # folder to serve
PORT         = 8001                       # port for HTTP server
POLL_SECONDS = 2                          # how often to scan (in seconds)
LOG_CSV      = "csv/middleware_events.csv"          # CSV log file
STATE_FILE   = "csv/state.txt"                # file to remember processed files
# ------------------------------------------------

# --- CSV Logger ---
class CSVLogger:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        init_needed = not os.path.exists(path)
        self.lock = threading.Lock()
        if init_needed:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp_utc", "filename", "incoming_path", "served_path"])

    def log(self, timestamp, filename, incoming_path, served_path):
        with self.lock:
            with open(self.path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, filename, incoming_path, served_path])

# --- State Tracker ---
class StateTracker:
    def __init__(self, path):
        self.path = path
        self.processed = set()
        if os.path.exists(path):
            with open(path, "r") as f:
                self.processed = set(line.strip() for line in f if line.strip())

    def save(self, filename):
        with open(self.path, "a") as f:
            f.write(filename + "\n")
        self.processed.add(filename)

    def seen(self, filename):
        return filename in self.processed

# --- File Monitor ---
class FileMonitor:
    def __init__(self, incoming, served, logger, tracker, poll_seconds=2):
        self.incoming = os.path.abspath(incoming)
        self.served = os.path.abspath(served)
        self.logger = logger
        self.tracker = tracker
        self.poll = poll_seconds
        os.makedirs(self.incoming, exist_ok=True)
        os.makedirs(self.served, exist_ok=True)

    def run(self):
        while True:
            for entry in os.scandir(self.incoming):
                if entry.is_file(follow_symlinks=False):
                    filename = entry.name
                    path = entry.path
                    if not self.tracker.seen(filename):
                        self.process(path, filename)
            time.sleep(self.poll)

    def process(self, path, filename):
        served_path = os.path.join(self.served, filename)
        if os.path.exists(served_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while True:
                candidate = os.path.join(self.served, f"{base}-{counter}{ext}")
                if not os.path.exists(candidate):
                    served_path = candidate
                    break
                counter += 1
        try:
            shutil.copy2(path, served_path)
            os.chmod(served_path, 0o644)
        except Exception:
            return
        try:
            os.chmod(path, 0)
        except Exception:
            pass

        ts = datetime.utcnow().isoformat() + "Z"
        self.logger.log(ts, filename, path, served_path)
        self.tracker.save(filename)

# --- HTTP Server ---
class SilentHTTPServer:
    def __init__(self, serve_dir, port):
        self.serve_dir = os.path.abspath(serve_dir)
        self.port = int(port)
        os.makedirs(self.serve_dir, exist_ok=True)

    def start(self):
        def handler_factory(*args, directory=self.serve_dir, **kwargs):
            return SimpleHTTPRequestHandler(*args, directory=directory, **kwargs)

        with ThreadingTCPServer(("", self.port), handler_factory) as httpd:
            httpd.serve_forever()

# --- Main ---
def main():
    logger = CSVLogger(LOG_CSV)
    tracker = StateTracker(STATE_FILE)
    monitor = FileMonitor(INCOMING_DIR, SERVED_DIR, logger, tracker, poll_seconds=POLL_SECONDS)
    http_server = SilentHTTPServer(SERVED_DIR, PORT)

    monitor_thread = threading.Thread(target=monitor.run, daemon=True)
    monitor_thread.start()
    http_server.start()

if __name__ == "__main__":
    main()
