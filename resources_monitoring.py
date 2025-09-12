import psutil
import time
import csv
from datetime import datetime
import os

DISK_SPIKE_THRESHOLD = 30 * 1024 * 1024  
CSV_FILE = "csv/disk_io_speed.csv"


write_header = not os.path.exists(CSV_FILE)

if write_header:
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ["Timestamp", "Read Speed (MB/s)", "Write Speed (MB/s)", "Alert"]
        writer.writerow(header)
        print(",".join(header))  

if not write_header:

    print(",".join(["Timestamp", "Read Speed (MB/s)", "Write Speed (MB/s)", "Alert"]))

if __name__ == "__main__":
    prev_disk_io = psutil.disk_io_counters()
    prev_read = prev_disk_io.read_bytes
    prev_write = prev_disk_io.write_bytes

    try:
        while True:
            time.sleep(1) 

            curr_disk_io = psutil.disk_io_counters()
            curr_read = curr_disk_io.read_bytes
            curr_write = curr_disk_io.write_bytes

            read_speed = curr_read - prev_read
            write_speed = curr_write - prev_write

            prev_read = curr_read
            prev_write = curr_write

            read_speed_mb = read_speed / (1024**2)
            write_speed_mb = write_speed / (1024**2)

            alert = ""
            if read_speed >= DISK_SPIKE_THRESHOLD or write_speed >= DISK_SPIKE_THRESHOLD:
                alert = "SPIKE DETECTED"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [timestamp, f"{read_speed_mb:.2f}", f"{write_speed_mb:.2f}", alert]

            with open(CSV_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

            print(",".join(row))

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
