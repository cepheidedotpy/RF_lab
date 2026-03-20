from src.core.hardware_control import *
import src.core.hardware_control as hc
from src.core.data_processing import (calculate_actuation_and_release_voltages, calculate_actuation_and_release_voltages_v2, extract_pull_down_voltage_and_iso, detect_sticking_events, extract_data, extract_data_v2, extract_data_v3, create_smooth_pull_in_voltage_waveform, scale_waveform_to_dac, apply_threshold_filter, plot_signal_fft, plot_signal_fft_noise_removal, timing_wrapper, format_duration)
from src.core.file_io import extension_detector, filetypes_dir, saves3p, saves2p, saves1p, file_get, check_if_file_name_exists
import traceback
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import time
from functools import wraps
import RsInstrument
import matplotlib.artist
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import pyvisa
from RsInstrument import RsInstrument, RsInstrException, TimeoutException, StatusException
from matplotlib.ticker import FuncFormatter
from scipy.signal import savgol_filter, get_window, convolve
import typing
from src.core import config as dir_and_var_declaration
from src.core.config import (
    zva_init, sig_gen_init, osc_init, rf_gen_init, powermeter_init,
    zva_init_mock, sig_gen_init_mock, osc_init_mock, rf_gen_init_mock,
    powermeter_init_mock)

# import ttkbootstrap as ttk

matplotlib.ticker.ScalarFormatter(useOffset=True, useMathText=True)

# This code is dated to 15/02/24
"""
Developer : T0188303 - A.N.
"""
os.system('cls')

# Initialize global instrument variables to None




path = r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data'

# global zva, signal_generator, osc, rf_Generator
if os.path.exists(path):
    os.chdir('{}'.format(path))
else:
    print(f"Warning: Directory not found: {path}")


# Opening resource manager
# rm = pyvisa.ResourceManager()
# signal_generator: pyvisa.Resource = sig_gen_init()
# osc: pyvisa.Resource = osc_init()
# zva: RsInstrument = zva_init(zva="ZVA50")
# powermeter: pyvisa.Resource = powermeter_init()
# rf_Generator: RsInstrument = rf_gen_init(rf_gen_type='smb')


# VNA parameter definition
















































































def triggered_data_acquisition(filename: str = r'default',
                               zva_file_dir: str = r"C:\Users\Public\Documents\Rohde-Schwarz\ZNA\Traces",
                               pc_file_dir: str = r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\S2P",
                               file_format: str = 's2p') -> None:
    try:
        sweep_time: str = zva.query_str_with_opc('SENSe1:SWEep:TIME?')
        print("Sweep time is set to {} s\n".format(sweep_time), end='\n')
        trigger_measurement_zva()
        time.sleep(float(sweep_time))
        if file_format == 's3p':
            saves3p(filename)
            file_get(filename, zva_file_dir, pc_file_dir, extension='s3p')
        elif file_format == 's2p':
            saves2p(filename)
            file_get(filename, zva_file_dir, pc_file_dir, extension='s2p')
        elif file_format == 's1p':
            saves1p(filename)
            file_get(filename, zva_file_dir, pc_file_dir, extension='s1p')
        print_error_log()
    except:
        sweep_time = zva.query_str_with_opc('SENSe1:SWEep:TIME?')
        signal_generator.write('SOURce1:FREQuency {}'.format(1 / (10 * float(sweep_time))))
        print('An error occured in triggered_data_acquisition PROCESS \n')
        print('prf may be incompatible \n')
        print_error_log()












def get_curve(channel: int = 4) -> np.ndarray:
    print(f"Acquiring curve {channel}")
    curve_data = np.array([])
    
    # Lazy initialization to fix NoneType namespace issue
    global osc, signal_generator, rf_Generator, powermeter, zva
    if hc.osc is not None and osc is None:
        osc = hc.osc
        signal_generator = hc.signal_generator
        rf_Generator = hc.rf_Generator
        powermeter = hc.powermeter
        zva = hc.zva

    try:
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
        # print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        trigger_ref = float(osc.query(
            'HORizontal:MAIn:DELay:POSition?')) / 100  # get trigger position in percentage of samples (default is 10%)
        ref_index = trigger_ref * acquisition_length  # get the 1st index of the ramp using trigger ref position and
 
        ramp_frequency = float(signal_generator.query('FREQuency?'))  # adapt the length of the ramp with frequency
 
        # Determine the length of the triangle and the number of samples in the triangle
        ramp_length = 1 / (4 * ramp_frequency)
        ramp_period = 1 / (ramp_frequency)
        # print("ramp periode is = {}".format(ramp_period), end='\n')
        # rf_Generator.write("SOURce:PULM:WIDTh {}".format(ramp_period * 2))
        sample_rate = float(osc.query('HORizontal:MODE:SAMPLERate?'))
        number_of_samples = sample_rate * ramp_period  # Number of samples in the triangles
        # print("number of samples in the triangle is {}".format(number_of_samples))
        print("ref_index is {}".format(ref_index))
        # data_truncated is the truncated data. This data  is cropped from ref index to 1500 samples after the end of
        # the triangle
        data_truncated = np.zeros((acquisition_length, 2))[int(ref_index):int(ref_index) + int(
            number_of_samples)]  # 1500 samples added to make sure the triangle is complete
        curve_data = data_truncated
        # data = np.zeros((acquisition_length,2))
        info = get_channel_info(channel=channel)
        osc.write("DATa:STOP {}".format(acquisition_length))
        # curve = np.array(osc.query('CURV?').split(','), dtype=float)
        curve = np.array(osc.query('CURV?').split(','), dtype=float)[
                int(ref_index):int(ref_index) + int(number_of_samples)]
        y_offset = info['y_offset'][0]
        y_scale = info['y_scale'][0]
        time_base = info['sweep_duration'] / acquisition_length
        # print(time_base)
        time = np.arange(0, info['sweep_duration'], time_base)[
               int(ref_index):int(ref_index) + int(number_of_samples)]
        # print("duration of sweep = {} s\n".format(info['sweep_duration']))
        curve_data[:, 0] = (curve - y_offset) * y_scale
        curve_data[:, 1] = time[:]
        # print("get_curve function ended")
    except Exception:
        print("Unable to acquire Data")
        traceback.print_exc()
    return curve_data


