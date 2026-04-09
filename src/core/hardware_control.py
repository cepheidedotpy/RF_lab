import os
import time
import typing
import traceback
import pyvisa
import numpy as np
from functools import wraps
from RsInstrument import RsInstrument, RsInstrException, TimeoutException, StatusException
from src.core import config as dir_and_var_declaration
from src.core.config import (
    zva_init, sig_gen_init, osc_init, rf_gen_init, powermeter_init,
    zva_init_mock, sig_gen_init_mock, osc_init_mock, rf_gen_init_mock, powermeter_init_mock
)

rm: typing.Optional[pyvisa.ResourceManager] = None
signal_generator: typing.Optional[pyvisa.resources.tcpip.TCPIPInstrument] = None
osc: typing.Optional[pyvisa.resources.tcpip.TCPIPInstrument] = None
zva: typing.Optional[RsInstrument] = None
rf_Generator: typing.Optional[RsInstrument] = None
powermeter: typing.Optional[pyvisa.resources.tcpip.TCPIPInstrument] = None

def initialize_hardware(zva_ip: str, sig_gen_ip: str, osc_ip: str, powermeter_ip: str, rf_gen_ip: str, offline=False):
    global rm, osc, signal_generator, zva, powermeter, rf_Generator
    if offline:
        print("INFO: Running in OFFLINE mode.")
        rm = None  # or a mock resource manager if needed
        signal_generator = sig_gen_init_mock()
        osc = osc_init_mock()
        zva = zva_init_mock()
        powermeter = powermeter_init_mock()
        rf_Generator = rf_gen_init_mock()
        return

    try:
        rm = pyvisa.ResourceManager()
        signal_generator = sig_gen_init(sig_gen_ip)
        osc = osc_init(osc_ip)
        zva = zva_init(tcpip_address=zva_ip, zva="ZNA67")
        powermeter = powermeter_init(powermeter_ip)
        rf_Generator = rf_gen_init(tcpip_address=rf_gen_ip, rf_gen_type='smb')

        # Injectized instruments into dependent modules to fix the 'NoneType' namespace issue
        try:
            import src.core.scripts_and_functions as saf
            saf.osc = osc
            saf.signal_generator = signal_generator
            saf.powermeter = powermeter
            saf.rf_Generator = rf_Generator
            saf.zva = zva
        except ImportError:
            pass

        try:
            import src.core.data_processing as dp
            dp.osc = osc
        except ImportError:
            pass

        # Configure zva_parameters for the connected VNA model
        if zva is not None:
            dir_and_var_declaration.zva_directories(zva)
    except Exception as e:
        print(f"Hardware initialization failed: {e}")
        print("Running in offline mode. Some functionality will be disabled.")
        rm = None
        signal_generator = None
        osc = None
        zva = None
        powermeter = None
        rf_Generator = None

