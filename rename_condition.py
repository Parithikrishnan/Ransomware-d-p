from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

# Directory to monitor
MONITOR_DIR = "/home/r1ley/ransom/"  # change this to the folder you want to watch

class RenameHandler(FileSystemEventHandler):
    def on_moved(self, event):
        if not event.is_directory:
            print(f"File Renamed: {event.src_path} -> {event.dest_path}")

if __name__ == "__main__":
    event_handler = RenameHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITOR_DIR, recursive=True)
    observer.start()
    print(f"Monitoring file renames in: {MONITOR_DIR}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