def get_curve_fft(channel: int = 4):
    print(f"Acquiring curver {channel}")
    try:
        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
        curve_data = np.empty(shape=acquisition_length)
        # print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        info = get_channel_info(channel=channel)
        osc.write("DATa:STOP {}".format(acquisition_length))
        # curve = np.array(osc.query('CURV?').split(','), dtype=float)
        curve = np.array(osc.query('CURV?').split(','), dtype=float)

        y_offset = info['y_offset'][0]
        y_scale = info['y_scale'][0]
        data_truncated = np.zeros((acquisition_length, 2))
        curve_data = data_truncated
        time_base = info['sweep_duration'] / acquisition_length
        # print(time_base)
        time = np.arange(0, info['sweep_duration'], time_base)
        # print("duration of sweep = {} s\n".format(info['sweep_duration']))
        curve_data[:, 0] = (curve - y_offset) * y_scale
        curve_data[:, 1] = time[:]
        # print(curve[:, 0])
        # print(curve[:, 1])
        # print("get_curve function ended")
    except:
        print("Unable to acquire Data")
    return curve_data


def measure_pull_down_voltage(filename=r'default'):
    curve_det = get_curve(channel=4)
    curve_bias = get_curve(channel=2)
    t = curve_det[:, 1]
    rf_detector = curve_det[:, 0]
    v_bias = curve_bias[:, 0]
    file_array = np.vstack((v_bias, rf_detector, t))
    # print(file_array[:, 0], end='\n')
    np.savetxt('{}.txt'.format(filename), file_array, delimiter=',', newline='\n',
               header='#V_bias(V),rf_detector (V), time (s)')
    # except:
    #     print("Unable to acquire Data")


def measure_pull_down_voltage_pulsed(filename=r'default'):
    curve_det = get_curve_using_cursors(channel=4)
    curve_bias = get_curve_using_cursors(channel=2)
    t = curve_det[:, 1]
    rf_detector = curve_det[:, 0]
    v_bias = curve_bias[:, 0]
    file_array = np.vstack((v_bias, rf_detector, t))
    # print(file_array[:, 0], end='\n')
    np.savetxt('{}.txt'.format(filename), file_array, delimiter=',', newline='\n',
               header='#V_bias(V),rf_detector (V), time (s)')


def power_test_sequence_v2(
        app,
        new_data_event,
        filename: str = 'test',
        start: float = -30.0,
        stop: float = -20.0,
        step: float = 1.0,
        sleep_duration: float = 1.0,
        offset_a1: float = 0.0,
        offset_b1: float = 0.0,
) -> tuple[list[float], list[float]]:
    """
    Conducts a power sweep test and records the average input and output power levels for a DUT (Device Under Test).

    Args:
        app: Reference to the main application instance to update the plot.
        :param new_data_event: Event to signal new data is available.
        :param filename (str): The name of the file to save results. Defaults to 'test'.
        :param start (float): The starting power level in dBm. Defaults to -30.0.
        :param stop (float): The stopping power level in dBm. Defaults to -20.0.
        :param step (float): The step size for the power level sweep in dBm. Defaults to 1.0.
        :param sleep_duration (float): The duration to sleep between steps in seconds. Defaults to 1.0.
        :param offset_a1: (float): Offset to apply to channel A1 measurements. Defaults to 0.0.
        :param offset_b1 (float): Offset to apply to channel B1 measurements. Defaults to 0.0.

    Returns:
        tuple: Two lists containing the average input power levels and the average output power levels.
    """
    # Generate the power levels to sweep
    power_input_amp = list(np.arange(start, stop, step))
    power_input_dut_avg = []
    power_output_dut_avg = []

    # Set the power limit on the RF generator
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LIMit:AMPLitude {stop + 2}')
    signal_generator.write('OUTP ON')

    # Initialize the RF generator output and set the starting power level
    rf_Generator.write_str_with_opc('OUTP OFF')
    time.sleep(0.5)
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LEVel:IMMediate:AMPLitude {start}')
    time.sleep(0.5)
    rf_Generator.write('OUTPut 1')

    # Configure the power meter for external triggering and continuous measurement
    powermeter.write('TRIG1:SOUR EXT')
    powermeter.write('TRIG2:SOUR EXT')
    powermeter.write('INIT:CONT:ALL 1')
    powermeter.write('AVER:STAT OFF')

    app.is_power_sweeping = True
    for power_level in power_input_amp:
        if not app.is_power_sweeping:
            break
        rf_Generator.write(f'SOUR:POW:LEVEL:IMM:AMPL {power_level}')
        signal_generator.write('TRIG')
        time.sleep(sleep_duration)
        # power_input_dut_avg.append(round(float(powermeter.query('FETC2?')) + offset_b1, ndigits=2))
        power_input_dut_avg.append(round(float(powermeter.query('FETC2?')), ndigits=2))
        # power_output_dut_avg.append(round(float(powermeter.query('FETC1?')) + offset_a1, ndigits=2))
        power_output_dut_avg.append(round(float(powermeter.query('FETC1?')), ndigits=2))
        app.new_data_event_power_sweep.set()
        # Update the dataframe with the new measurements
        app.file_power_sweep = pd.DataFrame({
            'Power Input DUT Avg (dBm)': power_input_dut_avg[1:],
            'Power Output DUT Avg (dBm)': power_output_dut_avg[1:]
        })
        # new_data_event.set()  # Signal that new data is available

    # Turn off the signal generator and RF generator outputs
    signal_generator.write('OUTP OFF')
    rf_Generator.write('OUTP OFF')
    print("Sweep ended")
    # Save the DataFrame to a CSV file
    app.file_power_sweep.to_csv(f'{filename}.csv', index=False)
    app.is_power_sweeping = False
    return power_input_dut_avg, power_output_dut_avg


