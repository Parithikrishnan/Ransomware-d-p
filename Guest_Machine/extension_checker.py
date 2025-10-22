import os
import time
import csv

RANSOM_EXTS = [
    ".locked", ".encrypted", ".enc", ".crypt", ".crypz", ".locky", ".crypto", ".cry",
    ".wncry", ".wnry", ".wcry", ".wncrypt",
    ".zzzzz", ".osiris", ".aesir", ".lukitus", ".diablo6", ".ykcol",
    ".djvu", ".djvut", ".puma", ".pumax", ".pumaxl", ".domn", ".bora",
    ".moka", ".grod", ".vero", ".kuub", ".nesa", ".npsk", ".lokf", ".meka",
    ".crypted", ".cryptxxx",
    ".dharma", ".wallet", ".arrow", ".bip", ".booA", ".cetus", ".gamma", ".gpg",
    ".ryk", ".ryuk", ".conti",
    ".fila", ".krab", ".lokd", ".nyton", ".sodinokibi", ".koko", ".malox",
    ".matrix", ".btc", ".pay", ".keypass", ".myskle", ".malware",
    ".crypt1"
]

target_dir = "/home/r1ley/ransom/"
interval = 2  
csv_file = "csv/ransomware_files.csv"

# Create CSV with headers if not exists
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "File Path", "Extension"])

while True:
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in RANSOM_EXTS:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                file_path = os.path.join(root, f)
                
                # Write to CSV
                with open(csv_file, mode="a", newline="") as f_out:
                    writer = csv.writer(f_out)
                    writer.writerow([timestamp, file_path, ext])
    time.sleep(interval)
