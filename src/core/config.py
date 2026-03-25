from RsInstrument import *
import pyvisa
from RsInstrument import RsInstrument
import os

"""
Developer : T0188303 - A.N.
Refactored for resilience: Paths are now relative to the project root.
"""

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Project directories
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
SETUP_DIR = os.path.join(BASE_DIR, 'setup')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Create directories if they don't exist
for d in [CONFIG_DIR, SETUP_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# These are the file names of the different configurations of the ZVA67
zva_s1p_config_ZVA67 = 's1p_setup.znxml'
zva_s2p_config_ZVA67 = 's2p_setup.znxml'
zva_s3p_config_ZVA67 = 's3p_setup.znxml'
zva_spst_config_ZVA67 = os.path.join(SETUP_DIR, 'SPST.znxml')

# These are the file names of the different configurations of the ZVA50
zva_s1p_config_ZVA50 = r's1p-zva50.zvx'
zva_s2p_config_ZVA50 = r's2p-zva50.zvx'
zva_s3p_config_ZVA50 = r's3p-zva50.zvx'

# PC File Paths for setups
pc_file_s1p = os.path.join(CONFIG_DIR, zva_s1p_config_ZVA50)
pc_file_s2p = os.path.join(CONFIG_DIR, zva_s2p_config_ZVA50)
pc_file_s3p = os.path.join(CONFIG_DIR, zva_s3p_config_ZVA50)

# This is the placeholder file used in the instrument to copy the configuration of the ZVA from the PC
# Note: These paths are usually on the instrument filesystem if it's Windows-based
instrument_file_ZVA67 = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\RecallSets\placeholder.znxml'
instrument_file_ZVA50 = r'C:\Rohde&Schwarz\Nwa\RecallSets\placeholder.zvx'

# Default placeholder file to be stored in the zva_parameter Dictionary
instrument_file = instrument_file_ZVA67

# Default directories for measurement data (simplified to a single DATA_DIR for resilience)
PC_File_Dir: str = DATA_DIR
PC_File_Dir_pull_in_Display: str = DATA_DIR
PC_File_Dir_s2p_Display: str = DATA_DIR
PC_File_Dir_s3p_Display: str = DATA_DIR
PC_File_Dir_s3p_Cycling: str = DATA_DIR

ZVA_File_Dir_ZVA67: str = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces'  # ZVA67 Trace file directory
ZVA_File_Dir_ZVA50: str = r'C:\Rohde&Schwarz\Nwa\Traces'  # ZVA50 Trace file directory

# Default trace directory
zva_traces: str = ZVA_File_Dir_ZVA67

# Use @py backend explicitly for Docker/Linux environments
try:
    rm = pyvisa.ResourceManager('@py')
except Exception:
    rm = pyvisa.ResourceManager()

# Dynamic Address Resolution
import os
from dotenv import load_dotenv
load_dotenv()

from src.core.network_utils import resolve_mdns_hostname
import re

def resolve_visa_address(address: str) -> str:
    """
    Translates hostname-based VISA addresses to IP-based ones if possible.
    """
    # Just a simple proxy/wrapper now, the logic remains but we use it via Env vars
    host_match = re.search(r'TCPIP0?::([^:]+)::', address)
    if host_match:
        hostname = host_match.group(1)
        if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', hostname):
            resolved_ip = resolve_mdns_hostname(hostname)
            if resolved_ip != hostname:
                address = address.replace(hostname, resolved_ip)
    return address

def open_resource_robust(rm, address):
    """
    Attempts to open a VISA resource. If standard VXI-11 (inst0) fails,
    tries direct socket connection on port 5025.
    """
    try:
        return rm.open_resource(address)
    except Exception as e:
        print(f"DEBUG: Standard connection failed for {address}: {e}")
        # Try fallbacks for TCPIP
        if "TCPIP" in address:
            # Try to extract IP
            ip_match = re.search(r'(\d{1,3}(\.\d{1,3}){3})', address)
            if ip_match:
                ip = ip_match.group(1)
                # Try raw socket port 5025 (standard SCPI)
                socket_address = f"TCPIP0::{ip}::5025::SOCKET"
                print(f"DEBUG: Attempting fallback to {socket_address}...")
                try:
                    res = rm.open_resource(socket_address)
                    res.read_termination = '\n'
                    res.write_termination = '\n'
                    return res
                except Exception as e2:
                    print(f"DEBUG: Fallback failed: {e2}")
        raise e

# IP Addresses for different apparatus
# Prioritize Environment Variables (set by host-side discovery)
# The .env file stores bare IPs (e.g. 169.254.5.21), so we wrap them into full VISA strings.
def make_visa_address(env_key: str, default_hostname: str) -> str:
    """Builds a VISA address from an env IP or falls back to mDNS hostname."""
    env_val = os.environ.get(env_key, '')
    if env_val:
        # If it looks like an IP, use it directly
        if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', env_val):
            return f'TCPIP0::{env_val}::inst0::INSTR'
        # If it looks like a full VISA string already
        if 'TCPIP' in env_val:
            return env_val
    # Fallback: try mDNS, then return a hostname-based VISA string
    resolved = resolve_mdns_hostname(default_hostname)
    return f'TCPIP0::{resolved}::inst0::INSTR'

signal_generator_ip: str = make_visa_address('SIG_GEN_IP', 'A-33521B-00526')
rf_generator_ip: str = make_visa_address('RF_GEN_IP', 'rssmb100a179766')
powermeter_ip: str = make_visa_address('POWERMETER_IP', '169.254.64.175')
oscilloscope_ip: str = make_visa_address('OSC_IP', 'DPO5054-C011738')

zva_env = os.environ.get('VNA_IP', '')
if zva_env and re.match(r'^\d{1,3}(\.\d{1,3}){3}$', zva_env):
    zva_ip_ZNA67: str = f'TCPIP0::{zva_env}::inst0::INSTR'
elif zva_env and 'TCPIP' in zva_env:
    zva_ip_ZNA67: str = zva_env
else:
    _zna_host = resolve_mdns_hostname('ZNA67-101810')
    zva_ip_ZNA67: str = f'TCPIP0::{_zna_host}::inst0::INSTR'
zva_ip_ZVA50: str = resolve_visa_address(r'TCPIP0::ZVx-000000::inst0::INSTR')

print(f"DEBUG: VNA Address: {zva_ip_ZNA67}")
print(f"DEBUG: SIG_GEN Address: {signal_generator_ip}")
print(f"DEBUG: RF_GEN Address: {rf_generator_ip}")
print(f"DEBUG: OSC Address: {oscilloscope_ip}")
print(f"DEBUG: POWERMETER Address: {powermeter_ip}")

ip_zva: str = zva_ip_ZNA67  # ZVA IP variable

zva_parameters: dict[str, str] = {
    'setup_s1p': pc_file_s1p, 'setup_s2p': pc_file_s2p, 'setup_s3p': pc_file_s3p, 'instrument_file': instrument_file,
    'zva_traces': zva_traces, 'ip_zva': ip_zva
}

def zva_directories(zva: RsInstrument) -> tuple[str, str, str, str, str]:
    global pc_file_s2p, pc_file_s3p, pc_file_s1p, instrument_file, zva_traces
    model = zva.idn_string
    if model == r"Rohde&Schwarz,ZVA50-4Port,1145111052100151,3.60":
        zva_parameters['setup_s1p'] = os.path.join(CONFIG_DIR, zva_s1p_config_ZVA50)
        zva_parameters['setup_s2p'] = os.path.join(CONFIG_DIR, zva_s2p_config_ZVA50)
        zva_parameters['setup_s3p'] = os.path.join(CONFIG_DIR, zva_s3p_config_ZVA50)
        zva_parameters['instrument_file'] = r'C:\Rohde&Schwarz\Nwa\RecallSets\placeholder.zvx'
        zva_parameters['zva_traces'] = ZVA_File_Dir_ZVA50
        zva_parameters['ip_zva'] = zva_ip_ZVA50

        pc_file_s1p = zva_parameters['setup_s1p']
        pc_file_s2p = zva_parameters['setup_s2p']
        pc_file_s3p = zva_parameters['setup_s3p']
        instrument_file = ZVA_File_Dir_ZVA50
        zva_traces = ZVA_File_Dir_ZVA50

    elif model == r"Rohde-Schwarz,ZNA67-4Port,1332450064101810,2.73":
        zva_parameters['setup_s1p'] = os.path.join(CONFIG_DIR, zva_s1p_config_ZVA67)
        zva_parameters['setup_s2p'] = os.path.join(CONFIG_DIR, zva_s2p_config_ZVA67)
        zva_parameters['setup_s3p'] = os.path.join(CONFIG_DIR, zva_s3p_config_ZVA67)
        zva_parameters['instrument_file'] = instrument_file_ZVA67
        zva_parameters['zva_traces'] = ZVA_File_Dir_ZVA67
        zva_parameters['ip_zva'] = zva_ip_ZNA67

        pc_file_s1p = zva_parameters['setup_s1p']
        pc_file_s2p = zva_parameters['setup_s2p']
        pc_file_s3p = zva_parameters['setup_s3p']
        instrument_file = instrument_file_ZVA67
        zva_traces = ZVA_File_Dir_ZVA67

    return pc_file_s1p, pc_file_s2p, pc_file_s3p, instrument_file, zva_traces

def zva_init(tcpip_address: str = zva_ip_ZNA67, zva="ZNA67") -> RsInstrument | None:
    _id = r'Vector Network Analyser'
    error = False
    if zva == "ZVA50":
        tcpip_address = zva_ip_ZVA50
    elif zva == "ZNA67":
        tcpip_address = zva_ip_ZNA67
    try:
        # options="SelectVisaBackend=rs" forces use of the installed visa backend (pyvisa-py in Docker)
        zva_inst = RsInstrument(tcpip_address, id_query=False, reset=False, options="SelectVisaBackend=rs")
        zva_inst.write_str_with_opc("SYSTem:DISPlay:UPDate ON")
        print("VNA Connected")
        return zva_inst
    except Exception as e:
        print(f"{_id} connection error: {e}")
        return None

def sig_gen_init(tcpip_address: str = signal_generator_ip) -> pyvisa.resources.tcpip.TCPIPInstrument | None:
    _id = "Signal Generator"
    try:
        sig_gen = open_resource_robust(rm, tcpip_address)
        print("Signal generator Connected")
        return sig_gen
    except Exception as e:
        print(f"{_id} connection error: {e}")
        return None

def osc_init(tcpip_address: str = oscilloscope_ip) -> pyvisa.resources.tcpip.TCPIPInstrument | None:
    _id = "Oscilloscope"
    try:
        osc = open_resource_robust(rm, tcpip_address)
        print("Oscilloscope Connected")
        return osc
    except Exception as e:
        print(f"{_id} connection error: {e}")
        return None

def rf_gen_init(tcpip_address: str = rf_generator_ip, rf_gen_type: str = 'smf') -> RsInstrument | None:
    _id = "RF Generator"
    try:
        if rf_gen_type == 'smf':
            tcpip_address = r'TCPIP0::rssmf100a105220::inst0::INSTR'
        # RsInstrument has its own robust logic, but we can pass options
        rf_gen = RsInstrument(tcpip_address, id_query=False, reset=False, options="SelectVisaBackend=rs")
        print("RF generator Connected")
        return rf_gen
    except Exception as e:
        print(f"{_id} connection error: {e}")
        return None

def powermeter_init(tcpip_address: str = r'TCPIP0::A-N1912A-00589::inst0::INSTR') -> pyvisa.resources.tcpip.TCPIPInstrument | None:
    _id = "Powermeter"
    try:
        powermeter = open_resource_robust(rm, tcpip_address)
        print("Powermeter Connected")
        return powermeter
    except Exception as e:
        print(f"{_id} connection error: {e}")
        return None

# Setup files
cycling_setup_oscilloscope = os.path.join(SETUP_DIR, 'setup-cycling-AN3.set')
pullin_setup_oscilloscope = os.path.join(SETUP_DIR, 'setup-pullin-AN.set')
cycling_setup_sig_gen = "CYCLE4kHz.sta"
cycling_setup_rf_gen = "setup-cycling.savrcltxt"
pullin_setup_sig_gen = "ramp.sta"
pullin_setup_rf_gen = "/var/user/pull-in.savrcltxt"
snp_meas_setup_sig_gen = "PULSE.sta"
power_test_setup_sig_gen = "power.sta"
power_test_setup_rf_gen = "/var/user/power.savrcltxt"
time_domain_power_test_setup_rf_gen = "/var/user/time-domain-power-test.savrcltxt"
power_test_setup_powermeter = "*RCL 3"
power_bias_test_setup_powermeter = "*RCL 5"

patterns = {
    '1%': '1000pulses_100us_pulse_dc1%_36Vtop40V_triangle.arb',
    '2%': '1000pulses_100us_pulse_dc2%_36Vtop40V_triangle.arb',
    '3%': '1000pulses_100us_pulse_dc3%_36Vtop40V_triangle.arb',
    '4%': '1000pulses_100us_pulse_dc4%_36Vtop40V_triangle.arb',
    '5%': '1000pulses_100us_pulse_dc5%_36Vtop40V_triangle.arb',
    '10%': '1000pulses_100us_pulse_dc10%_36Vtop40V_triangle.arb',
    '15%': '1000pulses_100us_pulse_dc15%_36Vtop40V_triangle.arb',
    '20%': '1000pulses_100us_pulse_dc20%_36Vtop40V_triangle.arb',
}

try:
    from src.hardware.mock_hardware import MockInstrument
except ImportError:
    class MockInstrument:
        def __init__(self, *args, **kwargs):
            print("WARNING: MockInstrument class not found. Using a placeholder.")
        def __getattr__(self, name):
            return lambda *args, **kwargs: print(f"WARNING: Called '{name}' on a placeholder mock instrument.")

def zva_init_mock(tcpip_address: str = 'MOCK_ZVA', zva="ZNA67"):
    return MockInstrument(tcpip_address)

def sig_gen_init_mock(tcpip_address: str = 'MOCK_SIG_GEN'):
    return MockInstrument(tcpip_address)

def osc_init_mock(tcpip_address: str = 'MOCK_OSC'):
    return MockInstrument(tcpip_address)

def rf_gen_init_mock(tcpip_address: str = 'MOCK_RF_GEN', rf_gen_type: str = 'smf'):
    return MockInstrument(tcpip_address)

def powermeter_init_mock(tcpip_address: str = 'MOCK_POWERMETER'):
    return MockInstrument(tcpip_address)