def power_test_sequence(
        filename: str = 'test',
        start: float = -30.0,
        stop: float = -20.0,
        step: float = 1.0,
        sleep_duration: float = 1.0,
        offset_a1: float = 0.0,
        offset_b1: float = 0.0,
) -> tuple[list[float], list[float]]:
    """
    Conducts a power sweep test and records the average input and output power levels for a DUT (Device Under Test).

    Args:
        filename (str): The name of the file to save results. Defaults to 'test'.
        start (float): The starting power level in dBm. Defaults to -30.0.
        stop (float): The stopping power level in dBm. Defaults to -20.0.
        step (float): The step size for the power level sweep in dBm. Defaults to 1.0.
        sleep_duration (float): The duration to sleep between steps in seconds. Defaults to 1.0.
        offset_a1 (float): Offset to apply to channel A1 measurements. Defaults to 0.0.
        offset_b1 (float): Offset to apply to channel B1 measurements. Defaults to 0.0.

    Returns:
        tuple: Two lists containing the average input power levels and the average output power levels.
    """
    # Generate the power levels to sweep
    power_input_amp = list(np.arange(start, stop, step))
    power_input_dut_avg = []
    power_output_dut_avg = []

    # Set the power limit on the RF generator
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LIMit:AMPLitude {stop + 2}')
    signal_generator.write('OUTP ON')

    # Initialize the RF generator output and set the starting power level
    rf_Generator.write_str_with_opc('OUTP OFF')
    time.sleep(0.5)
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LEVel:IMMediate:AMPLitude {start}')
    time.sleep(0.5)
    # Configure the power meter for external triggering and continuous measurement
    powermeter.write('TRIG1:SOUR EXT')
    powermeter.write('TRIG2:SOUR EXT')
    powermeter.write('INIT:CONT:ALL 1')
    powermeter.write('AVER:STAT OFF')
    rf_Generator.write('OUTPut 1')
    # Sweep through the power levels and record measurements
    for power_level in power_input_amp:
        rf_Generator.write(f'SOUR:POW:LEVEL:IMM:AMPL {power_level}')
        signal_generator.write('TRIG')
        time.sleep(sleep_duration)
        power_input_dut_avg.append(round(float(powermeter.query('FETC2?')) + offset_b1, ndigits=2))
        power_output_dut_avg.append(round(float(powermeter.query('FETC1?')) + offset_a1, ndigits=2))

    # Turn off the signal generator and RF generator outputs
    power_input_dut_avg.pop(0)
    power_output_dut_avg.pop(0)
    signal_generator.write('OUTP OFF')
    rf_Generator.write('OUTP OFF')
    print("Sweep ended")

    # Save results to file
    file_array = np.vstack((power_input_dut_avg, power_output_dut_avg))
    # os.chdir(path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data")
    np.savetxt(f'{filename}.txt', file_array, delimiter=',', newline='\n',
               header='#P_in_DUT(dBm), P_out_DUT(dBm)')

    return power_input_dut_avg, power_output_dut_avg


def power_test_smf(
        filename: str = 'test',
        start: float = -30.0,
        stop: float = -20.0,
        step: float = 1.0,
        sleep_duration: float = 1.0,
        offset_a1: float = 0.0,
        offset_b1: float = 0.0,
) -> tuple[list[float], list[float]]:
    """
    Conducts a power sweep test and records the average input and output power levels for a DUT (Device Under Test).

    Args:
        filename (str): The name of the file to save results. Defaults to 'test'.
        start (float): The starting power level in dBm. Defaults to -30.0.
        stop (float): The stopping power level in dBm. Defaults to -20.0.
        step (float): The step size for the power level sweep in dBm. Defaults to 1.0.
        sleep_duration (float): The duration to sleep between steps in seconds. Defaults to 1.0.
        offset_a1 (float): Offset to apply to channel A1 measurements. Defaults to 0.0.
        offset_b1 (float): Offset to apply to channel B1 measurements. Defaults to 0.0.

    Returns:
        tuple: Two lists containing the average input power levels and the average output power levels.
    """
    # Generate the power levels to sweep
    power_input_amp = list(np.arange(start, stop, step))
    power_input_dut_avg = []
    power_output_dut_avg = []

    # Set the power limit on the RF generator
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LIMit:AMPLitude {stop + 2}')

    signal_generator.write('OUTP ON')

    # Initialize the RF generator output and set the starting power level
    rf_Generator.write_str_with_opc('OUTP OFF')
    time.sleep(0.5)
    rf_Generator.write_str_with_opc(f'SOURce:POWer:LEVel:IMMediate:AMPLitude {start}')
    time.sleep(0.5)
    # Configure the power meter for external triggering and continuous measurement
    powermeter.write('TRIG1:SOUR EXT')
    powermeter.write('TRIG2:SOUR EXT')
    powermeter.write('INIT:CONT:ALL 1')
    powermeter.write('AVER:STAT OFF')
    rf_Generator.write('OUTPut 1')
    # Sweep through the power levels and record measurements
    for power_level in power_input_amp:
        rf_Generator.write(f'SOUR:POW:LEVEL:IMM:AMPL {power_level}')
        signal_generator.write('TRIG')
        time.sleep(sleep_duration)
        power_input_dut_avg.append(round(float(powermeter.query('FETC2?')) + offset_b1, ndigits=2))
        power_output_dut_avg.append(round(float(powermeter.query('FETC1?')) + offset_a1, ndigits=2))

    # Turn off the signal generator and RF generator outputs
    power_input_dut_avg.pop(0)
    power_output_dut_avg.pop(0)
    signal_generator.write('OUTP OFF')
    rf_Generator.write('OUTP OFF')
    print("Sweep ended")

    # Save results to file
    file_array = np.vstack((power_input_dut_avg, power_output_dut_avg))
    # os.chdir(path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data")
    np.savetxt(f'{filename}.txt', file_array, delimiter=',', newline='\n',
               header='#P_in_DUT(dBm), P_out_DUT(dBm)')

    return power_input_dut_avg, power_output_dut_avg


