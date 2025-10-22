import os
import time
import subprocess

# Directory to monitor
MONITOR_DIR = "/home/r1ley/suspecious"

# File extensions to execute
EXECUTABLE_EXTS = ['.py', '.sh']

# Track files already seen
seen_files = set()

def execute_file(filepath):
    ext = os.path.splitext(filepath)[1]
    try:
        if ext == '.py':
            print(f"Executing Python file: {filepath}")
            subprocess.run(['python3', filepath], check=True)
        elif ext == '.sh':
            print(f"Executing Shell script: {filepath}")
            subprocess.run(['bash', filepath], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {filepath}: {e}")

def scan_directory():
    global seen_files
    current_files = set(os.listdir(MONITOR_DIR))
    new_files = current_files - seen_files

    for filename in new_files:
        filepath = os.path.join(MONITOR_DIR, filename)
        if os.path.isfile(filepath):
            if any(filename.endswith(ext) for ext in EXECUTABLE_EXTS):
                execute_file(filepath)

    seen_files = current_files

if __name__ == "__main__":
    seen_files = set(os.listdir(MONITOR_DIR))
    print(f"Monitoring directory: {MONITOR_DIR}")
    
    while True:
        scan_directory()
        time.sleep(5)  
