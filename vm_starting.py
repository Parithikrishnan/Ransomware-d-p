import subprocess

# --- CONFIGURATION ---
QEMU_BIN = "/usr/bin/qemu-system-x86_64"        # QEMU binary path
VM_IMAGE = "/var/lib/libvirt/images/Alpine-mama.qcow2"  # Your existing VM disk image
RAM_MB = "2048"                                 # RAM size in MB
SHARED_DIR = "/home/r1ley/ransom"               # Shared folder (host ↔ guest)
# ----------------------

def start_vm():
    # QEMU command
    qemu_cmd = [
        QEMU_BIN,
        "-m", RAM_MB,                           # Allocate memory
        "-hda", VM_IMAGE,                       # VM disk image
        "-enable-kvm",                          # Enable hardware acceleration
        "-net", "nic",                          # Add a virtual NIC
        "-net", "user,hostfwd=tcp::2222-:22",   # Forward host port 2222 -> guest 22 (SSH)
        "-virtfs", f"local,path={SHARED_DIR},mount_tag=hostshare,security_model=passthrough,id=hostshare"
        # Remove '-nographic' if you want GUI window
    ]

    print("[+] Starting virtual machine...")
    proc = subprocess.Popen(qemu_cmd)

    print(f"[+] VM started with PID {proc.pid}")
    print("[+] Access VM display window or use: ssh -p 2222 user@127.0.0.1")
    return proc

if __name__ == "__main__":
    vm_process = start_vm()
    vm_process.wait()   # Wait until VM is shut down