def setup_power_test_sequence(pulse_width=100, delay=30):  # in us
    # Configuration signal_generator
    signal_generator.write('*RST')
    signal_generator.write(
        "MMEM:LOAD:STATe '{}'".format(dir_and_var_declaration.power_test_setup_sig_gen))  # 100_us_PULSE.sta
    # Configuration rf_Generator
    rf_Generator.write('*RST')
    rf_Generator.write(
        "MMEMory:LOAD:STATe 4, '{}'".format(dir_and_var_declaration.power_test_setup_rf_gen))  # 100_us_PULSE.sta
    rf_Generator.write("*RCL 4")  # 100_us_PULSE.sta
    # Configuration powermeter
    powermeter.write('*RST')
    powermeter.write(f'{dir_and_var_declaration.power_test_setup_powermeter}')
    # rf_Generator.write("SOURCe1:PULM:WIDTh {}".format(float(pulse_width) * 10 ** (-6)))
    # rf_Generator.write("SOURCe1:PULM:DELay {}".format(float(delay) * 10 ** (-6)))

    # delay_pulse_rf_gen = float(rf_Generator.query("SOURCe1:PULM:DELay?"))
    # width_pulse_rf_gen = float(rf_Generator.query("SOURCe1:PULM:WIDTh?"))

    # print(delay_pulse_rf_gen)
    # print(width_pulse_rf_gen)










# @powermeter_opc_control




def connect():
    machines = ['ZNA67-101810', 'A-33521B-00526', 'DPO5054-C011738', 'rssmb100a179766', '192.168.0.30']
    machine_names = ['zva', 'signal_generator', 'osc', 'rf_Generator', 'powermeter']
    # machine_dict = {zip(machine_names, machines)} for machine, machine_name in zip(machines, machine_names): try:
    # if machine_name == 'zva': machine_dict[machine_name]=RsInstrument(f'TCPIP0::{machine}::inst0::INSTR',
    # id_query=True, reset=False) else: machine_dict[machine_name]=rm.open_resource(f'TCPIP0::{
    # machine}::inst0::INSTR') except pyvisa.errors.VisaIOError: print(f"Machine {machine_name} ({machine}) is
    # offline. Skipping...")

    zva = RsInstrument('TCPIP0::ZNA67-101810::inst0::INSTR', id_query=False, reset=False)
    sig_gen = rm.open_resource('TCPIP0::A-33521B-00526::inst0::INSTR')
    osc = rm.open_resource('TCPIP0::DPO5054-C011738::inst0::INSTR')
    rf_gen = RsInstrument('TCPIP0::rssmb100a179766::inst0::INSTR')
    powermeter = rm.open_resource('TCPIP0::A-N1912A-00589::inst0::INSTR')
    return zva, sig_gen, osc, rf_gen, powermeter




def get_curve_cycling(channel: int = 4) -> np.array(float):
    """
    Acquire waveform data of set channel,
    functions returns an array  with the time base and values at the specified channel
    :param channel: Oscilloscope channel
    :return: Data array shape (N, 2) with N the number of samples in the channel

    """
    data = np.zeros(1)
    # try:
    osc.write('Data:Source CH{}'.format(channel))
    acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
    # print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
    trigger_ref = float(osc.query(
        'HORizontal:MAIn:DELay:POSition?')) / 100  # get trigger position in percentage of samples (default is 10%)
    sample_rate = float(osc.query('HORizontal:MODE:SAMPLERate?'))
    info = get_channel_info(channel=channel)
    osc.write("DATa:STOP {}".format(acquisition_length))
    curve = np.array(osc.query('CURV?').split(','), dtype=float)
    y_offset = info['y_offset'][0]
    y_scale = info['y_scale'][0]
    time_base = info['sweep_duration'] / acquisition_length
    # print(time_base)
    time = np.arange(0, info['sweep_duration'], time_base)

    data = np.zeros((acquisition_length, 2))
    data[:, 0] = (curve - y_offset) * y_scale
    data[:, 1] = time
    # print("get_curve function ended")
    # except:
    #     print("Unable to acquire Data : Error in get_curve_cycling function")
    return data


def switching_time():
    sw_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
    return sw_time










