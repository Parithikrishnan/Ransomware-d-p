import socket
import os
import time

SAVE_DIR = "/home/r1ley/testingransom/results"
SERVER_IP = "192.168.122.193"
SERVER_PORT = 9000
INTERVAL = 10  # seconds between checks

os.makedirs(SAVE_DIR, exist_ok=True)

def receive_file(conn):
    try:
        # Receive filename and filesize
        data = conn.recv(1024).decode()
        if not data:
            return False  # No data received
        filename, filesize = data.split("|")
        filesize = int(filesize)
        
        # Send ACK
        conn.send(b"ACK")
        
        # Receive file content
        filepath = os.path.join(SAVE_DIR, filename)
        received = 0
        with open(filepath, "wb") as f:
            while received < filesize:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
        print(f"[RECEIVED] {filename}")
        return True
    except Exception as e:
        # Could be timeout or connection issue
        return False

def main():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # optional, prevent blocking forever
                s.connect((SERVER_IP, SERVER_PORT))
                print(f"[CONNECTED] to server {SERVER_IP}:{SERVER_PORT}")
                
                # Try to receive all files in this batch
                start_time = time.time()
                while time.time() - start_time < INTERVAL:
                    if not receive_file(s):
                        time.sleep(0.5)  # small sleep to avoid busy loop
        except Exception as e:
            print(f"[ERROR] {e}, retrying in {INTERVAL} seconds...")
            time.sleep(INTERVAL)  # wait before reconnecting

if __name__ == "__main__":
    main()
