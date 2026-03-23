import socket
import time
import logging
from typing import Optional
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

# Suppress zeroconf logging unless needed
logging.getLogger('zeroconf').setLevel(logging.ERROR)

class InstrumentListener(ServiceListener):
    def __init__(self, target_hostname: str):
        self.target_hostname = target_hostname.lower().split('.')[0] # Remove .local if present
        self.found_ip: Optional[str] = None

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info:
            # The service name usually looks like "hostname._vxi-11._tcp.local."
            host_part = info.server.lower().split('.')[0]
            if host_part == self.target_hostname:
                addresses = info.parsed_addresses()
                if addresses:
                    self.found_ip = addresses[0]

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

def resolve_mdns_hostname(hostname: str, timeout: float = 2.0) -> str:
    """
    Attempts to resolve a hostname (like 'ZNA67-101810') to an IP address 
    using mDNS (Zeroconf) browsing.
    Returns the original hostname if resolution fails.
    """
    # 1. Try standard socket resolution first (might work on host or if DNS is configured)
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        pass

    # 2. Try mDNS discovery
    zeroconf = Zeroconf()
    listener = InstrumentListener(hostname)
    
    # Common instrument service types
    services = ["_vxi-11._tcp.local.", "_hislip._tcp.local.", "_lxi._tcp.local.", "_http._tcp.local."]
    
    browser = ServiceBrowser(zeroconf, services, listener)
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if listener.found_ip:
            break
        time.sleep(0.1)
    
    zeroconf.close()
    
    if listener.found_ip:
        print(f"DEBUG: Resolved {hostname} to {listener.found_ip} via mDNS")
        return listener.found_ip
    
    return hostname # Fallback to original hostname