@timing_wrapper
def cycling_sequence(app, new_data_event, number_of_cycles: float = 1e9, number_of_pulses_in_wf: float = 1000,
                     filename: str = "test",
                     wf_duration: float = 0.205, events: float = 100, header: str = "",
                     df_path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Mechanical cycling",
                     conversion_coeff: float = 0.046):
    """
    Cycling test sequence outputs MEMS characteristics during the tested duration.

    :param conversion_coeff: Conversion coefficient from DC to RF
    :param app: Reference to the Tkinter application instance to update the plot.
    :param new_data_event: Event to signal new data is available.
    :param df_path: File path.
    :param number_of_cycles: Total number of cycles in sequence duration.
    :param number_of_pulses_in_wf: Number of pulses in waveform.
    :param filename: Test sequence output filename.
    :param wf_duration: Total duration of the waveform in the sequence.
    :param events: Number of trigger events before oscilloscope performs an acquisition.
    :param header: Header string to be written at the top of the CSV file.
    :return: File containing a dataframe.
    """
    number_of_triggers_before_acq = events  # Number of B trigger events in A -> B sequence
    number_of_triggered_acquisitions = int(number_of_cycles / (number_of_pulses_in_wf * number_of_triggers_before_acq))
    # cycles = pd.Series(
    #     np.arange(start=0, stop=number_of_cycles, step=number_of_pulses_in_wf * number_of_triggers_before_acq),
    #     name="cycles")

    test_duration = wf_duration * number_of_cycles / number_of_pulses_in_wf
    starting_number_of_acq = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))

    print(f"Number of triggers required: {number_of_triggered_acquisitions}")
    print(f"Starting number of triggers: {starting_number_of_acq}")
    print(f"Number of remaining cycles: {number_of_cycles}")
    print(f"Estimated test duration: {format_duration(test_duration)}")

    count = starting_number_of_acq
    signal_generator.write("OUTput 1")
    remaining_count = number_of_cycles
    app.is_cycling = True
    while count < number_of_triggered_acquisitions + starting_number_of_acq:
        # Write header and DataFrame to CSV
        with open(f"{df_path}\\{filename}.csv", 'w') as f:
            f.write(header + '\n')
            app.file_df.to_csv(f, index=False, header=True, sep=",")

        try:
            new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
            remaining_count: float = number_of_cycles - (
                    new_value - starting_number_of_acq) * number_of_pulses_in_wf * events
            if count == new_value:
                # print("Waiting for trigger...", end='\n')
                # time.sleep(1)
                new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))

            else:
                count = new_value
                ch_4_detector = get_curve_cycling(channel=4)
                ch_2_bias = get_curve_cycling(channel=2)
                data = extract_data_v3(rf_detector_channel=ch_4_detector, v_bias_channel=ch_2_bias,
                                       conversion_coeff=conversion_coeff)
                data["cycles"] = (count - starting_number_of_acq) * number_of_pulses_in_wf * events
                app.file_df = pd.concat([app.file_df, data], ignore_index=True)
                new_data_event.set()  # Signal that new data is available
                clear_screen(0.1)
        except KeyboardInterrupt:
            break
    # Define thresholds for detecting sticking events
    thresholds = {
        "amplitude_variation": 0.5,  # Example threshold, adjust as needed
        "switching_time": 50e-6,  # Example threshold, adjust as needed
        "release_time": 50e-6  # Example threshold, adjust as needed
    }
    app.file_df = detect_sticking_events(app.file_df, thresholds)
    signal_generator.write("OUTput 0")

    # Write header and DataFrame to CSV
    with open(f"{df_path}\\{filename}.csv", 'w') as f:
        f.write(header + '\n')
        app.file_df.to_csv(f, index=False, header=True, sep=",")

    app.is_cycling = False
    new_data_event.set()  # Signal that final data is available
    print("Test complete!")
    return app.file_df


def cycling_sequence_no_processing(app, new_data_event, number_of_cycles: float = 1e9,
                                   number_of_pulses_in_wf: float = 1000,
                                   filename: str = "test",
                                   wf_duration: float = 0.205, events: float = 100, header: str = "",
                                   df_path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Mechanical cycling",
                                   conversion_coeff: float = 0.046):
    """
       Cycling test sequence outputs MEMS characteristics during the tested duration.

       :param conversion_coeff: Conversion coefficient from DC to RF
       :param app: Reference to the Tkinter application instance to update the plot.
       :param new_data_event: Event to signal new data is available.
       :param df_path: File path.
       :param number_of_cycles: Total number of cycles in sequence duration.
       :param number_of_pulses_in_wf: Number of pulses in waveform.
       :param filename: Test sequence output filename.
       :param wf_duration: Total duration of the waveform in the sequence.
       :param events: Number of trigger events before oscilloscope performs an acquisition.
       :param header: Header string to be written at the top of the CSV file.
       :return: File containing a dataframe.
       """
    number_of_triggers_before_acq = events  # Number of B trigger events in A -> B sequence
    number_of_triggered_acquisitions = int(number_of_cycles / (number_of_pulses_in_wf * number_of_triggers_before_acq))
    cycles = pd.Series(
        np.arange(start=0, stop=number_of_cycles, step=number_of_pulses_in_wf * number_of_triggers_before_acq),
        name="cycles")

    test_duration = wf_duration * number_of_cycles / number_of_pulses_in_wf
    starting_number_of_acq = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))

    print(f"Number of triggers required: {number_of_triggered_acquisitions}")
    print(f"Starting number of triggers: {starting_number_of_acq}")
    print(f"Number of remaining cycles: {number_of_cycles}")
    print(f"Estimated test duration: {format_duration(test_duration)}")

    count = starting_number_of_acq
    signal_generator.write("OUTput 1")
    # remaining_count = number_of_cycles
    app.is_cycling = True
    while count < number_of_triggered_acquisitions + starting_number_of_acq:
        # Write header and DataFrame to CSV
        with open(f"{df_path}\\{filename}.csv", 'w') as f:
            f.write(header + '\n')
            app.file_df.to_csv(f, index=False, header=True, sep=",")

        try:
            new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
            remaining_count: float = number_of_cycles - (
                    new_value - starting_number_of_acq) * number_of_pulses_in_wf * events
            if count == new_value:
                # print("Waiting for trigger...", end='\n')
                new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
                # os.system('cls')
            else:
                count = new_value
                ch_4_detector = get_curve_cycling(channel=4)
                ch_2_bias = get_curve_cycling(channel=2)
                data = extract_data_v3(rf_detector_channel=ch_4_detector, v_bias_channel=ch_2_bias)
                data["cycles"] = (count - starting_number_of_acq) * number_of_pulses_in_wf * events
                app.file_df = pd.concat([app.file_df, data], ignore_index=True)
                new_data_event.set()  # Signal that new data is available
                # os.system('cls')
        except KeyboardInterrupt:
            break
    # Define thresholds for detecting sticking events
    thresholds = {
        "amplitude_variation": -2,  # Example threshold, adjust as needed
        "switching_time": 50e-6,  # Example threshold, adjust as needed
        "release_time": 50e-6  # Example threshold, adjust as needed
    }
    app.file_df = detect_sticking_events(app.file_df, thresholds)
    signal_generator.write("OUTput 0")

    # Write header and DataFrame to CSV
    with open(f"{df_path}\\{filename}.csv", 'w') as f:
        f.write(header + '\n')
        app.file_df.to_csv(f, index=False, header=True, sep=",")

    app.is_cycling = False
    new_data_event.set()  # Signal that final data is available
    print("Test complete!")
    return app.file_df


