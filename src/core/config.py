from RsInstrument import *
import pyvisa
from RsInstrument import RsInstrument

"""
Developer : T0188303 - A.N.
This file is used for directory and configuration file declaration. 2 VNAs are supported. ZVA67 and ZVA50.
Switching between the two should be transparent for the Main program user. The IP addresses of the different apparatus 
is also declared within this file. 

zva_parameter: Dictionary handling the different zva parameters. This dictionary is configured after VNA connection.
The different parameters handled are:
- setup_s1p, setup_s2p setup_s3p: Setups for S1P, S2P and S3P measurement. These files are sent from the PC to a 
"Placeholder" configuration file.
This configuration file is called when a setup button is pressed. This allows for local storage of the ZVA configuration
files.
- instrument_file: This variable stores the placeholder file directory and file name in order to be accessed during
ZVA configuration.
- zva_traces: This variable stores the directory of the traces to be transferred from VNA to PC
- ip_zva: This variable stores the ip address of the VNA

"""
# These are the file names of the different configurations of the ZVA67
zva_s1p_config_ZVA67 = 's1p_setup.znxml'
zva_s2p_config_ZVA67 = 's2p_setup.znxml'
zva_s3p_config_ZVA67 = 's3p_setup.znxml'
zva_spst_config_ZVA67 = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\RecallSets\SPST.znxml'

# These are the file names of the different configurations of the ZVA67
zva_s1p_config_ZVA50 = r's1p-zva50.zvx'
zva_s2p_config_ZVA50 = r's2p-zva50.zvx'
zva_s3p_config_ZVA50 = r's3p-zva50.zvx'

# PC File Path on our PC
pc_file_s1p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s1p_config_ZVA50)
pc_file_s2p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s2p_config_ZVA50)
pc_file_s3p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s3p_config_ZVA50)

# This is the placeholder file used in the instrument to copy the configuration of the ZVA from the PC
instrument_file_ZVA67 = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\RecallSets\placeholder.znxml'
instrument_file_ZVA50 = r'C:\Rohde&Schwarz\Nwa\RecallSets\placeholder.zvx'

# Default placeholder file to be stored in the zva_parameter Dicitonnary
instrument_file = instrument_file_ZVA67

PC_File_Dir: str = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data'  # Default directory for measurement data
PC_File_Dir_pull_in_Display: str = PC_File_Dir
PC_File_Dir_s2p_Display: str = PC_File_Dir
PC_File_Dir_s3p_Display: str = PC_File_Dir
PC_File_Dir_s3p_Cycling: str = PC_File_Dir

ZVA_File_Dir_ZVA67: str = r'C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces'  # ZVA67 Trace file directory
ZVA_File_Dir_ZVA50: str = r'C:\Rohde&Schwarz\Nwa\Traces'  # ZVA50 Trace file directory

# Default trace directory
zva_traces: str = ZVA_File_Dir_ZVA67
# zva_traces: str = ZVA_File_Dir_ZVA67

rm = pyvisa.ResourceManager()

# global ip_zva, signal_generator_ip, ip_zva, rf_generator_ip, powermeter_ip, oscilloscope_ip
# def define_ip_addresses():

signal_generator_ip: str = r'TCPIP0::A-33521B-00526::inst0::INSTR'
rf_generator_ip: str = r'TCPIP0::rssmb100a179766::inst0::INSTR'
powermeter_ip: str = r'TCPIP0::169.254.64.175::inst0::I=STR'
oscilloscope_ip: str = r'TCPIP0::DPO5054-C011738::inst0::INSTR'

# define_ip_addresses()

zva_ip_ZNA67: str = r'TCPIP0::ZNA67-101810::inst0::INSTR'
zva_ip_ZVA50: str = r'TCPIP0::ZVx-000000::inst0::INSTR'

ip_zva: str = zva_ip_ZNA67  # ZVA IP variable

zva_parameters: dict[str: str] = {
    'setup_s1p': pc_file_s1p, 'setup_s2p': pc_file_s2p, 'setup_s3p': pc_file_s3p, 'instrument_file': instrument_file,
    'zva_traces': zva_traces, 'ip_zva': ip_zva
}


