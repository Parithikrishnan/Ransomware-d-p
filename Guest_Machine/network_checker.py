import subprocess
import csv
import os
from datetime import datetime

# CSV output file
CSV_FILE = "csv/dns_capture.csv"

# Ensure CSV exists with headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "src_ip", "dst_ip", "protocol", "length"])

# TCPDump command for port 53 (DNS)
TCPDUMP_CMD = ["sudo", "tcpdump", "-l", "-n", "port 53"]

# Run tcpdump as a subprocess
with subprocess.Popen(TCPDUMP_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
    try:
        for line in proc.stdout:
            # Example tcpdump line format:
            # 12:34:56.789012 IP 192.168.1.2.12345 > 8.8.8.8.53: UDP, length 32
            parts = line.split()
            if "IP" in parts:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    src_ip = parts[2].split('.')[0:-1]  # get IP without port
                    src_ip = '.'.join(src_ip)
                    dst_ip = parts[4].split('.')[0:-1]
                    dst_ip = '.'.join(dst_ip)
                    protocol = parts[5].replace(',', '')
                    length = parts[-1]
                except IndexError:
                    continue

                # Write to CSV
                with open(CSV_FILE, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, src_ip, dst_ip, protocol, length])

    except KeyboardInterrupt:
        print("\nCapture stopped by user.")