def sig_gen_opc_control(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        opc_test = '0'
        while opc_test == '0':
            time.sleep(0.1)
            opc_test = signal_generator.query("*OPC?").removesuffix('\n')
            if opc_test == 0:
                print(f'Operation still in progress OPC_value={opc_test}')
            else:
                print(f'{function.__name__} execution done!')
        return result

    return wrapper

def rf_gen_opc_control(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        opc_test = '0'
        while opc_test == '0':
            time.sleep(0.1)
            opc_test = rf_Generator.query("*OPC?").removesuffix('\n')
            if opc_test == 0:
                print(f'Operation still in progress OPC_value={opc_test}')
            else:
                print(f'{function.__name__} execution done!')
        return result

    return wrapper

def powermeter_opc_control(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        opc_test = '0'
        while opc_test == '0':
            time.sleep(0.1)
            opc_test = powermeter.query("*OPC?").removesuffix('\n')
            if opc_test == 0:
                print(f'Operation still in progress OPC_value={opc_test}')
            else:
                print(f'{function.__name__} execution done!')
        return result

    return wrapper

@sig_gen_opc_control
def bias_voltage(voltage: str = '10') -> float:
    """
     Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage = user_input/20]
     because of the voltage amplifier
    :param voltage: voltage value
    :return: Set voltage at the amplifier output
    """
    # Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage =
    # user_input/20] because of the amplifier
    voltage_at_sig_gen = float(voltage) / 20
    print(voltage_at_sig_gen)
    signal_generator.write("SOURce:VOLTage:OFFSET 0")
    signal_generator.write("SOURce:VOLTage:LOW 0")
    signal_generator.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    probe_voltage = signal_generator.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(signal_generator.query("SOURce:VOLTage?")) * 20
    print(set_voltage)
    return set_voltage

@sig_gen_opc_control
def bias_pull_in_voltage(voltage: str = 1) -> float:
    # Set bias voltage from user input to correspond to signal generator input. [sig_gen_voltage = user_input/20]
    # because of the amplifier
    voltage_at_sig_gen = float(voltage) / 20
    print(voltage_at_sig_gen)
    signal_generator.write("SOURce:VOLTage:OFFSET 0")
    signal_generator.write("SOURce:VOLTage:LOW -{}".format(voltage_at_sig_gen))
    signal_generator.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    probe_voltage = signal_generator.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(signal_generator.query("SOURce:VOLTage?")) * 20
    print(set_voltage)
    return set_voltage

@sig_gen_opc_control
def ramp_width(width: float = 100) -> None:  # Set ramp length (µs) in pull down voltage test
    frequency_gen = 1 / (4 * float(width * 10 ** (-6)))
    print(f"Ramp frequency = {frequency_gen / 1e3} kHz")
    try:
        signal_generator.write('SOURce1:FUNCtion:RAMP:SYMMetry 50')  # selecting pulse function
        signal_generator.write('FREQuency {}'.format(frequency_gen))
        signal_generator.write('OUTPut 1')  # Turn on output
        error_log = signal_generator.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            signal_generator.write('FREQuency {}'.format(frequency_gen))
        time.sleep(1)
    except pyvisa.VisaIOError:
        print('Signal Generator VisaIOError')

def set_f_start(f_start: float = 1) -> None:  # Set start frequency function
    # f_converted = f_start+'E'+'9' # string
    f_converted = f_start * 10 ** 9  # float
    zva.write_str_with_opc("FREQ:STAR {}".format(f_converted, type='E'))
    print("F_start is set to {} GHz \n".format(f_start))

def set_fstop(fstop: float = 10) -> None:  # Set stop frequency function
    # f_converted = f_stop+'E'+'9' # string
    f_converted = fstop * 10 ** 9  # float
    zva.write_str_with_opc("FREQ:STOP {}".format(f_converted, type='E'))
    print("Fstop is set to {} GHz \n".format(fstop))

def number_of_points(points: float = 501) -> None:  # Set Number of points function
    zva.write_str_with_opc("SWEep:POINts {}".format(points))
    print("Number of points set to {} points \n".format(points))

def set_pulse_width(
        width: float = 10) -> None:  # Set the pulse width as a function of the VNA sweep time in S parameter
    # measurement
    try:
        width_converted = width  # float
        print("Pulse width: {} s".format(width_converted, type='E', precision=2), end='\n')
        signal_generator.write("SOURce1:FUNCtion:PULSe:WIDTh {}".format(width_converted, type='E'))
        pri = signal_generator.query("SOURce1:FUNCtion:PULSe:PERiod?").split('\n')[0]
        # print(f"pri={pri} s")
        prf = 1 / float(pri)
        print(f"prf={prf} Hz\npri={pri} s")
        sweep_time = zva.query_str_with_opc("SWEep:TIME?")
        print(f"Sweep time={sweep_time} s")
        if float(sweep_time) > width_converted:
            print("Pulse width is too small for a complete sweep measurement", end='\n')
            prf_req = 1 / float(sweep_time)
            print("Minimum pulse length is: {}\nRequired prf={} Hz".format(sweep_time, prf_req), end='\n')
    finally:
        print_error_log()

def sig_gen_set_output_log() -> str:  # Get error log of the signal generator
    a = r"Bias voltage set to {} V".format(float(signal_generator.query("SOURce:VOLTage?")) * 20)
    b = r"Pulse width is set to {} s".format(float(signal_generator.query("SOURce1:FUNCtion:PULSe:WIDTh?")))
    c = r"prf set to {} Hz".format(1 / float(signal_generator.query("SOURce1:FUNCtion:PULSe:PERiod?")))
    return a + '\n' + b + '\n' + c

@sig_gen_opc_control
def set_prf(prf: float = 1e3) -> str:  # Set pulse repetition frequency
    pri = 1 / prf
    width = signal_generator.query("SOURce1:FUNCtion:PULSe:WIDTh?").split('\n')[0]
    print(f"Pulse width = {width} s")
    if float(width) > pri:
        print("Pulse width is too large, settings conflict\nMax Pulse width must be < {}".format(pri))
        error_log = "Pulse width is too large, settings conflict\nMax Pulse width must be < {}".format(pri)
    else:
        signal_generator.write("SOURce1:FUNCtion:PULSe:PERiod {}".format(pri))
        error_log = f"Pulse width set to {width}"
    return error_log

def set_zva(start: float = 1, stop: float = 10, points: float = 501) -> None:
    # Configure the ZVA with all the input parameters entered the GUI
    set_f_start(start)
    print("Fstart is set to {} GHz \n".format(float(zva.query("FREQ:STARt?")) / (10 ** 9)))
    set_fstop(stop)
    print("Fstop is set to {} GHz \n".format(float(zva.query("FREQ:STOP?")) / (10 ** 9)))
    number_of_points(points)
    print("Number of points set to {} points \n".format(zva.query("SWEep:POINts?")))

def sig_gen_set_output_ramp_log() -> str:  # Set the ramp parameters in pull down voltage test
    a = r"Ramp voltage is set to {} V".format(
        float(signal_generator.query("SOURce:VOLTage?")) * (20 / 2))  # Gain amplifier = 20, Vcc/2
    b = r"Ramp duration is set to {} µs".format(10 ** 6 * 1 / (4 * float(signal_generator.query("FREQuency?"))))
    return f"{a}'\n'{b}"

def zva_set_output_log() -> str:  # Get error log of the ZVA
    a = r"Fstart is set to {} GHz".format(float(zva.query("FREQ:STARt?")) / (10 ** 9))
    b = r"Fstop is set to {} GHz".format(float(zva.query("FREQ:STOP?")) / (10 ** 9))
    c = r"Number of points set to {} points".format(zva.query("SWEep:POINts?"))
    return f"{a}'\n'{b}'\n'{c}"

def trigger_measurement_zva():  # Trigger the ZVA using the signal generator
    # zva.write_str_with_opc('TRIGger:SOURce EXTernal')  # >>>>>>>>> UNCOMMENT THIS LINE <<<<<<<<<<<<<<<<<<<<<<
    signal_generator.write('TRIG')
    signal_generator.query('*OPC?')
    # time.sleep(2)
    print("Signal generator sent Trigger pulse \n")

@powermeter_opc_control
def powermeter_config_power_bias() -> None:
    powermeter.write('*RST')
    powermeter.write(f'{dir_and_var_declaration.power_bias_test_setup_powermeter}')

@powermeter_opc_control
def powermeter_config_power_test() -> None:
    powermeter.write('*RST')
    powermeter.write(f'{dir_and_var_declaration.power_test_setup_powermeter}')

def comprep_zva():  # Preparation of the communication
    if zva is None:
        print("ZVA not initialized, skipping comms prep")
        return
    zva.visa_timeout = 5000
    zva.opc_timeout = 5000
    zva.instrument_status_checking = True
    zva.clear_status()
    print("Comms are ready")

def close_resource(resource: RsInstrument | pyvisa.Resource) -> None:
    if resource == RsInstrument:
        print(f"Closing {resource.__str__}")
    elif resource == pyvisa.Resource:
        print(f"Closing {resource.__repr__}")
    resource.close()

def close_zva() -> None:
    # Close VISA Session
    zva.close()
    print("ZVA session closed \n")

def close_sig_gen() -> None:
    # Close signal generator VISA Session
    signal_generator.close()
    print("Signal generator session closed \n")

def close_osc() -> None:
    # Close oscilloscope VISA Session
    osc.close()
    print("Oscilloscope session closed \n")

def close_rf_gen() -> None:  # Close rf generator VISA Session
    rf_Generator.close()
    print("RF generator session closed \n")

def close_powermeter() -> None:  # Close powermeter VISA Session
    powermeter.close()
    print("Powermeter session closed \n")

def close_all_resources() -> None:  # Close all resources VISA Session
    instrument_list: list[RsInstrument | pyvisa.Resource | None] = [signal_generator, zva, osc, rf_Generator,
                                                                    powermeter]
    for instrument in instrument_list:
        if instrument is not None:
            try:
                instrument.close()
                print(f"{instrument} closed")
            except pyvisa.errors.VisaIOError as e:
                print(f"Error closing {instrument}: {e}")

def setup_zva_with_rst(ip: str) -> None:
    global zva  # Declare zva as global
    # Resetting the ZNA67 or ZVA50
    zva = RsInstrument('{}'.format(ip), id_query=True, reset=True)
    zva.opc_query_after_write = True
    zva.write_str_with_opc(
        r"MMEMory:LOAD:STATe 1, '{}'".format(dir_and_var_declaration.zva_parameters["instrument_file"]))
    zva.write_str_with_opc("SYSTem:DISPlay:UPDate ON")
    print('ZVA Reset complete!', end='\n')

def setup_zva_no_rst(ip: str) -> None:
    global zva  # Declare zva as global
    zva = RsInstrument('{}'.format(ip), id_query=True, reset=False)
    zva.opc_query_after_write = True
    zva.write_str_with_opc("SYSTem:DISPlay:UPDate ON")
    print('ZVA Reset complete!', end='\n')

def setup_signal_generator_pulsed_with_rst(ip: str) -> pyvisa.resources.tcpip.TCPIPInstrument:
    global signal_generator
    print(dir_and_var_declaration.snp_meas_setup_sig_gen)
    signal_generator = rm.open_resource(r'{}'.format(ip))
    signal_generator.write('*RST')
    time.sleep(0.5)
    signal_generator.write('OUTput OFF')
    time.sleep(0.5)
    signal_generator.write(
        'MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.snp_meas_setup_sig_gen))  # Load STATE_4
    time.sleep(0.5)
    signal_generator.write('TRIGger:SOURce EXTernal')
    signal_generator.write('BURSt:STATe 1')
    signal_generator.write('BURS:NCYC 1')
    signal_generator.write('OUTput ON')

    error_log = signal_generator.query('SYSTem:ERRor?')
    print('Signal generator Reset complete!', end='\n')
    return signal_generator

def configuration_sig_gen(frequency_gen: float = 150, amplitude: float = 1, pulse_width: float = 0.001333) -> None:
    try:
        signal_generator.write('*RST')
        signal_generator.write(
            'MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.pullin_setup_sig_gen))  # Load STATE_4
        signal_generator.write('FREQuency {}'.format(1))  # set a default frequency before programming to avoid errors
        signal_generator.write('SOURce1:FUNCtion PULSe')  # selecting pulse function
        signal_generator.write("SOURce:VOLTage:OFFSET 0")
        signal_generator.write("SOURce:VOLTage:LOW 0")
        signal_generator.write("SOURce:VOLTage:HIGH 2.5")
        signal_generator.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        signal_generator.write('OUTPut 1')  # turn on output
        signal_generator.write('OUTPut:SYNC:MODE NORMal')
        signal_generator.write('SOURce1:FUNCtion:PULSe:WIDTh {}'.format(pulse_width))
        error_log = signal_generator.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            frequency_gen = 1 / (10 * pulse_width)
            print(error, error_log, sep='\n', end='\n')
            signal_generator.write('FREQuency {}'.format(frequency_gen))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')

def configuration_sig_gen_power() -> None:
    signal_generator.write('*RST')
    signal_generator.write('MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.power_test_setup_sig_gen))

def configuration_sig_gen_snp(frequency_gen: float = 150, amplitude: float = 1, pulse_width: float = 0.001333) -> None:
    try:
        signal_generator.write('*RST')
        print(dir_and_var_declaration.snp_meas_setup_sig_gen)

        signal_generator.write(
            'MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.snp_meas_setup_sig_gen))  # Load STATE_4
        signal_generator.write('FREQuency {}'.format(1))  # set a default frequency before programming to avoid errors
        signal_generator.write('SOURce1:FUNCtion PULSe')  # selecting pulse function
        signal_generator.write("SOURce:VOLTage:OFFSET 0")
        signal_generator.write("SOURce:VOLTage:LOW 0")
        signal_generator.write("SOURce:VOLTage:HIGH 2.5")
        signal_generator.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        signal_generator.write('OUTPut 1')  # turn on output
        signal_generator.write('OUTPut:SYNC:MODE NORMal')
        signal_generator.write('SOURce1:FUNCtion:PULSe:WIDTh {}'.format(pulse_width))
        error_log = signal_generator.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        if int(error) != 0:
            frequency_gen = 1 / (10 * pulse_width)
            print(error, error_log, sep='\n', end='\n')
            signal_generator.write('FREQuency {}'.format(frequency_gen))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')

def configuration_sig_gen_pull_in(ramp_length: float = 50, amplitude: float = 1) -> float:  # 50µs ramp_length
    ramp_frequency = 1 / (4 * ramp_length * 10 ** (-6))
    ramp_period = (4 * ramp_length * 10 ** (-6))
    try:
        signal_generator.write("*RST")
        signal_generator.write(
            'MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.pullin_setup_sig_gen))  # Load STATE_4
        # signal_generator.write('FREQuency {}'.format(1))
        # signal_generator.write('SOURce1:FUNCtion RAMP')  # selecting pulse function
        # signal_generator.write('FUNCtion:RAMP:SYMMetry 50')
        # signal_generator.write("SOURce:VOLTage:OFFSET 0")
        # signal_generator.write("SOURce:VOLTage:LOW -{}".format(amplitude))
        # signal_generator.write("SOURce:VOLTage:HIGH {}".format(amplitude))
        # signal_generator.write('SOURce:BURSt:NCYCles MINimum')  # set burst cycles to 0
        # signal_generator.write('OUTPut 1')  # turn on output
        # signal_generator.write('OUTPut:SYNC:MODE NORMal')
        # signal_generator.write('FREQuency {}'.format(ramp_frequency))
        error_log = signal_generator.query('SYSTem:ERRor?')
        error = error_log.split(sep=',')[0]
        print(error, error_log, sep='\n', end='\n')
        osc.write('HORizontal:MODE:SCAle {}'.format(ramp_period / 5))
        if int(error) != 0:
            print(error, error_log, sep='\n', end='\n')
            signal_generator.write('FREQuency {}'.format(ramp_frequency))
        time.sleep(1)
    except:
        print('Signal Generator Configuration error')
    return ramp_period

def configuration_pull_in(ramp_length: float = 50, amplitude: float = 1, rf_frequency: float = 10):
    configuration_sig_gen_pull_in(ramp_length=50, amplitude=1)
    setup_rf_synth(frequency=rf_frequency, power=-10)

def print_error_log():
    error_log_sig_gen = ""
    error_log_sig_zva = ""
    error_string_sig_gen = ""
    error_string_zva = ""

    # Check if 'signal_generator' is defined
    if 'signal_generator' in globals():
        try:
            error_log_sig_gen = signal_generator.query('SYSTem:ERRor?')
            error_string_sig_gen = error_log_sig_gen.split(",")[1]
            print('SIGNAL GENERATOR ERROR LOG:\n' + error_string_sig_gen, end='\n')
        except Exception as e:
            print(f"Failed to query SIGNAL GENERATOR: {str(e)}")

    # Check if 'zva' is defined
    if 'zva' in globals():
        try:
            error_log_sig_zva = zva.query_str('SYSTem:ERRor?')
            error_string_zva = error_log_sig_zva.split(",")[1]
            print('ZVA ERROR LOG:\n' + error_string_zva, end='\n')
        except Exception as e:
            print(f"Failed to query ZVA: {str(e)}")

    # Combine the error logs
    a = 'SIGNAL GENERATOR ERROR LOG:\n' + error_string_sig_gen
    b = 'ZVA ERROR LOG:\n' + error_string_zva
    return a + '\n' + b

def setup_osc_cycling():
    osc.write("*RST")
    osc.write('RECALL:SETUP "{}"'.format(dir_and_var_declaration.cycling_setup_oscilloscope))
    acquisition_length = osc.query("HORizontal:ACQLENGTH?")
    record_length = osc.query("HORizontal:MODE:RECOrdlength?")
    x_unit = osc.query("HORizontal:MAIn:UNIts:STRing?")
    x_scale = osc.query("HORizontal:MODE:SCAle?")
    trigger_ref = int(osc.query('HORizontal:MAIn:DELay:POSition?'))
    ch2_y_scale = osc.query("CH2:SCAle?")  # Scale of channel 2
    ch4_y_scale = osc.query("CH4:SCAle?")  # Scale of channel 4
    setup_info = dict([
        ('x_unit', x_unit), ('x_scale', x_scale), ('ch2_y_scale', ch2_y_scale), ('ch4_y_scale', ch4_y_scale),
        ('acquisition_length', acquisition_length)])
    # ('acquisition_length', acquisition_length), ('trig_ref', trig_ref)])
    return (setup_info)

def force_trigger_osc():
    osc.write('TRIGGER FORCE')

def setup_rf_synth(frequency: float = 10, power: float = -10,
                   power_lim: float = -6):  # GHz, 6 dBm is max linear input for a non distorted pulse
    rf_Generator.write('SOUR:POW:LIM:AMPL -1'.format(power_lim))
    rf_Generator.write('OUTP ON')
    rf_Generator.write('SOUR:POW:IMM:AMPL {}'.format(power))
    rf_Generator.write('SOUR:FREQ {} GHz; LEV {}'.format(frequency, power))
    rf_Generator.write('OUTP ON')

def get_channel_info(channel: int = 4) -> dict:
    channel_info: dict = {}
    try:
        osc.write('Data:Source CH{}'.format(channel))
        osc.write('Data:ENCdg ASCII')
        x_scale = osc.query('HORizontal:MODE:SCAle?')
        x_divisions = osc.query('HORizontal:DIVisions?')
        acquisition_length = osc.query("HORizontal:ACQLENGTH?")

        # print("acquisition_length = {} samples\n".format(acquisition_length))

        sweep_duration = float(x_scale) * float(x_divisions)
        # print("sweep duration = {} s\n".format(sweep_duration))
        y_scale = osc.query_ascii_values('WFMOutpre:Ymult?')
        y_offset = osc.query_ascii_values('WFMOutpre:YOFf?')
        channel_info = dict([('y_offset', y_offset), ('x_scale', x_scale), ('y_scale', y_scale),
                             ('x_divisions', x_divisions), ('sweep_duration', sweep_duration),
                             ('acquisition_length', acquisition_length)])
        # print("get_channel_info function ended")
    except Exception:
        print("Unable to Get channel info")
        traceback.print_exc()
    return channel_info

def set_signal_generator_pulse_parameters(pulse_width: float, pulse_period: float, burst_mode: bool = True):
    """
    Sets the pulse width, pulse period, and burst mode for the signal generator.

    Args:
        pulse_width (float): The desired pulse width in microseconds.
        pulse_period (float): The desired pulse period in microseconds.
        burst_mode (bool): True to enable burst mode, False to disable.
    """
    try:
        signal_generator.write(f"SOURce1:FUNCtion:PULSe:PERiod {pulse_period} S")
        signal_generator.write(f"SOURce1:FUNCtion:PULSe:WIDTh {pulse_width} S")
        if burst_mode:
            signal_generator.write("BURSt:STATe ON")
        else:
            signal_generator.write("BURSt:STATe OFF")
        print(
            f"Signal generator pulse parameters set: Width={pulse_width}us, Period={pulse_period}us, Burst={burst_mode}")
    except Exception as e:
        print(f"Error setting signal generator pulse parameters: {e}")

def setup_rf_synth(frequency: float, power: float):
    """
    Sets up the RF synthesizer with the specified frequency and power.

    Args:
        frequency (float): The desired RF frequency in GHz.
        power (float): The desired RF power in dBm.
    """
    try:
        rf_Generator.write(f"SOURce:FREQuency {frequency}GHZ")
        rf_Generator.write(f"SOURce:POWer:LEVel:IMMediate:AMPLitude {power}DBM")
        rf_Generator.write("OUTPut ON")
        print(f"RF Generator set to Frequency={frequency}GHz, Power={power}dBm")
    except Exception as e:
        print(f"Error setting RF synthesizer: {e}")

def set_rf_power(power: float):
    """
    Sets the RF power.

    Args:
        power (float): The desired RF power in dBm.
    """
    try:
        rf_Generator.write(f"SOURce:POWer:LEVel:IMMediate:AMPLitude {power}DBM")
        print(f"RF Generator set to Power={power}dBm")
    except Exception as e:
        print(f"Error setting RF power: {e}")

def get_powermeter_channels(offset_a1: float = 0, offset_b1: float = 0) -> tuple[float, float, float]:
    """
    Queries the power meter values for channels A1 and B1, applies the given offsets, and returns the results.

    Args:
        offset_a1 (float): The offset to apply to the power value of channel A1. Defaults to 0.0.
        offset_b1 (float): The offset to apply to the power value of channel B1. Defaults to 0.0.

    Returns:
        tuple: A tuple containing the power values for channel A1 and channel B1, respectively, after applying the offsets.
    """
    # Initialize the power meter for continuous measurements
    powermeter.write('INIT:CONT:ALL 1')
    # Query power value for channel A1 and apply offset
    power_value_a1 = round(float(powermeter.query('FETC1?')) + offset_a1, ndigits=3)
    # Query power value for channel B1 and apply offset
    power_value_b1 = round(float(powermeter.query('FETC2?')) + offset_b1, ndigits=3)
    power_value_b2 = round(float(powermeter.query('FETC4?')) + offset_b1, ndigits=3)
    powermeter.write('INIT:CONT:ALL 0')
    # Print the queried power values
    # print(f"Power value for channel A1: {power_value_a1}")
    # print(f"Power value for channel B1: {power_value_b1}")
    return power_value_a1, power_value_b1, power_value_b2

def set_channel_attenuation(atts: dict[str, float]) -> None:
    """
    Sets the attenuation for specified channels on the power meter.

    Args:
        atts (dict[int, float]): A dictionary where keys are sensor numbers (1-2)
                                 and values are the attenuation values to set.
    """
    powermeter.write('SENSe1:CORRection:GAIN2:STATe 1')
    powermeter.write('SENSe2:CORRection:GAIN2:STATe 1')

    for channel, attenuation in atts.items():
        if channel == "A":
            sensor = 1
        elif channel == "B":
            sensor = 2
        command = f'SENSe{sensor}:CORRection:GAIN2:MAGNitude {attenuation}'
        print(command)
        powermeter.write(command)

        print(f"Set attenuation for channel {channel} to {attenuation} dB")

@powermeter_opc_control
def set_time_domain_window(trigger_delay: float, trace_duration: float, gate_duration: float):
    """
    Sets the time domain window for the power meter.

    Args:
        trigger_delay (float): The trigger delay in seconds.
        trace_duration (float): The trace duration in seconds.
        gate_duration (float): The gate duration in seconds.
    """
    powermeter.write(f"TRIG:DEL {trigger_delay}")
    powermeter.write(f"TRAC:TIME {trace_duration}")
    powermeter.write(f"GATE:TIME {gate_duration}")

def send_trig():
    signal_generator.write('TRIG')
    signal_generator.query('*OPC?')
    return print('trigger sent')

def clear_screen(delay=1.0):
    """
    Clears the screen after an optional delay.
    Args:
        delay (float): Time in seconds to wait before clearing the screen.
    """
    time.sleep(delay)  # Pause for the specified delay
    os.system('cls' if os.name == 'nt' else 'clear')

def signal_Generator_cycling_config():
    signal_generator.write("*RST")
    signal_generator.write('OUTput 0')
    time.sleep(1)
    signal_generator.write('MMEM:LOAD:STAT "{}"'.format(dir_and_var_declaration.cycling_setup_sig_gen))
    signal_generator.write('OUTput 0')
    time.sleep(1)
    signal_generator.write("*OPC?")
    print("Signal Generator cycling config")

def osc_cycling_config():
    osc.write(r'RECALL:SETUP "{}"'.format(dir_and_var_declaration.cycling_setup_oscilloscope))
    print("Oscilloscope cycling config")
    osc.write("*OPC?")

def osc_pullin_config():
    osc.write(r'RECALL:SETUP "{}"'.format(dir_and_var_declaration.pullin_setup_oscilloscope))
    print("Oscilloscope pullin config")
    osc.write("*OPC?")

def rf_gen_pull_in_setup():
    rf_Generator.write_str_with_opc("*RST")
    rf_Generator.write_str_with_opc(r"MMEMory:LOAD:STATe 2, '{}'".format(dir_and_var_declaration.pullin_setup_rf_gen))
    rf_Generator.write_str_with_opc('OUTP ON')
    rf_Generator.write_str_with_opc('SOUR:FREQ {} GHz; LEV {}'.format(10, -10))

def rf_gen_time_domain_setup():
    rf_Generator.write_str_with_opc("*RST")
    rf_Generator.write_str_with_opc(
        fr"MMEMory:LOAD:STATe 5, '{dir_and_var_declaration.time_domain_power_test_setup_rf_gen}'")
    rf_Generator.write_str_with_opc("*RCL 5")
    rf_Generator.write_str_with_opc('SOUR:FREQ {} GHz; LEV {}'.format(10, 0))

def rf_gen_cycling_setup(frequency=10, power=-10,
                         power_lim=5):
    rf_Generator.write_str_with_opc("*RST")
    rf_Generator.write_str_with_opc(r"MMEMory:LOAD:STATe 1, '{}'".format(dir_and_var_declaration.cycling_setup_rf_gen))
    rf_Generator.write_str_with_opc('SOUR:POW:LIM:AMPL {}'.format(power_lim))
    rf_Generator.write_str_with_opc('OUTP ON')
    rf_Generator.write_str_with_opc('SOUR:POW:IMM:AMPL {}'.format(power))
    rf_Generator.write_str_with_opc('SOUR:FREQ {} GHz; LEV {}'.format(frequency, power))
    rf_Generator.write_str_with_opc('OUTP ON')

def rf_gen_power_setup(frequency=9.3, power=-25,
                       power_lim=0):
    rf_Generator.write_str_with_opc("*RST")
    rf_Generator.write_str_with_opc(
        r"MMEMory:LOAD:STATe 4, '{}'".format(dir_and_var_declaration.power_test_setup_rf_gen))
    rf_Generator.write_str_with_opc("*RCL 4")
    rf_Generator.write_str_with_opc('SOUR:FREQ {} GHz; LEV {}'.format(frequency, power))
    rf_Generator.write_str_with_opc('SOUR:POW:LIM:AMPL {}'.format(power_lim))

def set_osc_event_count(nth_trigger=10):
    osc.write("TRIGger:B:EVENTS:COUNt {}".format(nth_trigger))
    print("Trigger on {}th trigger".format(nth_trigger))

def rf_gen_power_lim():
    pass

def rf_gen_set_freq(frequency: float = 10) -> None:
    rf_Generator.write_str_with_opc(f'SOUR:FREQ {frequency} GHz')

def move_oscilloscope_cursor(cursor_number: int = 1, cursor_type: str = 'X', position: str = '0.206') -> None:
    """
    Moves a specified cursor to a designated position on a Tektronix oscilloscope.

    Args:
        cursor_number (int): The cursor number (1 or 2) to be moved.
        cursor_type (str): The type of cursor to move ('X' for horizontal, 'Y' for vertical).
        position (float): The position to move the cursor to. This should be within the valid range for the cursor type.

    Raises:
        ValueError: If the cursor number is not 1 or 2, or if the cursor type is neither 'X' nor 'Y'.
        Exception: If there is an error in communication with the oscilloscope.

    Returns:
        None: This function does not return a value but moves the cursor on the oscilloscope.
    """
    # Validate cursor number and type
    if cursor_number not in [1, 2]:
        raise ValueError("Cursor number must be 1 or 2")
    if cursor_type.upper() not in ['X', 'Y']:
        raise ValueError("Cursor type must be 'X' for horizontal or 'Y' for vertical")

    try:
        # Construct and send the SCPI command to move the cursor
        command = f'CURSor:SCREEN:{cursor_type.upper()}POSITION{cursor_number} {position}'
        osc.write(command)
        print(f"Cursor {cursor_number} moved to position {position} on {cursor_type.upper()} axis.")
    except Exception as e:
        print(f"Failed to move cursor due to: {str(e)}")

def on_off_signal_generator_switch() -> int:
    """
    Toggles the on/off status of a signal generator and returns its original status.

    Returns:
        int: The original on/off status of the signal generator before toggling (1 for ON, 0 for OFF).
    """
    # Query the signal generator to get the current ON/OFF status.
    signal_generator_on_off_status = signal_generator.query(r'OUTput1?')

    # Print the current status of the signal generator to the console.
    print(f"Current Signal Generator status: {signal_generator_on_off_status}")

    # Check the first character of the status returned by the query.
    if signal_generator_on_off_status[0] == '1':
        # The generator is currently ON, send a command to turn it OFF.
        signal_generator.write("OUTput1 0")
        print("Turning OFF Signal Generator")
    elif signal_generator_on_off_status[0] == '0':
        # The generator is currently OFF, send a command to turn it ON.
        signal_generator.write("OUTput1 1")
        print("Turning ON Signal Generator")
    else:
        # If the status is neither '1' nor '0', it's unknown and an error is raised.
        raise ValueError("Signal Generator ON/OFF status unknown")

    # Return the numeric version of the original status (1 or 0).
    return int(signal_generator_on_off_status)

def query_signal_generator() -> str:
    """Queries the current status of the signal generator."""
    return signal_generator.query(r'OUTput1?')[0]

def toggle_signal_generator() -> None:
    """Toggles the signal generator's state based on the current status."""
    current_status = query_signal_generator()
    new_status = '0' if current_status[0] == '1' else '1'
    signal_generator.write(f"OUTput1 {new_status}")
    print(f"Signal Generator turned {'ON' if new_status == '1' else 'OFF'}")

def load_pattern(
        filename: str = r'filtered_1000pulses_100us_pulse_dc20%_30Vtop_24Vhold_40V_triangle_filtered.arb') -> None:
    """
    Loads an arbitrary waveform pattern from a USB device into a signal generator.
    """
    signal_generator.write('*RST')  # Reset the signal generator to its default settings.
    signal_generator.write(r'MMEMory:CDIRectory "USB:\PATTERNS\"')  # Set the memory directory to PATTERNS on the USB.
    print(signal_generator.query('SYSTem:ERRor?'))  # Query the system for any errors and print them.
    print("Directory switched")  # Inform the user that the directory has been switched.
    signal_generator.write(
        fr'MMEMory:LOAD:DATA "USB:\PATTERNS\{filename}"')  # Load the waveform data from the specified file.
    signal_generator.write(
        fr'FUNC:ARB "USB:\PATTERNS\{filename}"')  # Set the function to arbitrary waveform using the loaded file.
    signal_generator.write(r'FUNC ARB')  # Confirm that the function mode is set to arbitrary waveform.

    # Enable output on channel 1 and set voltage offset to zero.
    signal_generator.write("OUTPut1 0")  # Turn on output channel 1.
    signal_generator.write("VOLTage:OFFSET 0")  # Set the voltage offset to zero.

def load_pull_in_voltage_waveform(voltages: list[int], width_pulse_us: float, max_samples: int = 10e6) -> np.ndarray:
    """
    Generate a waveform within the maximum sample size constraint.
    """
    # Find the minimum sample rate that keeps the total sample count within max_samples
    total_pulse_sections = len(voltages) * 2  # ascent and continuous descent
    max_pulse_width_samples = max_samples // total_pulse_sections
    sample_rate = max_pulse_width_samples / width_pulse_us / 1e-6  # calculate the sample rate

    # Calculate the actual pulse width in samples based on the adjusted sample rate
    pulse_width_samples = int(width_pulse_us * 1e-6 * sample_rate)

    # Generate the waveform with adjusted pulse width
    waveform = np.concatenate([
                                  np.array([voltage] * pulse_width_samples + [0] * pulse_width_samples) for voltage in
                                  voltages] +
                              [np.array([voltage] * pulse_width_samples) for voltage in reversed(voltages)]
                               )

    return waveform.astype(int)  # , sample_rate

def create_pulse_ascent(amplitude, width, include_zero=True):
    pulse = np.array([amplitude] * width)
    if include_zero:
        pulse = np.concatenate([pulse, np.array([0] * width)])
    return pulse

def create_pulse_descent(amplitude, next_amplitude, width, include_zero=True, taper_length=5):
    pulse = np.array([amplitude] * width)
    if 0 < taper_length < width:
        # Create a linear taper to smoothly decrease the pulse to the next amplitude
        taper = np.linspace(amplitude, next_amplitude, taper_length)
        pulse[-taper_length:] = taper  # Apply the taper at the end of the pulse

    if include_zero:
        zero_gap = np.array([0] * width)
        pulse = np.concatenate([pulse, zero_gap])

    return pulse

def create_descending_waveform(voltages: list[int], width_pulse: int):
    # Ensure 'voltages' is a list; if not, it could cause the type error mentioned.
    if not isinstance(voltages, list):
        raise ValueError("voltages must be a list of numbers")

    pulses = []
    for i in range(len(voltages) - 1):
        # Pass the next voltage in the list as 'next_amplitude'
        pulse = create_pulse_descent(voltages[i], voltages[i + 1], width_pulse, include_zero=False, taper_length=5)
        pulses.append(pulse)

    # Handle the last pulse (no taper needed if it's the final one in the sequence)
    last_pulse = create_pulse_descent(voltages[-1], voltages[-1], width_pulse, include_zero=False, taper_length=0)
    pulses.append(last_pulse)

    return np.concatenate(pulses)

def upload_waveform_to_signal_Generator(arb_name: str, waveform: np.ndarray, amplitude: float = 2) -> None:
    """Upload a waveform to the signal generator as a comma-separated list of DAC values."""
    dac_values = ', '.join(map(str, waveform))
    signal_generator.write(r"*RST")
    signal_generator.write(r"DATA:VOLatile:CLEar")
    signal_generator.write(fr'SOURce1:VOLTage:LIMit:HIGH 3')

    print(f"Operation status: {signal_generator.query('*OPC?')}")
    time.sleep(2)
    signal_generator.write(f'SOURce1:FUNCtion:ARBitrary "EXP_RISE"')
    time.sleep(2)
    print(signal_generator.query(r'SYSTem:ERRor?'))
    try:
        signal_generator.write(f"SOURce1:DATA:ARB:DAC {arb_name}, {dac_values}")
        print(f"Operation status: {signal_generator.query('*OPC?')}")
    except:
        print("LOADING PHASE FAILED")
    print(signal_generator.query(r"DATA:VOLatile:CAT?"))

    print(signal_generator.query(r'SYSTem:ERRor?'))

    signal_generator.write(f"SOURce1:FUNCtion:ARBitrary {arb_name}")
    print(signal_generator.query(r'SYSTem:ERRor?'))

    signal_generator.write(fr'SOURce1:FUNCtion:ARBitrary:SRATe 7272727')
    signal_generator.write(fr'SOURce1:FUNCtion:ARBitrary:FILTer STEP')
    signal_generator.write(r'SOURce1:FUNC ARB')
    signal_generator.write(r'SOURce1:BURSt:STATe 1')
    signal_generator.write("TRIGger1:SOURce BUS")
    signal_generator.write(f"SOURce1:VOLTage {str(amplitude)}")
    signal_generator.write("OUTPut1 1")
    signal_generator.write("VOLTage:OFFSET 0")

def sweep(amplitude: int = 10, voltage_steps: int = 20) -> list[int]:
    output_list = []
    for step in np.arange(start=1, stop=voltage_steps + 1):
        output_list.append(amplitude / voltage_steps * step)
    output_list.append(0)
    print(f"Precision => {amplitude / voltage_steps} V")
    return sorted(output_list)

def dc_voltage(dc_value=0):
    signal_generator.write(f"SOURce:VOLTage:OFFSET {dc_value}")

def voltage_sweep(v1: str = '0', v2: str = '30', delay: float = 1, filname_prefix: str = 'test',
                  dir=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S1P',
                  step: int = 1):
    signal_generator.write('OUTPut 0')
    starting_voltage = float(v1)
    end_voltage = float(v2)
    voltages = np.linspace(start=starting_voltage, stop=end_voltage, num=step)
    os.chdir(dir)
    signal_generator.write('OUTPut 1')
    for voltage in voltages:
        time.sleep(delay)
        dc_voltage(voltage)
        print(f'Acquiring S1P data for {voltage} V')
        saves1p(filename=f'{filname_prefix}_{round(voltage, ndigits=2)}')
        file_get(filename=f'{filname_prefix}_{round(voltage, ndigits=2)}',
                 zva_file_dir=dir_and_var_declaration.ZVA_File_Dir_ZVA67,
                 pc_file_dir=dir, extension='s1p')
        time.sleep(delay)
    dc_voltage(dc_value=0)
    print('sweep finished')

def toggle_trigger():
    trigger_state = zva.query_str_with_opc("TRIGger:SOURce?")
    if trigger_state == 'IMM':
        zva.write_str_with_opc('TRIGger:SOURce EXTernal')
        print("Trigger switched to external")
    else:
        zva.write_str_with_opc('TRIGger:SOURce IMM')
        print("Trigger switched to immediate")
    print(trigger_state)

def query_powermeter(command: str = "*OPC?"):
    print(f'sending --> {command}')
    print(powermeter.query(command))

def setPowermeterTraceDuration(duration: str = "100E-6",
                               channel: str = "1"):
    try:
        while True:
            error_message = powermeter.query("SYSTem:ERRor?")
            print(error_message)
            if error_message.startswith(("+0", "0,")):
                break  # No more errors
            print(f"Cleared old error: {error_message.strip()}")

        powermeter.write("TRACe1:STAT ON")
        powermeter.write("TRACe2:STAT ON")
        powermeter.write("AVER:STAT ON")
        powermeter.write("SENSe1:AVERage:COUNt:AUTO ON")
        powermeter.write("SENSe2:AVERage:COUNt:AUTO ON")
        powermeter.write("TRACe1:DEFine:DURation:REFerence 50")
        powermeter.write("TRACe2:DEFine:DURation:REFerence 50")

        command_string = f"SENSe{channel}:TRACe:TIME {duration}"
        powermeter.write(command_string)
        powermeter.write("INIT:CONT:ALL ON")

        print("Powermeter is configured and armed for continuous external triggers.")

    except Exception as e:
        print(f"An error occurred: {e}")
        if powermeter:
            print(f"Instrument says: {powermeter.query('SYSTem:ERRor?')}")
        raise e

def define_powermeter_settings(trigger_delay: str = "10E-6",
                               trace_duration: str = "200E-6",
                               gate_duration: str = "10E-6",
                               power_unit: str = "DBM"):
    powermeter.write("TRACe1:STAT ON")
    powermeter.write("TRACe2:STAT ON")
    powermeter.write("INIT:CONT:ALL ON")
    powermeter.write('AVER:STAT ON')
    powermeter.write('SENSe1:AVERage:COUNt:AUTO')
    powermeter.write('SENSe2:AVERage:COUNt:AUTO')
    powermeter.write('TRACe1:DEFine:DURation:REFerence 50')
    powermeter.write('TRACe1:DEFine:DURation:REFerence 50')
    powermeter.write("SENSe1:TRACe:AUToscale")
    powermeter.write("SENSe2:TRACe:AUToscale")
    powermeter.write(f"SENSe1:TRACe:TIME {trace_duration}")
    powermeter.write(f"SENSe2:TRACe:TIME {trace_duration}")

    print("Acquiring waveform...")
    powermeter.write("SENS1:DET:FUNC NORM")
    query_powermeter(command="OUTPut:RECorder1:STATe?")
    query_powermeter(command="OUTPut:RECorder2:STATe?")
    powermeter.write("OUTPut:RECorder2:STATe ON")
    powermeter.write(f"SENS2:DET:FUNC NORM")
    powermeter.write(f"SENSe1:SWE1:TIME {gate_duration}")
    powermeter.write(f"SENSe1:SWE2:TIME {gate_duration}")
    powermeter.write(f"SENSe1:SWE3:TIME {gate_duration}")
    powermeter.write(f"SENSe1:SWE4:TIME {gate_duration}")
    powermeter.write(f"SENSe2:SWE1:TIME {gate_duration}")
    powermeter.write(f"SENSe2:SWE2:TIME {gate_duration}")
    powermeter.write(f"SENSe2:SWE3:TIME {gate_duration}")
    powermeter.write(f"SENSe2:SWE4:TIME {gate_duration}")
    powermeter.write(f"SENSe1:SWEep1:OFFSet:TIME {trigger_delay}")
    powermeter.write(f"SENSe1:SWEep2:OFFSet:TIME {trigger_delay}")
    powermeter.write(f"SENSe1:SWEep3:OFFSet:TIME {trigger_delay}")
    powermeter.write(f"SENSe1:SWEep4:OFFSet:TIME {trigger_delay}")
    powermeter.write(f"SENSe2:SWEep1:OFFSet:TIME {trigger_delay}")
    powermeter.write(f"SENSe2:SWEep2:OFFSet:TIME {trigger_delay}")
    powermeter.write(f"SENSe2:SWEep3:OFFSet:TIME {trigger_delay}")
    powermeter.write(f"SENSe2:SWEep4:OFFSet:TIME {trigger_delay}")
    powermeter.write(f"SENSe1:TRACe:UNIT {power_unit}")
    powermeter.write(f"SENSe2:TRACe:UNIT {power_unit}")
    powermeter.write("CALC1:LIM:UPP:DATA 40")
    powermeter.write("CALC2:LIM:UPP:DATA 40")
    powermeter.write("CALC3:LIM:UPP:DATA 40")
    powermeter.write("CALC4:LIM:UPP:DATA 40")
    powermeter.write("CALC1:LIM:LOW:DATA -40")
    powermeter.write("CALC2:LIM:LOW:DATA -40")
    powermeter.write("CALC3:LIM:LOW:DATA -40")
    powermeter.write("CALC4:LIM:LOW:DATA -40")
    powermeter.write("FORMat:READings:DATA REAL")
    powermeter.write("FORMat:READings:BORDer NORM")

def acquire_powermeter_trace() -> typing.Any:
    powermeter.write("TRIG:SOUR EXT")
    powermeter.write("INIT:CONT OFF")
    powermeter.write("TRAC:STAT ON")
    power_values_dBm_1 = powermeter.query_binary_values(message="TRACe1:DATA? HRESolution",
                                                        header_fmt="ieee", is_big_endian=True,
                                                        chunk_size=2000)

@sig_gen_opc_control
def set_bias_voltage_cycling(voltage_input: str = '10') -> float:
    voltage_at_sig_gen = float(voltage_input) / 20
    print(voltage_at_sig_gen)
    signal_generator.write("SOURce:VOLTage:HIGH {}".format(voltage_at_sig_gen))
    signal_generator.write("SOURce:VOLTage:LOW {}".format(-voltage_at_sig_gen))
    probe_voltage = signal_generator.query("SOURce:VOLTage?")
    print("probe_voltage is {}:".format(float(probe_voltage)))
    set_voltage = float(signal_generator.query("SOURce:VOLTage?")) * 20
    print(set_voltage)
    return set_voltage

@sig_gen_opc_control
def upload_arb_binary(data: np.ndarray, arb_name: str = "MY_ARB", sample_rate: float = 1e6) -> None:
    """
    Uploads raw DAC values (integers) directly to the signal generator volatile memory
    using high-speed binary transfer (SCPI DATA:ARB:DAC).
    """
    if signal_generator is None:
        print("Signal generator not connected. Cannot upload arb.")
        return

    def check_errors(step_label):
        err = signal_generator.query("SYSTem:ERRor?").strip()
        if not err.startswith('+0'):
            print(f"ERROR after {step_label}: {err}")
            return False
        return True
    
    # 1. Clear previous volatile arbs to free memory
    signal_generator.write("SOURce1:DATA:VOLATILE:CLEar")
    check_errors("SOURce1:DATA:VOLATILE:CLEar")

    print(signal_generator.query('SOURce1:DATA:VOLATILE:FREE?'), end='\n')  
      
    # 2. Upload the data block
    signal_generator.write("FORM:BORD NORM") 
    check_errors("FORM:BORD NORM")
    
    # Binary upload directly to VOLATILE
    cmd = "SOURce1:DATA:ARB:DAC VOLATILE, "
    print(data.size, end='\n')
    # Use is_big_endian=False to match FORM:BORD SWAP (Little-Endian)
    signal_generator.write_binary_values(message=cmd, values=data, datatype='h', is_big_endian=True, header_fmt='ieee')
    check_errors("SOURce1:DATA:ARB:DAC VOLATILE")
    
    # 3. Select and Activate the 'VOLATILE' waveform
    # First, specify that the arbitrary function should use the VOLATILE buffer
    signal_generator.write('SOURce1:FUNCtion:ARBitrary "VOLATILE"')
    check_errors("Selection of VOLATILE Arb")
    
    # Second, set the main output function to ARB (this 'links' the selection to the output)
    signal_generator.write("SOURce1:FUNCtion ARB")
    check_errors("Setting Function to ARB")
    
    print(signal_generator.query('DATA:VOL:CAT?'), end='\n')  
    
    # 4. Set the sample rate
    signal_generator.write(f"SOURce1:FUNCtion:ARBitrary:SRATe {sample_rate}")
    check_errors("Setting Sample Rate")
    
    # 5. Turn output ON so the waveform actually plays
    signal_generator.write("OUTPut1 ON")

    
    print(f"Upload process for {arb_name} finished. Check console for any logged errors above.")