def cycling_sequence_with_escape_interrupt(app, new_data_event,
                                           number_of_cycles: float = 1e9,
                                           number_of_pulses_in_wf: float = 1000,
                                           filename: str = "test",
                                           wf_duration: float = 0.205,
                                           events: float = 100,
                                           header: str = "",
                                           df_path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Mechanical cycling"):
    """
    Cycling test sequence outputs MEMS characteristics during the tested duration.

    This version allows an Escape key press to interrupt the sequence gracefully.

    :param app: Reference to the Tkinter application instance to update the plot (and check for stop).
    :param new_data_event: Event to signal new data is available.
    :param df_path: File path.
    :param number_of_cycles: Total number of cycles in sequence duration.
    :param number_of_pulses_in_wf: Number of pulses in waveform.
    :param filename: Test sequence output filename.
    :param wf_duration: Total duration of the waveform in the sequence.
    :param events: Number of trigger events before oscilloscope performs an acquisition.
    :param header: Header string to be written at the top of the CSV file.
    :return: Pandas DataFrame (final data).
    """
    number_of_triggers_before_acq = events
    number_of_triggered_acquisitions = int(
        number_of_cycles / (number_of_pulses_in_wf * number_of_triggers_before_acq)
    )

    test_duration = wf_duration * number_of_cycles / number_of_pulses_in_wf
    starting_number_of_acq = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))

    print(f"Number of triggers required: {number_of_triggered_acquisitions}")
    print(f"Starting number of triggers: {starting_number_of_acq}")
    print(f"Number of remaining cycles: {number_of_cycles}")
    print(f"Estimated test duration: {format_duration(test_duration)}")

    count = starting_number_of_acq
    signal_generator.write("OUTput 1")
    remaining_count = number_of_cycles
    app.is_cycling = True

    # -- Main measurement loop --

    while count < number_of_triggered_acquisitions + starting_number_of_acq:
        # Check if the user requested to stop (Escape key pressed).
        if app.stop_requested:
            print("ESC key pressed: stopping the cycling sequence early.")
            break

        # Write the partial data to CSV
        with open(f"{df_path}\\{filename}.csv", 'w') as f:
            f.write(header + '\n')
            app.file_df.to_csv(f, index=False, header=True, sep=",")

        try:
            new_value = float(osc.query('ACQuire:NUMACq?').removesuffix('\n'))
            remaining_count = number_of_cycles - (
                    new_value - starting_number_of_acq
            ) * number_of_pulses_in_wf * events

            if count == new_value:
                # The acquisition hasn't advanced; just re-query after a short wait.
                # You may want to use time.sleep or some other logic here.
                pass
            else:
                # Acquisition advanced, gather new data
                count = new_value
                ch_4_detector = get_curve_cycling(channel=4)
                ch_2_bias = get_curve_cycling(channel=2)

                data = extract_data_v3(
                    rf_detector_channel=ch_4_detector,
                    v_bias_channel=ch_2_bias
                )
                data["cycles"] = (
                        (count - starting_number_of_acq)
                        * number_of_pulses_in_wf
                        * events
                )

                app.file_df = pd.concat([app.file_df, data], ignore_index=True)
                new_data_event.set()  # Signal that new data is available
                # clear_screen(0.1)
            time.sleep(0.01)  # Added to allow stop event to be processed

        except KeyboardInterrupt:
            # If the user presses Ctrl+C in the console, we also stop gracefully.
            print("KeyboardInterrupt detected: stopping cycling sequence.")
            break

    # -- After exiting the loop (either completed or interrupted) --
    # Detect “sticking events” or other final processing
    thresholds = {
        "insertion_loss": 0.5,  # Example threshold, adjust as needed
        "t_on_time": 50e-6,  # Example threshold, adjust as needed
        "t_off_time": 50e-6  # Example threshold, adjust as needed
    }
    app.file_df = detect_sticking_events(app.file_df, thresholds)

    # Disable signal generator output
    signal_generator.write("OUTput 0")

    # Final save of the data to CSV
    with open(f"{df_path}\\{filename}.csv", 'w') as f:
        f.write(header + '\n')
        app.file_df.to_csv(f, index=False, header=True, sep=",")

    app.is_cycling = False
    app.stop_requested = False
    new_data_event.set()  # Signal that final data is available

    print("Test complete (either finished or interrupted)!")
    return app.file_df


def save_waveform(waveform_ch4: np.array(np.array(float)),
                  waveform_ch2: np.array(float),
                  filename: str) -> np.array(float):
    data = np.zeros(shape=2)
    info = get_channel_info(channel=4)
    data = np.vstack((waveform_ch4[:, 0], waveform_ch2[:, 0], waveform_ch4[:, 1]))
    np.savetxt('{}.txt'.format(filename), data, delimiter=',', newline='\n',
               header='#waveform_ch4, waveform_ch2, time (s)')
    return data


def save_waveform_v2(waveform_ch4: np.ndarray, waveform_ch2: np.ndarray, filename: str) -> np.ndarray:
    """
    Saves waveform data to a text file and returns the combined data.

    Args:
        waveform_ch4 (np.ndarray): 2D NumPy array containing channel 4 data (e.g., time and amplitude).
        waveform_ch2 (np.ndarray): 2D NumPy array containing channel 2 data (e.g., time and amplitude).
        filename (str): The base name of the output file (without extension).

    Returns:
        np.ndarray: Combined data array containing selected columns from the input arrays.
                    Shape: (3, n), where n is the number of rows in the input arrays.

    Raises:
        ValueError: If the input arrays do not have the expected shapes.
    """
    # Check if the input arrays are valid
    if waveform_ch4.shape[1] < 2 or waveform_ch2.shape[1] < 1:
        raise ValueError("Input arrays must have at least 2 columns for waveform_ch4 and 1 column for waveform_ch2.")

    # Combine the data into a single array
    data = np.vstack((waveform_ch4[:, 0], waveform_ch2[:, 0], waveform_ch4[:, 1]))

    # Save the combined data to a text file
    np.savetxt(
        f'{filename}.txt',  # File name
        data,  # Data to save
        delimiter=',',  # Column delimiter
        newline='\n',  # Row delimiter
        header='# waveform_ch4, waveform_ch2, time (s)'  # Header for the file
    )

    return data