def zva_directories(zva: RsInstrument) -> tuple[str, str, str, str, str]:
    global pc_file_s2p, pc_file_s3p, pc_file_s1p, instrument_file, zva_traces
    model = zva.idn_string
    if model == r"Rohde&Schwarz,ZVA50-4Port,1145111052100151,3.60":
        zva_parameters['setup_s1p'] = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(
            zva_s1p_config_ZVA50)
        zva_parameters['setup_s2p'] = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(
            zva_s2p_config_ZVA50)
        zva_parameters['setup_s3p'] = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(
            zva_s3p_config_ZVA50)
        zva_parameters['instrument_file'] = r'C:\Rohde&Schwarz\Nwa\RecallSets\placeholder.zvx'
        zva_parameters['zva_traces'] = ZVA_File_Dir_ZVA50
        zva_parameters['ip_zva'] = zva_ip_ZVA50

        pc_file_s1p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s1p_config_ZVA50)
        pc_file_s2p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s2p_config_ZVA50)
        pc_file_s3p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s3p_config_ZVA50)
        instrument_file = ZVA_File_Dir_ZVA50
        zva_traces = ZVA_File_Dir_ZVA50

    elif model == r"Rohde-Schwarz,ZNA67-4Port,1332450064101810,2.73":
        zva_parameters['setup_s1p'] = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(
            zva_s1p_config_ZVA67)
        zva_parameters['setup_s2p'] = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(
            zva_s2p_config_ZVA67)
        zva_parameters['setup_s3p'] = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(
            zva_s3p_config_ZVA67)
        zva_parameters['instrument_file'] = instrument_file_ZVA67
        zva_parameters['zva_traces'] = ZVA_File_Dir_ZVA67
        zva_parameters['ip_zva'] = zva_ip_ZNA67

        pc_file_s1p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s1p_config_ZVA67)
        pc_file_s2p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s2p_config_ZVA67)
        pc_file_s3p = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\ZVA config\{}'.format(zva_s3p_config_ZVA67)
        instrument_file = instrument_file_ZVA67
        zva_traces = ZVA_File_Dir_ZVA67

    return pc_file_s1p, pc_file_s2p, pc_file_s3p, instrument_file, zva_traces


def zva_init(tcpip_address: str = r'TCPIP0::ZNA67-101810::inst0::INSTR', zva="ZNA67") -> RsInstrument | None:
    _id = r'Vector Network Analyser'
    error = False
    zva_name = zva
    if zva_name == "ZVA50":
        tcpip_address = zva_ip_ZVA50

    elif zva_name == "ZNA67":
        tcpip_address = zva_ip_ZNA67
    try:
        zva = RsInstrument(tcpip_address, id_query=False, reset=False)
        print(type(zva))
        zva.write_str_with_opc("SYSTem:DISPlay:UPDate ON")
    except TimeoutException as e:
        error = True
        print(e.args[0])
        print('Timeout Error in ZVA')
    except StatusException as e:
        error = True
        print(e.args[0])
        print('Status Error in ZVA')
    except ResourceError as e:
        error = True
        print(e.args[0])
        print('Status Error in ZVA')
    except RsInstrException as e:
        error = True
        print(e.args[0])
        print('Status Error in ZVA')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("VNA Connected")
        return zva


def sig_gen_init(
        tcpip_address: str = r'TCPIP0::A-33521B-00526::inst0::INSTR') -> pyvisa.resources.tcpip.TCPIPInstrument | None:
    _id = "Signal Generator"
    error = False
    sig_gen = None
    try:
        sig_gen = rm.open_resource(tcpip_address)
        print(type(sig_gen))
    except pyvisa.VisaIOError as e:
        error = True
        print(e.args[0])
        print(f'Error {e} occurred in signal generator')
    except pyvisa.VisaTypeError as e:
        error = True
        print(e.args[0])
        print(f'Error {e} occurred occurred in signal generator')
    except ResourceError as e:
        error = True
        print(e.args[0])
        print('Resource Error in signal generator')
    except pyvisa.VisaIOWarning as e:
        error = True
        print(f'Error {e} occurred occurred in signal generator')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("Signal generator Connected")
        return sig_gen


