import os
import subprocess
import platform
import re
from src.core.network_utils import resolve_mdns_hostname

def ping_host(host):
    """wl
    Returns True if host responds to a ping request.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

instruments = {
    "VNA (ZNA67)": "ZNA67-101810",
    "Signal Generator": "A-33521B-00526",
    "RF Generator": "rssmb100a179766",
    "Oscilloscope": "DPO5054-C011738",
    "Powermeter": "169.254.64.175"
}

print("--- Dynamic Hardware Discovery Test (Docker) ---")
for name, hostname in instruments.items():
    # If it's already an IP, just ping it
    if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', hostname):
        resolved_ip = hostname
    else:
        print(f"Resolving {name} ({hostname})...")
        resolved_ip = resolve_mdns_hostname(hostname)
    
    status = "REACHABLE" if ping_host(resolved_ip) else "UNREACHABLE"
    
    if resolved_ip != hostname:
        print(f"{name}: {hostname} -> {resolved_ip} : {status}")
    else:
        print(f"{name}: {hostname} : {status}")

print("-----------------------------------------------")
print("If status is REACHABLE, the app will now connect automatically using names.")