def online_mode():
    try:
        # Main-------------------------------------------------------------------------------------------------------------------------
        RsInstrument.assert_minimum_version('1.5.0')

        os.chdir(r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data")

        print("Connected instrument list: \n")
        # for ressouce in list(ressources.values()):
        #     print(ressouce, end='\n')

        zva = RsInstrument('TCPIP0::ZNA67-101810::inst0::INSTR', id_query=False, reset=False)
        sig_gen = rm.open_resource('TCPIP0::A-33521B-00526::inst0::INSTR')
        osc = rm.open_resource('TCPIP0::DPO5054-C011738::inst0::INSTR')
        rf_gen = RsInstrument('TCPIP0::rssmb100a179766::inst0::INSTR')
        powermeter = rm.open_resource('TCPIP0::192.168.0.83::inst0::INSTR')

        idn = zva.query_str('*IDN?')
        idn2 = sig_gen.query('*IDN?')
        idn3 = osc.query('*IDN?')
        idn4 = rf_gen.query('*IDN?')

        print(idn, end='\n')
        print(idn2, end='\n')
        print(idn3, end='\n')
        print(idn4, end='\n')
    except:
        print("Connection error")


def load_config(pc_file: str,
                inst_file: str):
    """
    Loads a configuration file from the PC to the instrument and activates it.

    Parameters:
    pc_file (str): The file path of the configuration file on the PC. Default is a specified file path.
    inst_file (str): The file path on the instrument where the configuration will be loaded. Default is a specified file path.
    """
    # Reset the ZVA instrument to its default state.
    model = zva.idn_string
    print(f"Active VNA Model: {model}")
    zva.reset()
    if model == r"Rohde&Schwarz,ZVA50-4Port,1145111052100151,3.60":
        # Transfer the configuration file from the PC to the instrument.
        zva.send_file_from_pc_to_instrument(pc_file, inst_file)
        print("_______", end='\n')
        print(pc_file, end='\n')
        print("_______", end='\n')
        # Load the transferred setup on the instrument.
        zva.write_str_with_opc(f'MMEM:LOAD:STAT 1, "{inst_file}"')
        # zva.write_str_with_opc(f'MMEMory:CDIRectory "{inst_file}"')

        # Print a confirmation message indicating the configuration file has been loaded.
        print(f"{pc_file} configuration loaded to:\n{inst_file}", end='\n')
    elif model == r"Rohde-Schwarz,ZNA67-4Port,1332450064101810,2.73":
        # Transfer the configuration file from the PC to the instrument.
        zva.send_file_from_pc_to_instrument(pc_file, inst_file)

        # Load the transferred setup on the instrument.
        zva.write_str_with_opc(f'MMEM:LOAD:STAT 1,"{inst_file}"')

        # Print a confirmation message indicating the configuration file has been loaded.
        print(f"{pc_file} configuration loaded to:\n{inst_file}", end='\n')
    else:
        print(f"Instrument model not recognized, can't load config", end='\n')






























































def get_curve_using_cursors(channel: int = 4):
    try:
        cursor_1_postion = float(osc.query("CURSor:VBArs:POSITION1?"))
        print(cursor_1_postion)
        cursor_2_postion = float(osc.query("CURSor:VBArs:POSITION2?"))
        print(cursor_2_postion)

        acquisition_length = int(osc.query("HORizontal:ACQLENGTH?"))  # get number of samples
        # print("acquisition_length in get curve function = {} samples\n".format(acquisition_length))
        trigger_ref = float(osc.query(
            'HORizontal:MAIn:DELay:POSition?')) / 100  # get trigger position in percentage of samples (default is 10%)
        ref_index = trigger_ref * acquisition_length  # get the 1st index of the ramp using trigger ref position and

        sample_rate = float(osc.query('HORizontal:MODE:SAMPLERate?'))
        number_of_samples = sample_rate * (cursor_2_postion - cursor_1_postion)

        data_truncated = np.zeros((acquisition_length, 2))[int(ref_index):int(ref_index) + int(
            number_of_samples)]  # 1500 samples added to make sure the triangle is complete
        curve_data = data_truncated
        # data = np.zeros((acquisition_length,2))
        info = get_channel_info(channel=channel)
        osc.write("DATa:STOP {}".format(acquisition_length))

        curve = np.array(osc.query('CURV?').split(','), dtype=float)[
                int(ref_index):int(ref_index) + int(number_of_samples)]

        y_offset = info['y_offset'][0]
        y_scale = info['y_scale'][0]
        time_base = info['sweep_duration'] / acquisition_length
        # print(time_base)
        time = np.arange(0, info['sweep_duration'], time_base)[
               int(ref_index):int(ref_index) + int(number_of_samples)]
        # print("duration of sweep = {} s\n".format(info['sweep_duration']))
        curve_data[:, 0] = (curve - y_offset) * y_scale
        curve_data[:, 1] = time[:]
        # print("get_curve function ended")

    except:
        print("Unable to acquire Data")
    return curve_data

    # v_bias = get_curve(channel=2)
    # v_detector = get_curve(channel=4)
    # print(v_bias[:, 1])
    # print(v_detector[:, 1])
    # duration = get_channel_info(channel=4)['sweep_duration']
    # print(duration)
    # index_1_cut_v_bias = np.where(cursor_1_postion > v_bias[:, 1])[0]
    # index_2_cut_v_bias = np.where(cursor_2_postion > v_detector[:, 1])[0]
    # print(index_1_cut_v_bias)
    # print(index_2_cut_v_bias)
    # # v_bias = np.where(cursor_1_postion < v_bias[:, 1].all() < cursor_2_postion, v_bias[:, 0], 0)
    # # print(v_bias)
    # # cut_v_detector = np.where(cursor_1_postion < v_detector[:, 1].all() < cursor_2_postion, v_detector[:, 0], 0)
    # #
    # return v_bias, v_detector


def test_1() -> None:
    try:
        signal_generator.write("OUTput 1")
        os.chdir(path=r"C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Mechanical cycling")
        time.sleep(5)
        ch4 = get_curve_cycling(channel=4)
        ch2 = get_curve_cycling(channel=2)
        # print(ch4[:, 1])
        # mems_characteristics = extract_data_v3(rf_detector_channel=ch4, v_bias_channel=ch2)
        # signal_generator.write("OUTput 1")
        # print(mems_characteristics)
        # for keys, values in mems_characteristics.items():
        #     print(f'{keys} = {values} \n')
        signal_generator.write("OUTput 0")
        # mems_characteristics.clear()

        wf = save_waveform(waveform_ch4=ch4, waveform_ch2=ch2, filename='test'.upper())
        ax = plt.subplot(111)

        ax.plot(wf[2], wf[0], label='1')
        ax.plot(wf[2], wf[1], label='1')
        plt.show()
    except:
        print("error")
        signal_generator.write("OUTput 0")


def create_pulsed_pull_in_test_waveform(amplitude: int | float = 26, pulse_width: int = 20, filename='test') -> None:
    # Example usage:
    voltage_steps = 10
    voltage_values = sweep(amplitude=amplitude, voltage_steps=voltage_steps)  # Amplitudes of the pulses
    _amplitude = np.max(voltage_values) / 20
    width_pulse = pulse_width  # Duration of each pulse and zero gap in microseconds

    # Generate the waveform
    waveform = create_smooth_pull_in_voltage_waveform(voltages=voltage_values, width_pulse=width_pulse)
    # waveform = load_pull_in_voltage_waveform(voltages=voltage_values, width_pulse_us=width_pulse, max_samples=105)
    # scaled_waveform = scale_waveform_to_dac(waveform=waveform, min_dac=0, max_dac=32767)
    scaled_waveform = waveform
    # print(scaled_waveform, end='\n', sep='\n')
    print(len(scaled_waveform), end='\n')

    # Time vector for plotting (assuming each sample corresponds to a uniform time interval)
    # sample_rate = 7272727  # Hz
    # time_vector = np.linspace(0, len(waveform) * (1 / sample_rate), num=len(waveform), endpoint=False)

    upload_waveform_to_signal_Generator(arb_name=filename, waveform=scaled_waveform, amplitude=_amplitude)

    # Plotting the waveform
    # plt.figure(figsize=(10, 5))
    # plt.plot(time_vector * 1e6, waveform, label='Waveform')  # Time axis converted to microseconds
    # plt.title('Generated Waveform with Pulses and Zero Gaps')
    # plt.xlabel('Time (μs)')
    # plt.ylabel('Amplitude (Volts)')
    # plt.grid(True)
    # plt.legend()
    # plt.show()


def plot_file(filename='default.txt',
              directory=r'C:\Users\TEMIS\Desktop\TEMIS MEMS LAB\Measurement Data\Pullin voltage'):
    os.chdir('{}'.format(directory))
    with open(filename, newline='') as f:
        data_np = np.loadtxt(fname=filename, delimiter=',', unpack=True, skiprows=1)
        v_bias = data_np[:, 0].copy()
        v_log_amp = data_np[:, 1].copy()
        t = data_np[:, 2].copy()
        fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(15, 9), num=1)
        ax[0].plot(t, v_bias)  # , label=f'{length}')  # Time axis converted to microseconds
        ax[0].grid()
        ax[1].plot(t, v_log_amp)  # , label=f'{length}')  # Time axis converted to microseconds
        ax[1].grid()
        ax[2].plot(v_bias, v_log_amp)  # , label=f'{length}')  # Time axis converted to microseconds
        ax[2].grid()
        ax[0].set(ylabel='Bias Voltage (V)', xlabel='Time (s)')
        ax[1].set(ylabel='Detector Voltage (V)', xlabel='Time (s)')
        ax[2].set(ylabel='Detector Voltage (V)', xlabel='Amplitude (V)')
        plt.show()
















