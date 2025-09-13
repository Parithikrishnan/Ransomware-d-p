#!/usr/bin/env python3
import os
import time
import shutil
import threading
import csv
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer
from datetime import datetime

# ==========================
# Configuration (hardcoded)
# ==========================
WATCH_DIR = "/home/r1ley/Downloads"   # Directory to watch for new files
SERVE_DIR = "/home/r1ley/suspecious"     # Directory where files will be hosted
PORT = 8001                         # HTTP port
POLL_INTERVAL = 5                   # Scan interval (seconds)
LOG_FILE = "csv/events_hosting.csv" # Log file
# ==========================

# Ensure CSV directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Create log file with headers if missing
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "event_type", "details"])

def log_event(event_type, details):
    """Append log entry into CSV with timestamp"""
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), event_type, details])

def monitor_and_move(watch_dir, serve_dir, poll_interval=2):
    """Continuously scan watch_dir for new files and move them to serve_dir"""
    seen = set()
    try:
        for name in os.listdir(watch_dir):
            seen.add(name)
    except FileNotFoundError:
        os.makedirs(watch_dir, exist_ok=True)
        log_event("INFO", f"Created watch directory {watch_dir}")

    while True:
        try:
            current = set(os.listdir(watch_dir))
        except Exception as e:
            log_event("ERROR", f"Error listing {watch_dir}: {e}")
            time.sleep(poll_interval)
            continue

        new = current - seen
        if new:
            for fname in sorted(new):
                src = os.path.join(watch_dir, fname)
                if os.path.isdir(src):
                    log_event("INFO", f"Skipping directory {fname}")
                    seen.add(fname)
                    continue
                dest = os.path.join(serve_dir, fname)
                base, ext = os.path.splitext(fname)
                counter = 1
                while os.path.exists(dest):
                    dest = os.path.join(serve_dir, f"{base}_{counter}{ext}")
                    counter += 1
                try:
                    shutil.move(src, dest)
                    log_event("MOVED", f"{src} -> {dest}")
                except Exception as e:
                    log_event("ERROR", f"Failed to move {src}: {e}")
                seen.add(fname)
        time.sleep(poll_interval)

def start_http_server(serve_dir, port):
    """Start HTTP server to host serve_dir"""
    os.chdir(serve_dir)
    handler = SimpleHTTPRequestHandler

    class ReuseAddrThreadingServer(ThreadingTCPServer):
        allow_reuse_address = True

    server = ReuseAddrThreadingServer(("0.0.0.0", port), handler)
    log_event("INFO", f"HTTP server started on 0.0.0.0:{port}, serving {serve_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log_event("INFO", "Server shutdown requested.")
    finally:
        server.shutdown()
        server.server_close()
        log_event("INFO", "HTTP server stopped.")

def main():
    os.makedirs(WATCH_DIR, exist_ok=True)
    os.makedirs(SERVE_DIR, exist_ok=True)

    # Start monitoring thread
    t = threading.Thread(target=monitor_and_move, args=(WATCH_DIR, SERVE_DIR, POLL_INTERVAL), daemon=True)
    t.start()

    # Start HTTP server (blocking)
    start_http_server(SERVE_DIR, PORT)

if __name__ == "__main__":
    main()
