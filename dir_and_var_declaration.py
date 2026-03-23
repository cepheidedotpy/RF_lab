from RsInstrument import *
import pyvisa
from RsInstrument import RsInstrument
import os

"""
Developer : T0188303 - A.N.
Refactored for resilience: Paths are now relative to the project root.
This file handles directory and configuration file declaration.
"""

# Base directory for the project (current directory since this file is in the root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
instrument_file_ZVA67 = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\RecallSets\placeholder.znxml'
instrument_file_ZVA50 = r'C:\Rohde&Schwarz\Nwa\RecallSets\placeholder.zvx'

# Default placeholder file to be stored in the zva_parameter Dictionary
instrument_file = instrument_file_ZVA67

# Default directories for measurement data
PC_File_Dir: str = DATA_DIR
PC_File_Dir_pull_in_Display: str = DATA_DIR
PC_File_Dir_s2p_Display: str = DATA_DIR
PC_File_Dir_s3p_Display: str = DATA_DIR
PC_File_Dir_s3p_Cycling: str = DATA_DIR

ZVA_File_Dir_ZVA67: str = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces'  # ZVA67 Trace file directory
ZVA_File_Dir_ZVA50: str = r'C:\Rohde&Schwarz\Nwa\Traces'  # ZVA50 Trace file directory

# Default trace directory
zva_traces: str = ZVA_File_Dir_ZVA67

rm = pyvisa.ResourceManager()

# IP Addresses
signal_generator_ip: str = r'TCPIP0::A-33521B-00526::inst0::INSTR'
rf_generator_ip: str = r'TCPIP0::rssmb100a179766::inst0::INSTR'
powermeter_ip: str = r'TCPIP0::169.254.64.175::inst0::I=STR'
oscilloscope_ip: str = r'TCPIP0::DPO5054-C011738::inst0::INSTR'

zva_ip_ZNA67: str = r'TCPIP0::ZNA67-101810::inst0::INSTR'
zva_ip_ZVA50: str = r'TCPIP0::ZVx-000000::inst0::INSTR'

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
        pc_file_s1p, pc_file_s2p, pc_file_s3p = zva_parameters['setup_s1p'], zva_parameters['setup_s2p'], zva_parameters['setup_s3p']
        instrument_file = ZVA_File_Dir_ZVA50
        zva_traces = ZVA_File_Dir_ZVA50
    elif model == r"Rohde-Schwarz,ZNA67-4Port,1332450064101810,2.73":
        zva_parameters['setup_s1p'] = os.path.join(CONFIG_DIR, zva_s1p_config_ZVA67)
        zva_parameters['setup_s2p'] = os.path.join(CONFIG_DIR, zva_s2p_config_ZVA67)
        zva_parameters['setup_s3p'] = os.path.join(CONFIG_DIR, zva_s3p_config_ZVA67)
        zva_parameters['instrument_file'] = instrument_file_ZVA67
        zva_parameters['zva_traces'] = ZVA_File_Dir_ZVA67
        zva_parameters['ip_zva'] = zva_ip_ZNA67
        pc_file_s1p, pc_file_s2p, pc_file_s3p = zva_parameters['setup_s1p'], zva_parameters['setup_s2p'], zva_parameters['setup_s3p']
        instrument_file = instrument_file_ZVA67
        zva_traces = ZVA_File_Dir_ZVA67
    return pc_file_s1p, pc_file_s2p, pc_file_s3p, instrument_file, zva_traces

def zva_init(tcpip_address: str = zva_ip_ZNA67, zva="ZNA67") -> RsInstrument | None:
    error = False
    if zva == "ZVA50": tcpip_address = zva_ip_ZVA50
    elif zva == "ZNA67": tcpip_address = zva_ip_ZNA67
    try:
        inst = RsInstrument(tcpip_address, id_query=False, reset=False)
        inst.write_str_with_opc("SYSTem:DISPlay:UPDate ON")
        print("VNA Connected")
        return inst
    except Exception as e:
        print(f"VNA connection error: {e}")
        return None

def sig_gen_init(tcpip_address: str = signal_generator_ip):
    try:
        sig_gen = rm.open_resource(tcpip_address)
        print("Signal generator Connected")
        return sig_gen
    except Exception as e:
        print(f"Signal generator error: {e}")
        return None

def osc_init(tcpip_address: str = oscilloscope_ip):
    try:
        osc = rm.open_resource(tcpip_address)
        print("Oscilloscope Connected")
        return osc
    except Exception as e:
        print(f"Oscilloscope error: {e}")
        return None

def rf_gen_init(tcpip_address: str = rf_generator_ip, rf_gen_type: str = 'smf'):
    try:
        if rf_gen_type == 'smf': tcpip_address = r'TCPIP0::rssmf100a105220::inst0::INSTR'
        rf_gen = RsInstrument(tcpip_address, id_query=False, reset=False)
        print("RF generator Connected")
        return rf_gen
    except Exception as e:
        print(f"RF generator error: {e}")
        return None

def powermeter_init(tcpip_address: str = r'TCPIP0::A-N1912A-00589::inst0::INSTR'):
    try:
        pm = rm.open_resource(tcpip_address)
        print("Powermeter Connected")
        return pm
    except Exception as e:
        print(f"Powermeter error: {e}")
        return None

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
    from dev.mock_hardware import MockInstrument
except ImportError:
    class MockInstrument:
        def __init__(self, *args, **kwargs): pass
        def __getattr__(self, name): return lambda *args, **kwargs: None

def zva_init_mock(t='MOCK_ZVA', z="ZNA67"): return MockInstrument(t)
def sig_gen_init_mock(t='MOCK_SIG_GEN'): return MockInstrument(t)
def osc_init_mock(t='MOCK_OSC'): return MockInstrument(t)
def rf_gen_init_mock(t='MOCK_RF_GEN', r='smf'): return MockInstrument(t)
def powermeter_init_mock(t='MOCK_POWERMETER'): return MockInstrument(t)
