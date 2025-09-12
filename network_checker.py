'''
# redirect incoming DNS to 5353
sudo iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-ports 5353
sudo iptables -t nat -A PREROUTING -p tcp --dport 53 -j REDIRECT --to-ports 5353
# capture local processes' output too
sudo iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5353
sudo iptables -t nat -A OUTPUT -p tcp --dport 53 -j REDIRECT --to-ports 5353
'''

import argparse
import socket
import threading
import time
import csv
import os
from dnslib import DNSRecord, QTYPE

CSV_HEADERS = ["ts", "proto", "event", "client_ip", "client_port", "qname", "qtype", "pid", "raw_len", "answer_count"]

class CSVLogger:
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        new_file = not os.path.exists(path)
        self.f = open(path, "a", newline="", buffering=1)
        self.writer = csv.writer(self.f)
        if new_file:
            self.writer.writerow(CSV_HEADERS)

    def log(self, row):
        with self.lock:
            self.writer.writerow(row)

    def close(self):
        try:
            self.f.close()
        except Exception:
            pass

def now_ts():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")

def safe_parse_query(data):
    try:
        rec = DNSRecord.parse(data)
        qname = str(rec.q.qname) if rec.q else ""
        qtype = QTYPE[rec.q.qtype] if rec.q else ""
        return qname, qtype
    except Exception:
        return "", ""

def forward_udp_and_respond(data, addr, listen_sock, upstream_host, upstream_port, logger):
    client_ip, client_port = addr[0], addr[1]
    qname, qtype = safe_parse_query(data)
    # Log query
    logger.log([now_ts(), "UDP", "query", client_ip, client_port, qname, qtype, "", len(data), ""])
    # Forward to upstream
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(5.0)
            s.sendto(data, (upstream_host, upstream_port))
            resp, _ = s.recvfrom(65535)
            listen_sock.sendto(resp, addr)
            # Log response (answer_count when parseable)
            try:
                rrec = DNSRecord.parse(resp)
                ans = len(rrec.rr)
            except Exception:
                ans = ""
            logger.log([now_ts(), "UDP", "response", client_ip, client_port, qname, qtype, "", len(resp), ans])
    except Exception as e:
        logger.log([now_ts(), "UDP", "error", client_ip, client_port, qname, qtype, "", 0, str(e)])

def udp_server(listen_addr, listen_port, upstream_host, upstream_port, logger):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_addr, listen_port))
    print(f"[+] UDP DNS proxy listening on {listen_addr}:{listen_port}")
    try:
        while True:
            data, addr = sock.recvfrom(65535)
            threading.Thread(target=forward_udp_and_respond, args=(data, addr, sock, upstream_host, upstream_port, logger), daemon=True).start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("UDP server error:", e)

def handle_tcp_client(conn, addr, upstream_host, upstream_port, logger):
    client_ip, client_port = addr[0], addr[1]
    try:
        # read two bytes length prefix
        head = conn.recv(2)
        if len(head) < 2:
            conn.close(); return
        length = int.from_bytes(head, "big")
        body = b""
        while len(body) < length:
            part = conn.recv(length - len(body))
            if not part:
                break
            body += part
        qname, qtype = safe_parse_query(body)
        logger.log([now_ts(), "TCP", "query", client_ip, client_port, qname, qtype, "", len(body), ""])
        # forward to upstream (TCP)
        with socket.create_connection((upstream_host, upstream_port), timeout=5) as s:
            s.sendall(len(body).to_bytes(2, "big") + body)
            # read two bytes length
            head2 = s.recv(2)
            if len(head2) < 2:
                conn.close(); return
            resp_len = int.from_bytes(head2, "big")
            resp = b""
            while len(resp) < resp_len:
                resp += s.recv(resp_len - len(resp))
            # send back to client with length prefix
            conn.sendall(len(resp).to_bytes(2, "big") + resp)
            try:
                rrec = DNSRecord.parse(resp)
                ans = len(rrec.rr)
            except Exception:
                ans = ""
            logger.log([now_ts(), "TCP", "response", client_ip, client_port, qname, qtype, "", len(resp), ans])
    except Exception as e:
        logger.log([now_ts(), "TCP", "error", client_ip, client_port, "", "", "", 0, str(e)])
    finally:
        try:
            conn.close()
        except Exception:
            pass

def tcp_server(listen_addr, listen_port, upstream_host, upstream_port, logger):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((listen_addr, listen_port))
    sock.listen(64)
    print(f"[+] TCP DNS proxy listening on {listen_addr}:{listen_port}")
    try:
        while True:
            conn, addr = sock.accept()
            threading.Thread(target=handle_tcp_client, args=(conn, addr, upstream_host, upstream_port, logger), daemon=True).start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("TCP server error:", e)

def main():
    parser = argparse.ArgumentParser(description="DNS proxy logger to CSV")
    parser.add_argument("--listen", default="0.0.0.0", help="listen address")
    parser.add_argument("--port", default=5353, type=int, help="listen port (UDP/TCP)")
    parser.add_argument("--upstream", default="8.8.8.8:53", help="upstream DNS (host:port)")
    parser.add_argument("--csv", default="csv/dns_log.csv", help="CSV output file")
    args = parser.parse_args()

    upstream_host, upstream_port_s = args.upstream.split(":")
    upstream_port = int(upstream_port_s)

    logger = CSVLogger(args.csv)
    t1 = threading.Thread(target=udp_server, args=(args.listen, args.port, upstream_host, upstream_port, logger), daemon=True)
    t2 = threading.Thread(target=tcp_server, args=(args.listen, args.port, upstream_host, upstream_port, logger), daemon=True)
    t1.start()
    t2.start()
    print("[*] DNS proxy running. CSV ->", args.csv)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("exiting...")
    finally:
        logger.close()

if __name__ == "__main__":
    main()