def osc_init(
        tcpip_address: str = r'TCPIP0::DPO5054-C011738::inst0::INSTR') -> pyvisa.resources.tcpip.TCPIPInstrument | None:
    _id = "Oscilloscope"
    error = False
    osc = None
    try:
        osc = rm.open_resource(tcpip_address)
        print(type(osc))
    except pyvisa.VisaIOError as e:
        error = True
        print(f'Error {e} occurred in oscilloscope')
    except pyvisa.VisaTypeError as e:
        error = True
        print(f'Error {e} occurred in oscilloscope')
    except pyvisa.VisaIOWarning as e:
        error = True
        print(f'Error {e} occurred in oscilloscope')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("Oscilloscope Connected")
        return osc


def rf_gen_init(tcpip_address: str = r'TCPIP0::rssmb100a179766::inst0::INSTR',
                rf_gen_type: str = 'smf') -> RsInstrument | None:
    _id = "RF Generator"
    error = False
    rf_gen = None
    if rf_gen_type == 'smf':
        tcpip_address = r'TCPIP0::rssmf100a105220::inst0::INSTR'
        try:
            rf_gen = RsInstrument(tcpip_address, id_query=False, reset=False)
            print(type(rf_gen))
        except TimeoutException as e:
            error = True
            print(e.args[0])
            print('Timeout Error in RF generator')
        except StatusException as e:
            error = True
            print(e.args[0])
            print('Status Error in RF generator')
        except ResourceError as e:
            error = True
            print(e.args[0])
            print('Resource Error in RF generator')
        except RsInstrException as e:
            error = True
            print(e.args[0])
            print('Exception Error  in RF generator')
        if error:
            print(f"{_id} connection error", end='\n')
        else:
            print("RF generator Connected")
    elif rf_gen_type == 'smb':
        try:
            tcpip_address = r'TCPIP0::rssmb100a179766::inst0::INSTR'
            rf_gen = RsInstrument(tcpip_address, id_query=False, reset=False)
            print(type(rf_gen))
        except TimeoutException as e:
            error = True
            print(e.args[0])
            print('Timeout Error in RF generator')
        except StatusException as e:
            error = True
            print(e.args[0])
            print('Status Error in RF generator')
        except ResourceError as e:
            error = True
            print(e.args[0])
            print('Resource Error in RF generator')
        except RsInstrException as e:
            error = True
            print(e.args[0])
            print('Exception Error  in RF generator')
        if error:
            print(f"{_id} connection error", end='\n')
        else:
            print("RF generator Connected")
        return rf_gen


def powermeter_init(
        tcpip_address: str = r'TCPIP0::A-N1912A-00589::inst0::INSTR') -> pyvisa.resources.tcpip.TCPIPInstrument | None:
    _id = "Powermeter"
    error = False
    powermeter = None
    try:
        powermeter = rm.open_resource(tcpip_address)
        print(type(powermeter))
    except pyvisa.VisaIOError as e:
        error = True
        print(f'Error {e} occurred')
    except pyvisa.VisaTypeError as e:
        error = True
        print(f'Error {e} occurred')
    except ResourceError as e:
        error = True
        print(e.args[0])
    except pyvisa.VisaIOWarning as e:
        error = True
        print(f'Error {e} occurred')
    if error:
        print(f"{_id} connection error", end='\n')
    else:
        print("Powermeter Connected")
        return powermeter


cycling_setup_oscilloscope = r'C:/Users/Tek_Local_Admin/Desktop/fiab/setup-cycling-AN3.set'
pullin_setup_oscilloscope = r'C:/Users/Tek_Local_Admin/Desktop/fiab/setup-pullin-AN.set'
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
    # Handle the case where mock_hardware is not available, e.g., in a different environment
    class MockInstrument:
        def __init__(self, *args, **kwargs):
            print("WARNING: MockInstrument class not found. Using a placeholder.")

        def __getattr__(self, name):
            # Return a dummy callable for any method call
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