def powermeter_trace_acquisition_sequence():
    # try:
    #     limit_str = rf_Generator.query('SOUR:POW:LIM:AMPL?')
    #     limit_dbm = float(limit_str)
    #     safe_power = limit_dbm - 1
    # except:
    #     safe_power = -20  # fallback to a safe value

    # rf_Generator.write(f'SOUR:POW:IMM:AMPL {safe_power}')
    # time.sleep(0.1)
    rf_Generator.write("OUTPut ON")
    rf_Generator.query("*OPC?")
    time.sleep(1)
    powermeter.write("TRAC:STAT ON")
    signal_generator.write("*TRG")
    powermeter.write("INIT:CONT OFF")
    time.sleep(0.1)
    channel_1 = powermeter.query_binary_values(message="TRACe1:DATA? HRESolution",
                                               header_fmt="ieee", is_big_endian=True,
                                               chunk_size=2000)  # Channel A
    channel_2 = powermeter.query_binary_values(message="TRACe2:DATA? HRESolution",
                                               header_fmt="ieee", is_big_endian=True,
                                               chunk_size=2000)  # Channel B

    rf_Generator.write(cmd='OUTPut OFF')
    powermeter.write("INIT:CONT ON")

    return channel_1, channel_2




# initialize_hardware()

# if __name__ == "__main__":
#     os.chdir(r'C:\Users\TEMIS\PycharmProjects\pythonProject\venv\TEMIS MEMS LAB\dummy_data')
#     data = pd.read_csv(filepath_or_buffer=r"Project_Name-Cell_Name-Reticule-Device_name-10V.txt", sep=',')
#     v_bias = data['# #V_bias(V)'].values
#     print(v_bias)
#     v_log_amp = data['rf_detector (V)'].values
#     print(v_log_amp)



if __name__ == "__main__":
    signal_generator = sig_gen_init()
    set_bias_voltage_cycling('50')
    