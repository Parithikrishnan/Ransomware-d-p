import os
import random
import string
import time
import shutil
from threading import Thread

# Configuration
TARGET_FOLDER = "./helloworld"  # Directory to simulate file creation and encryption
FILE_SIZE_MB = 10  # Size of each file in MB (you can adjust this for larger/smaller files)
TRANSFER_RATE_MBPS = 30  # Desired transfer rate in Mbps

# Ensure the target folder exists
os.makedirs(TARGET_FOLDER, exist_ok=True)

# Helper function to generate random file names
def generate_filename():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".txt"

# Function to write a file (simulate encryption)
def write_file(file_path):
    with open(file_path, "wb") as f:
        f.write(os.urandom(FILE_SIZE_MB * 1024 * 1024))  # Writing random data to the file

# Function to read a file (simulate decryption)
def read_file(file_path):
    with open(file_path, "rb") as f:
        f.read()  # Simulating reading the file (no action needed, just for the test)

# Function to control file I/O rate (mimicking ransomware activity)
def simulate_ransomware():
    start_time = time.time()
    files_written = 0
    while True:
        # Create a new random file
        file_name = generate_filename()
        file_path = os.path.join(TARGET_FOLDER, file_name)

        # Write the file
        write_file(file_path)

        # Increment the count of files written
        files_written += 1

        # Simulate a delay to control the transfer rate (30 Mbps)
        elapsed_time = time.time() - start_time
        expected_files_written = (TRANSFER_RATE_MBPS * 1024 * 1024 * elapsed_time) / (FILE_SIZE_MB * 1024 * 1024)
        if files_written < expected_files_written:
            time.sleep(0.01)  # Short sleep to simulate rate limiting

        # Optionally: Simulate reading the file (decryption)
        read_file(file_path)

        # If you want to delete the files after reading them (simulating file deletion), you can do so
        os.remove(file_path)

# Run the simulation in a background thread to mimic constant file operations
if __name__ == "__main__":
    print("Starting ransomware simulation with 30 Mbps transfer rate...")
    thread = Thread(target=simulate_ransomware)
    thread.daemon = True
    thread.start()

    try:
        # Allow the script to run for 60 seconds (or however long you want for testing)
        time.sleep(60)
    except KeyboardInterrupt:
        print("Simulation interrupted.")
