import os
import time

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

while True:
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in RANSOM_EXTS:
                print(os.path.join(root, f))
    time.sleep(interval)
