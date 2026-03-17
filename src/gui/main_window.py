import sys
import os
import argparse

import ttkbootstrap as ttk
import tkinter as tk
from tkinter import Menu
import time
from tkinter import scrolledtext
from typing import Optional, Literal
import pandas as pd
import numpy as np
import skrf as rf
import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg
)
from src.core import scripts_and_functions
from src.core.config import zva_parameters
from src.core import config as dir_and_var_declaration
from src.gui.pull_in_test_window import PullInTestWindow
from src.gui.snp_test_window import SnpTestWindow
from src.gui.power_test_window import PowerTestWindow
from src.gui.cycling_test_window import CyclingTestWindow
from src.gui.pulsed_pull_in_test_window import PulsedPullInTestWindow
from src.gui.scpi_configuration_window import ScpiConfigurationWindow
from src.gui.pull_in_display_window import PullInDisplayWindow
from src.gui.s2p_display_window import S2pDisplayWindow
from src.gui.s3p_display_window import S3pDisplayWindow
from src.gui.time_domain_power_test_window import TimeDomainPowerTestWindow
from src.gui.display_window import DisplayWindow
import threading  # Import threading module
from matplotlib.ticker import FuncFormatter
from ttkbootstrap.constants import *
from src.gui.gui_utils import (
    tab_pad_x, tab_pad_y, default_style, add_tab, add_button, update_button,
    add_label, add_scrolled_text, add_label_frame, extension_detector,
    filetypes_dir, add_entry, add_combobox, add_Checkbutton, close_resources,
    call_s3p_config, call_s2p_config, call_s1p_config, update_entries,
    create_canvas, file_name_creation, create_figure, create_figure_with_axes,
    add_slider, add_small_scale
)


# ==============================================================================
# Imports
# ==============================================================================


# %matplotlib inline

""" This GUI is used to display S Parameters inside a Folder chosen by the user."""
_version = '10'

# This code is dated to 15/02/24

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams["legend.fontsize"] = 10
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.prop_cycle"] = plt.cycler(color=['#005b96', '#d9534f', '#5cb85c', '#f0ad4e', '#5bc0de', '#292b2c', '#e377c2'])
plt.rcParams["lines.linewidth"] = 1.5


class Window(ttk.Frame):
    """
    Main application class for handling SNP file display and acquisition.
    The app controls VNAs ZVA50 & ZVA67, the powermeter A-33521B, the RF generator RS SMB100a, and oscilloscope DPO DPO5054.

    This class inherits from ttk.Frame to provide a main application window.
    It initializes the GUI components and binds the necessary event handlers.
    """

    def __init__(self, master: tk.Tk, offline_mode=False):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        # Declare figures and axes
        self.signal_generator_instance: tk.StringVar
        self.text_snp_debug: tk.Text
        self.text_file_name_s3p_test: tk.Text
        self.canvas_v_pull_in_meas: tk.Canvas
        self.text_file_name_s3p_test: tk.Text
        self.text_iso_pull_out_minus_test: tk.Text
        self.text_iso_pull_in_minus_test: tk.Text
        self.text_iso_pull_out_plus_test: tk.Text
        self.text_pull_out_plus_test: tk.Text
        self.text_pull_out_minus_test: tk.Text
        self.text_pull_in_minus_test: tk.Text
        self.text_iso_pull_in_plus_test: tk.Text
        self.text_pull_in_plus_test: tk.Text
        self.text_iso_pull_out_minus: tk.Text
        self.text_iso_pull_in_minus: tk.Text
        self.text_iso_pull_out_plus: tk.Text
        self.canvas_v_pull_in_meas: tk.Canvas
        self.pull_in_v: tk.DoubleVar
        self.text_gen_controls_pull_in_debug: tk.Text
        self.test_cycling_var_bias: tk.StringVar
        self.test_cycling_var_nb_cycles: tk.DoubleVar
        self.test_cycling_ret: tk.StringVar
        self.test_cycling_project: tk.StringVar
        self.test_cycling_events: tk.DoubleVar
        self.test_cycling_var_nb_cycles: tk.DoubleVar
        self.test_pull_in_dir: tk.StringVar
        self.text_file_name_pull_in_test: tk.Text
        self.text_file_name_s3p_test: tk.Text
        self.test_s3p_dir: tk.StringVar
        self.nb_points: tk.DoubleVar
        self.text_gen_controls_pull_in_debug: tk.Text
        self.text_snp_debug: tk.Text
        self.zva_inst: tk.StringVar
        self.scale_frequency_lower_value: tk.DoubleVar
        self.scale_frequency_upper_value: tk.DoubleVar
        self.scale_isolation_value: tk.DoubleVar
        self.scale_voltage_value: tk.DoubleVar
        self.scale_amplitude_value: tk.DoubleVar
        self.s_parameter_s2p: tk.StringVar
        self.s_parameter_s3p: tk.StringVar
        self.fig_s3p: plt.figure
        self.ax_s3p: plt.axes
        self.fig_s2p: plt.axes
        self.ax_s2p: plt.axes
        self.fig_pull_in: plt.figure
        self.ax_pull_in: plt.axes
        self.fig_pull_in_meas: plt.figure
        self.ax_pull_in_meas: plt.axes
        self.fig_snp_meas: plt.figure
        self.ax_snp_meas: plt.axes
        self.fig_cycling: plt.figure
        self.ax_cycling_pull_in: plt.axes
        self.ax_cycling_pull_out: plt.axes
        self.ax_cycling_isolation: plt.axes
        self.ax_cycling_insertion_loss: plt.axes
        self.ax_cycling_t_down: plt.axes
        self.ax_cycling_t_up: plt.axes
        self.fig_power_meas: plt.figure
        self.ax_power_meas: plt.axes
        self.nb_points: tk.DoubleVar
        self.text_file_name_s3p_test: tk.Text
        self.canvas_cycling: FigureCanvasTkAgg
        self.ax_time_domain_power_meas: plt.axes
        self.fig_time_domain_power_meas: plt.figure

        self.zva_inst: tk.StringVar = tk.StringVar(value='TCPIP0::ZNA67-101810::inst0::INSTR')
        self.signal_generator_instance: tk.StringVar = tk.StringVar(value='TCPIP0::A-33521B-00526::inst0::INSTR')
        self.osc_inst: tk.StringVar = tk.StringVar(value='TCPIP0::DPO5054-C011738::inst0::INSTR')
        self.powermeter_inst: tk.StringVar = tk.StringVar(value='TCPIP0::A-N1912A-00589::inst0::INSTR')
        self.rf_gen_inst: tk.StringVar = tk.StringVar(value='TCPIP0::rssmb100a179766::inst0::INSTR')

        # Directories for display windows
        self.s3p_dir_name = tk.StringVar(
            value=dir_and_var_declaration.PC_File_Dir_s3p_Display)
        self.s2p_dir_name = tk.StringVar(
            value=dir_and_var_declaration.PC_File_Dir_s2p_Display)
        self.pull_in_dir_name = tk.StringVar(
            value=dir_and_var_declaration.PC_File_Dir_pull_in_Display)

        # Directories for cycling window
        self.test_cycling_dir = tk.StringVar(
            value=dir_and_var_declaration.PC_File_Dir_s3p_Cycling)

        # Directories for test windows
        self.test_pull_in_dir = tk.StringVar(value=dir_and_var_declaration.PC_File_Dir_pull_in_Display)
        self.txt_file_name_combobox = tk.StringVar()

        # Initialize hardware using the IPs from the StringVar instances
        scripts_and_functions.initialize_hardware(
            zva_ip=self.zva_inst.get(),
            sig_gen_ip=self.signal_generator_instance.get(),
            osc_ip=self.osc_inst.get(),
            powermeter_ip=self.powermeter_inst.get(),
            rf_gen_ip=self.rf_gen_inst.get(),
            offline=offline_mode
        )

        self.file_df: pd.DataFrame = pd.DataFrame(
            columns=["vpullin_plus", "vpullin_minus", "vpullout_plus", "vpullout_minus", "t_on_time",
                     "insertion_loss", "t_off_time", "isolation", "cycles", "sticking events"],
            dtype=np.float64, data=None)

        self.file_power_sweep = pd.DataFrame(columns=['Power Input DUT Avg (dBm)', 'Power Output DUT Avg (dBm)'])

        self.update_interval = 5000  # Update interval in milliseconds

        # Cycling status
        self.is_cycling = False
        self.is_power_sweeping = False
        # Configure styles
        # self.zva_inst = None
        self.configure_window()

        # Initialize figures and axes
        self.init_figures()

        # Initialize variables
        self.init_variables()

        # Set up the main menu
        self.create_main_menu()

        # Create the menu bar
        self.menubar()

        # Create an event to signal new data availability
        self.new_data_event = threading.Event()
        self.new_data_event_power_sweep = threading.Event()
        self.data_thread = threading.Thread(target=self.run_new_data_event)
        self.data_thread.daemon = True  # Ensures the thread will close when the main program exits
        self.data_thread.start()

        self.stop_requested = False
        self.pull_in_test_window_instance: Optional[PullInTestWindow] = None
        self.pull_in_display_window_instance: Optional[PullInDisplayWindow] = None
        self.snp_test_window_instance: Optional[SnpTestWindow] = None

    def on_checkbutton_toggle(self):
        """Handles the toggle action from the Checkbutton."""
        scripts_and_functions.toggle_signal_generator()
        # Update the Checkbutton state to reflect the actual state of the signal generator
        current_status = scripts_and_functions.query_signal_generator()
        self.toggle_state.set(True if current_status[0] == '1' else False)

    def configure_window(self):
        s = ttk.Style()
        s.configure('TButton', anchor='center', justify='center')
        s.configure('large.TButton', font=('Bahnschrift Light', 14))
        s.configure(style='.', font=('Bahnschrift Light', 10))

        # Set window properties
        self.master.title(f"SUMMIT 11K Machine Interface v{_version}")
        self.master.geometry("500x350")
        self.master.resizable(width=True, height=True)

    def init_figures(self):
        """Initialize all the matplotlib figures and their respective axes."""
        self.create_pulsed_pull_in_wf()
        self.create_cycling_axes()
        self.create_power_sweeping_axes()
        self.create_s3p_display_wf()
        self.create_snp_meas_wf()
        self.create_pull_in_meas_wf()
        self.create_s2p_display_wf()
        self.create_pull_in_display_wf()
        self.create_time_domain_power_axes_v2()

    def create_time_domain_power_axes_v2(self):
        self.fig_time_domain_power_meas = create_figure(num=9, figsize=(8.5, 6))
        self.ax_time_domain_power_meas_input = self.fig_time_domain_power_meas.add_subplot(2, 1, 1)
        self.ax_time_domain_power_meas_input.set(xlabel="time (s)", ylabel="Power (dBm)", title="Input Pulse")
        self.ax_time_domain_power_meas_input.grid("both")
        self.ax_time_domain_power_meas_output = self.fig_time_domain_power_meas.add_subplot(2, 1, 2)
        self.ax_time_domain_power_meas_output.set(xlabel="time (s)", ylabel="Power (dBm)", title="Output Pulse")
        self.ax_time_domain_power_meas_output.grid("both")

    def create_s3p_display_wf(self):
        self.fig_s3p, self.ax_s3p = create_figure_with_axes(num=1, figsize=(13, 4.1))
        self.ax_s3p.set_title("|Sij| vs frequency")
        self.ax_s3p.set(xlabel="Frequency (Hz)", ylabel="S Parameter (dB)", title="S Parameter vs Frequency")
        self.ax_s3p.grid(True)

    def create_s2p_display_wf(self):
        self.fig_s2p, self.ax_s2p = create_figure_with_axes(num=2, figsize=(13, 4.1))
        self.ax_s2p.set_title("|Sij| vs frequency")
        self.ax_s2p.set(xlabel="Frequency (Hz)", ylabel="S Parameter (dB)", title="S Parameter vs Frequency")
        self.ax_s2p.grid(True)

    def create_pull_in_display_wf(self):
        self.fig_pull_in, self.ax_pull_in = create_figure_with_axes(num=3, figsize=(13, 3.5))
        self.ax_pull_in.set(xlabel="V bias (V)", ylabel="Detector voltage (V)", title="Isolation vs Bias voltage")
        self.ax_pull_in.grid(True)

    def create_pull_in_meas_wf(self):
        self.fig_pull_in_meas, self.ax_pull_in_meas = create_figure_with_axes(num=4, figsize=(8.5, 6))
        self.ax_pull_in_meas.set(xlabel="V bias (V)", ylabel="Detector voltage (V)",
                                 title="Isolation vs Bias voltage")
        self.ax_pull_in_meas.grid(True)

    def create_snp_meas_wf(self):
        self.fig_snp_meas, self.ax_snp_meas = create_figure_with_axes(num=5, figsize=(8.5, 6))
        self.ax_snp_meas.set(xlabel="Frequency (Hz)", ylabel="S Parameter (dB)", title="|S| Parameter vs Frequency")
        self.ax_snp_meas.grid(True)

    def create_power_sweeping_axes(self):
        self.ax_power_meas = self.fig_power_meas.add_subplot(1, 1, 1)
        self.ax_power_meas.set(xlabel="Pin (dBm)", ylabel="Pout (dBm)", title="Pout vs Pin")
        self.ax_power_meas.set_xscale('linear')
        self.ax_power_meas.grid("both")
        self.ax_power_meas_secondary = self.ax_power_meas.twinx()
        self.ax_power_meas_secondary.set_ylabel('Loss (dB)')

    def create_cycling_axes(self):
        """Create and configure axes for the cycling figure."""
        self.ax_cycling_pull_in = self.fig_cycling.add_subplot(3, 2, 1)
        self.ax_cycling_pull_in.set(xlabel="Cycles", ylabel="Pull-in (V)", title="Pull-in Voltage")
        self.ax_cycling_pull_in.set_xscale('log')
        self.ax_cycling_pull_in.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_pull_out = self.fig_cycling.add_subplot(3, 2, 2)
        self.ax_cycling_pull_out.set(xlabel="Cycles", ylabel="Pull-out (V)", title="Pull-out Voltage")
        self.ax_cycling_pull_out.set_xscale('log')
        self.ax_cycling_pull_out.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_isolation = self.fig_cycling.add_subplot(3, 2, 3)
        self.ax_cycling_isolation.set(xlabel="Cycles", ylabel="Isolation (dB)", title="Isolation")
        self.ax_cycling_isolation.set_xscale('log')
        self.ax_cycling_isolation.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_insertion_loss = self.fig_cycling.add_subplot(3, 2, 4)
        self.ax_cycling_insertion_loss.set(xlabel="Cycles", ylabel="Insertion loss variation (dB)",
                                           title="Insertion loss variation")
        self.ax_cycling_insertion_loss.set_xscale('log')
        self.ax_cycling_insertion_loss.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_t_down = self.fig_cycling.add_subplot(3, 2, 5)
        self.ax_cycling_t_down.set(xlabel="Cycles", ylabel="ts_down (s)", title="Down state switching time")
        self.ax_cycling_t_down.set_xscale('log')
        self.ax_cycling_t_down.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_t_up = self.fig_cycling.add_subplot(3, 2, 6)
        self.ax_cycling_t_up.set(xlabel="Cycles", ylabel="ts_up (s)", title="Up state switching time")
        self.ax_cycling_t_up.set_xscale('log')
        self.ax_cycling_t_up.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        for ax in self.fig_cycling.axes:
            ax.grid()

    def create_pulsed_pull_in_wf(self):
        self.fig_pulsed_pull_in_meas = create_figure(num=8, figsize=(8.5, 6))
        self.ax_pulsed_pull_in_meas = self.fig_pulsed_pull_in_meas.add_subplot(2, 1, 1)
        self.ax_pulsed_pull_in_meas.grid('both')
        self.ax_pulsed_pull_in_meas.set(xlabel="V bias (V)", ylabel="Detector voltage (V)",
                                        title="Isolation vs Bias voltage")
        self.ax_pulsed_pull_in_wf = self.fig_pulsed_pull_in_meas.add_subplot(2, 1, 2)
        self.ax_pulsed_pull_in_wf.grid('both')
        self.ax_pulsed_pull_in_wf.set(xlabel="time (s)", ylabel="Detector voltage / V bias (V)",
                                      title="Detector voltage & V bias")
        self.ax_pulsed_pull_in_wf_det = self.ax_pulsed_pull_in_wf.twinx()

    def create_power_sweeping_axes(self):
        self.fig_power_meas = create_figure(num=7, figsize=(8.5, 6))
        self.ax_power_meas = self.fig_power_meas.add_subplot(1, 1, 1)
        self.ax_power_meas.set(xlabel="Pin (dBm)", ylabel="Pout (dBm)", title="Pout vs Pin")
        self.ax_power_meas.set_xscale('linear')
        self.ax_power_meas.grid("both")
        self.ax_power_meas_secondary = self.ax_power_meas.twinx()
        self.ax_power_meas_secondary.set_ylabel('Loss (dB)')

    def create_cycling_axes(self):
        """Create and configure axes for the cycling figure."""
        self.fig_cycling = create_figure(num=6, figsize=(10, 6))
        self.ax_cycling_pull_in = self.fig_cycling.add_subplot(3, 2, 1)
        self.ax_cycling_pull_in.set(xlabel="Cycles", ylabel="Pull-in (V)", title="Pull-in Voltage")
        self.ax_cycling_pull_in.set_xscale('log')
        self.ax_cycling_pull_in.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_pull_out = self.fig_cycling.add_subplot(3, 2, 2)
        self.ax_cycling_pull_out.set(xlabel="Cycles", ylabel="Pull-out (V)", title="Pull-out Voltage")
        self.ax_cycling_pull_out.set_xscale('log')
        self.ax_cycling_pull_out.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_isolation = self.fig_cycling.add_subplot(3, 2, 3)
        self.ax_cycling_isolation.set(xlabel="Cycles", ylabel="Isolation (dB)", title="Isolation")
        self.ax_cycling_isolation.set_xscale('log')
        self.ax_cycling_isolation.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_insertion_loss = self.fig_cycling.add_subplot(3, 2, 4)
        self.ax_cycling_insertion_loss.set(xlabel="Cycles", ylabel="Insertion loss variation (dB)",
                                           title="Insertion loss variation")
        self.ax_cycling_insertion_loss.set_xscale('log')
        self.ax_cycling_insertion_loss.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_t_down = self.fig_cycling.add_subplot(3, 2, 5)
        self.ax_cycling_t_down.set(xlabel="Cycles", ylabel="ts_down (s)", title="Down state switching time")
        self.ax_cycling_t_down.set_xscale('log')
        self.ax_cycling_t_down.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        self.ax_cycling_t_up = self.fig_cycling.add_subplot(3, 2, 6)
        self.ax_cycling_t_up.set(xlabel="Cycles", ylabel="ts_up (s)", title="Up state switching time")
        self.ax_cycling_t_up.set_xscale('log')
        self.ax_cycling_t_up.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

        for ax in self.fig_cycling.axes:
            ax.grid(True)

    def init_variables(self):
        """Initialize Tkinter variables."""
        self.s_parameter_s3p = tk.StringVar(value='S11')
        self.s_parameter_s2p = tk.StringVar(value='S11')

        self.scale_amplitude_value = tk.DoubleVar(value=-20)
        self.scale_voltage_value = tk.DoubleVar(value=50)
        self.scale_isolation_value = tk.DoubleVar(value=-1)
        self.scale_frequency_upper_value = tk.DoubleVar(value=2 * 10e9)
        self.scale_frequency_lower_value = tk.DoubleVar(value=0.1 * 10e9)
        self.ramp_width = tk.DoubleVar(value=100)
        self.f_start = tk.DoubleVar(value=1)
        self.f_stop = tk.DoubleVar(value=10)
        self.nb_points = tk.DoubleVar(value=100)

        self.pull_in_v_bias = tk.DoubleVar(value=0.0)
        self.pulse_width = tk.DoubleVar(value=0.0)
        self.pulse_freq = tk.DoubleVar(value=0.0)

        self.ax_s3p.set_ylim(ymin=self.scale_amplitude_value.get(), ymax=0)
        self.ax_s3p.set_xlim(xmin=0, xmax=self.scale_frequency_upper_value.get())

    def create_main_menu(self):
        """Create the main menu with buttons to open different windows."""
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Configure the grid to be centered
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        for i in range(5):
            main_frame.grid_rowconfigure(i, weight=1)

        add_button(main_frame, "Display", self.open_display_window, 0, 0, style='large.TButton')
        add_button(main_frame, "Power Test", self.open_power_test_window, 1, 0, style='large.TButton')
        add_button(main_frame, "Pull-in Test", self.open_pull_in_test_window, 0, 1, style='large.TButton')
        add_button(main_frame, "Cycling tab", self.open_cycling_window, 1, 1, style='large.TButton')
        add_button(main_frame, "SNP Test", self.open_snp_test_window, 0, 2, style='large.TButton')
        add_button(main_frame, "Resource Page", self.open_resource_page_window, 1, 2, style='large.TButton')
        add_button(main_frame, "Pulsed pull-in", self.open_pulsed_pull_in_window, 0, 3, style='large.TButton')
        add_button(main_frame, "Time domain Power test", self.open_time_domain_power_test_window, 1, 3,
                   style='large.TButton')
        add_button(main_frame, "Exit", self._quit, 0, 4, style='large.TButton', columnspan=2)
        # Add other buttons here for other windows in the future

    def open_display_window(self):
        """Open the Display window."""
        display_window = tk.Toplevel(self)
        display_window.title("Display")
        display_window.resizable(width=True, height=True)
        display_window.grid_rowconfigure(0, weight=1)
        display_window.grid_columnconfigure(0, weight=1)
        DisplayWindow(display_window, self)

    def open_time_domain_power_test_window(self):
        """Open the Time domain Power test window."""
        time_domain_power_test_window = tk.Toplevel(self)
        time_domain_power_test_window.title("Time domain Power test")
        time_domain_power_test_window.resizable(width=True, height=True)
        time_domain_power_test_window.grid_rowconfigure(0, weight=1)
        time_domain_power_test_window.grid_columnconfigure(0, weight=1)
        TimeDomainPowerTestWindow(time_domain_power_test_window, self)

    def open_pull_in_test_window(self):
        """Open the Pull-in test window."""
        pull_in_test_window = tk.Toplevel(self)
        pull_in_test_window.title("Pull-in Test")
        pull_in_test_window.resizable(width=True, height=True)
        pull_in_test_window.grid_rowconfigure(0, weight=1)
        pull_in_test_window.grid_columnconfigure(0, weight=1)
        self.pull_in_test_window_instance = PullInTestWindow(pull_in_test_window, self)

    def open_snp_test_window(self):
        """Open the SNP test window."""
        snp_test_window = tk.Toplevel(self)
        snp_test_window.title("SNP Test")
        snp_test_window.resizable(width=True, height=True)
        snp_test_window.grid_rowconfigure(0, weight=1)
        snp_test_window.grid_columnconfigure(0, weight=1)
        self.snp_test_window = SnpTestWindow(snp_test_window, self)

    def open_power_test_window(self):
        """Open the Power test window."""
        power_test_window = tk.Toplevel(self)
        power_test_window.title("Power Test")
        power_test_window.resizable(width=True, height=True)
        power_test_window.grid_rowconfigure(0, weight=1)
        power_test_window.grid_columnconfigure(0, weight=1)
        PowerTestWindow(power_test_window, self)

    def open_cycling_window(self):
        """Open the Cycling test window."""
        cycling_window = tk.Toplevel(self)
        cycling_window.title("Cycling tab")
        cycling_window.resizable(width=True, height=True)
        cycling_window.grid_rowconfigure(0, weight=1)
        cycling_window.grid_columnconfigure(0, weight=1)

        CyclingTestWindow(cycling_window, self)

    def open_resource_page_window(self):
        """Open the Resource Page window."""
        resource_page_window = tk.Toplevel(self)
        resource_page_window.title("Resource Page")
        resource_page_window.resizable(width=True, height=True)
        resource_page_window.grid_rowconfigure(0, weight=1)
        resource_page_window.grid_columnconfigure(0, weight=1)
        ScpiConfigurationWindow(resource_page_window, self)

    def open_pulsed_pull_in_window(self):
        """Open the Pulsed pull-in test window."""
        pulsed_pull_in_window = tk.Toplevel(self)
        pulsed_pull_in_window.title("Pulsed pull-in")
        pulsed_pull_in_window.resizable(width=True, height=True)
        pulsed_pull_in_window.grid_rowconfigure(0, weight=1)
        pulsed_pull_in_window.grid_columnconfigure(0, weight=1)
        PulsedPullInTestWindow(pulsed_pull_in_window, self)

    def menubar(self):
        """
        Creates the main menu bar for the application window.
        """
        # Create the main menu bar
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        # Create the File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label='New', command=self._new_file)
        file_menu.add_command(label='Open', command=self._open_file)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self._quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Create the Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label='About', command=self._about_msg)
        menubar.add_cascade(label="Help", menu=help_menu)

    def _quit(self):
        """
        Exits the application, ensuring that the window is closed and destroyed.
        """
        self.master.quit()
        self.master.destroy()

    def _about_msg(self):
        """
        Displays an 'About' message box with information about the application.
        """
        # about_message = (f"This is a GUI for MEMS characterization, version {_version}. "
        #                  "For more information, please contact the author at a.person@mail.com")
        # msg.showinfo('About', about_message)

    def _open_file(self):
        """
        Opens a file dialog to select a file and prints the selected file's path.
        """
        # file = filedialog.askopenfilename(parent=self.master,
        #                                   initialdir=r"C:\Users\a\Desktop",
        #                                   title='Select a file',
        #                                   filetypes=(("Text files", "*.txt"), ("All files", "*.*")У))
        # if file:
        #     print(f"Selected file: {file}")

    def _new_file(self):
        """
        Placeholder for creating a new file. Currently, it just prints a message.
        """
        print("New file created")

    def trace_s3p(self, filename: str | list, s_param: str):
        """
        Reads an S3P file, plots the specified S-parameter, and updates the canvas.
        """
        if not filename or not s_param:
            return

        # Clear the previous plot
        self._clear_ax_lines(self.ax_s3p)

        if isinstance(filename, str):
            filenames = [filename]
        else:
            filenames = filename

        for fn in filenames:
            try:
                filepath = os.path.join(self.s3p_dir_name.get(), fn)
                # Read the S3P file using skrf
                network = rf.Network(filepath)
                network.frequency.unit('GHz')
                network.frequency.unit = 'GHz'
                # Plot the specified S-parameter
                network.plot_s_db(m=int(s_param[1]) - 1, n=int(s_param[2]) - 1, ax=self.ax_s3p, label=f"{fn} S{s_param[1]}{s_param[2]}")
            except Exception as e:
                print(f"Error plotting S3P file {fn}: {e}")

        self.ax_s3p.grid(True)
        if self.ax_s3p.get_legend():
            self.ax_s3p.legend()

        # Redraw the canvas
        self.fig_s3p.canvas.draw()

    def trace_s2p(self, filename: str | list, s_param: str):
        """
        Reads an S2P file, plots the specified S-parameter, and updates the canvas.
        """
        if not filename or not s_param:
            return

        # Clear the previous plot
        self._clear_ax_lines(self.ax_s2p)

        if isinstance(filename, str):
            filenames = [filename]
        else:
            filenames = filename

        for fn in filenames:
            try:
                filepath = os.path.join(self.s2p_dir_name.get(), fn)
                # Read the S2P file using skrf
                network = rf.Network(filepath)
                network.frequency.unit = 'GHz'

                # Plot the specified S-parameter
                network.plot_s_db(m=int(s_param[1]) - 1, n=int(s_param[2]) - 1, ax=self.ax_s2p, label=f"{fn} S{s_param[1]}{s_param[2]}")
            except Exception as e:
                print(f"Error plotting S2P file {fn}: {e}")

        self.ax_s2p.grid(True)
        if self.ax_s2p.get_legend():
            self.ax_s2p.legend()

        # Redraw the canvas
        self.fig_s2p.canvas.draw()

    def trace_s1p(self, filename: str | list, s_param: str):
        """
        Reads an S1P file, plots the specified S-parameter, and updates the canvas.
        """
        if not filename or not s_param:
            return

        # Clear the previous plot
        self._clear_ax_lines(self.ax_s2p)

        if isinstance(filename, str):
            filenames = [filename]
        else:
            filenames = filename

        for fn in filenames:
            try:
                filepath = os.path.join(self.s2p_dir_name.get(), fn)
                # Read the S1P file using skrf
                network = rf.Network(filepath)
                network.frequency.unit = 'GHz'
                # Plot the specified S-parameter
                network.plot_s_db(m=int(s_param[1]) - 1, n=int(s_param[2]) - 1, ax=self.ax_s2p, label=f"{fn} S{s_param[1]}{s_param[2]}")
            except Exception as e:
                print(f"Error plotting S1P file {fn}: {e}")

        self.ax_s2p.grid(True)
        if self.ax_s2p.get_legend():
            self.ax_s2p.legend()

        # Redraw the canvas
        self.fig_s2p.canvas.draw()

    def trace_pull_down(self, filename: str | list):

        if not filename:
            return

        if isinstance(filename, str):
            filenames = [filename]
        else:
            filenames = filename

        # Clear the previous plot
        self._clear_ax_lines(self.ax_pull_in)
        self._clear_ax_lines(self.ax_pull_in_meas)
        self.text_scroll.delete("1.0", tk.END)

        for fn in filenames:
            # Ensure filename has .txt extension
            if not fn.endswith('.txt'):
                fn += '.txt'

            if self.pull_in_display_window_instance is not None:
                directory_display = self.pull_in_dir_name.get()
                filepath_display = os.path.join(directory_display, fn)
                try:
                    # Read the data from the file
                    with open(filepath_display, newline=''):
                        data_display = np.loadtxt(filepath_display, delimiter=',', unpack=True, skiprows=1)
                        v_bias_display = data_display[:, 0].copy()
                        v_log_amp_display = data_display[:, 1].copy()

                        pull_in_calculations_data_display = scripts_and_functions.calculate_actuation_and_release_voltages(
                            v_bias=v_bias_display,
                            v_logamp=v_log_amp_display)
                except FileNotFoundError:
                    print(f"File {fn} not found or bugged processing")
                    continue

                self.text_scroll.insert(tk.END, f'--- {fn} ---\n')
                self.text_scroll.insert(tk.END, 'Positive Pull-in voltage = {} V \n'.format(pull_in_calculations_data_display['vpullin_plus']))
                self.text_scroll.insert(tk.END, 'Negative Pull-in voltage = {} V \n'.format(pull_in_calculations_data_display['vpullin_minus']))
                self.text_scroll.insert(tk.END, 'Positive Pull-out voltage (+) = {} V \n'.format(pull_in_calculations_data_display['vpullout_plus']))
                self.text_scroll.insert(tk.END, 'Negative Pull-out voltage (+) = {} V \n'.format(pull_in_calculations_data_display['vpullout_minus']))
                self.text_scroll.insert(tk.END, 'Isolation (+) = {} dB \n'.format(pull_in_calculations_data_display['ninetypercent_iso_ascent']))
                self.text_scroll.insert(tk.END, 'Isolation (-) = {} dB \n\n'.format(pull_in_calculations_data_display['ninetypercent_iso_descent']))

                # Plot the data
                self.ax_pull_in.plot(v_bias_display, v_log_amp_display - np.max(v_log_amp_display), label="{}".format(fn)[:-4])

            if self.pull_in_test_window_instance is not None:
                directory_test = self.test_pull_in_dir.get()
                filepath_test = os.path.join(directory_test, fn)
                try:
                    with open(filepath_test, newline=''):
                        data_test = np.loadtxt(filepath_test, delimiter=',', unpack=True, skiprows=1)
                        v_bias_test = data_test[:, 0].copy()
                        v_log_amp_test = data_test[:, 1].copy()

                        pull_in_calculations_data_test = scripts_and_functions.calculate_actuation_and_release_voltages(
                            v_bias=v_bias_test,
                            v_logamp=v_log_amp_test)
                except FileNotFoundError:
                    print(f"File {fn} not found or bugged processing")
                    continue

                self.pull_in_test_window_instance.text_pull_in_plus_test.delete("1.0", "end")
                self.pull_in_test_window_instance.text_pull_in_minus_test.delete("1.0", "end")
                self.pull_in_test_window_instance.text_pull_out_plus_test.delete("1.0", "end")
                self.pull_in_test_window_instance.text_pull_out_minus_test.delete("1.0", "end")
                self.pull_in_test_window_instance.text_iso_pull_in_plus_test.delete("1.0", "end")
                self.pull_in_test_window_instance.text_iso_pull_in_minus_test.delete("1.0", "end")

                self.pull_in_test_window_instance.text_pull_in_plus_test.insert(tk.END, pull_in_calculations_data_test['vpullin_plus'])
                self.pull_in_test_window_instance.text_pull_in_minus_test.insert(tk.END, pull_in_calculations_data_test['vpullin_minus'])
                self.pull_in_test_window_instance.text_pull_out_plus_test.insert(tk.END, pull_in_calculations_data_test['vpullout_plus'])
                self.pull_in_test_window_instance.text_pull_out_minus_test.insert(tk.END, pull_in_calculations_data_test['vpullout_minus'])
                self.pull_in_test_window_instance.text_iso_pull_in_plus_test.insert(tk.END, pull_in_calculations_data_test['ninetypercent_iso_ascent'])
                self.pull_in_test_window_instance.text_iso_pull_in_minus_test.insert(tk.END, pull_in_calculations_data_test['ninetypercent_iso_descent'])

                # Plot the data
                self.ax_pull_in_meas.plot(v_bias_test, v_log_amp_test - np.max(v_log_amp_test), label="{}".format(fn)[:-4])

        if self.pull_in_display_window_instance is not None:
            self.ax_pull_in.grid(True)
            self.ax_pull_in.legend()
            self.fig_pull_in.canvas.draw()
            
        if self.pull_in_test_window_instance is not None:
            self.ax_pull_in_meas.grid(True)
            self.ax_pull_in_meas.legend()
            self.fig_pull_in_meas.canvas.draw()

    def calculate_pull_in_out_voltage(self):
        """
        Placeholder for calculating pull-in and pull-out voltages.
        This method needs to be implemented.
        """
        print("Calculating pull-in/out voltages (placeholder).")

    def update_s3p_plot_limits(self, *args):
        """
        Updates the plot limits for the S3P graph based on the slider values.
        """
        try:
            self.ax_s3p.set_ylim(bottom=self.scale_amplitude_value.get(), top=0)
            self.ax_s3p.set_xlim(left=self.scale_frequency_lower_value.get(),
                                 right=self.scale_frequency_upper_value.get())
            self.fig_s3p.canvas.draw()
        except Exception as e:
            print(f"Error updating S3P plot limits: {e}")

    def update_s2p_plot_limits(self, *args):
        """
        Updates the plot limits for the S2P graph based on the slider values.
        """
        try:
            self.ax_s2p.set_ylim(bottom=self.scale_amplitude_value.get(), top=0)
            self.ax_s2p.set_xlim(left=self.scale_frequency_lower_value.get(),
                                 right=self.scale_frequency_upper_value.get())
            self.fig_s2p.canvas.draw()
        except Exception as e:
            print(f"Error updating S2P plot limits: {e}")

    def _clear_ax_lines(self, ax):
        while ax.lines:
            ax.lines[0].remove()
        for poly in getattr(ax, 'collections', []):
            poly.remove()
        if ax.get_legend():
            ax.get_legend().remove()
        ax.relim()
        ax.autoscale_view()

    def delete_axs_s3p(self):
        """Clears the S3P plot axes."""
        self._clear_ax_lines(self.ax_s3p)
        self.fig_s3p.canvas.draw()

    def delete_axs_s2p(self):
        """Clears the S2P plot axes."""
        self._clear_ax_lines(self.ax_s2p)
        self.fig_s2p.canvas.draw()

    def delete_axs_vpullin(self):
        """Clears the Pull-in plot axes."""
        self._clear_ax_lines(self.ax_pull_in)
        self.fig_pull_in.canvas.draw()

    def set_f_start(self, f_start_value):
        """
        Sets the start frequency on the ZVA instrument.
        """
        scripts_and_functions.set_f_start(f_start_value)

    def set_fstop(self, f_stop_value):
        """
        Sets the stop frequency on the ZVA instrument.
        """
        scripts_and_functions.set_fstop(f_stop_value)

    def set_nb_points(self, nb_points_value):
        """
        Sets the number of points for the ZVA sweep.
        """
        scripts_and_functions.number_of_points(nb_points_value)

    def set_zva(self, f_start_value, f_stop_value, nb_points_value):
        """
        Configures the ZVA with start frequency, stop frequency, and number of points.
        """
        self.set_f_start(f_start_value)
        self.set_fstop(f_stop_value)
        self.set_nb_points(nb_points_value)

    def set_bias_voltage(self, pull_in_v_value):
        """
        Sets the bias voltage on the signal generator.
        """
        scripts_and_functions.dc_voltage(pull_in_v_value)

    def set_ramp_width(self, ramp_width_value):
        """
        Sets the ramp width on the signal generator.
        """
        scripts_and_functions.ramp_width(ramp_width_value)

    def set_prf(self, pulse_freq_value):
        """
        Sets the pulse repetition frequency on the signal generator.
        """
        scripts_and_functions.set_prf(pulse_freq_value)

    def set_pulse_gen(self, pull_in_v_value, ramp_width_value, pulse_freq_value):
        """
        Configures the signal generator with bias voltage, ramp width, and PRF.
        """
        self.set_bias_voltage(pull_in_v_value)
        self.set_ramp_width(ramp_width_value)
        self.set_prf(pulse_freq_value)

    def set_bias_pull_in(self, pull_in_v_bias_value):
        """
        Sets the bias voltage for the pull-in measurement.
        """
        scripts_and_functions.bias_pull_in_voltage(pull_in_v_bias_value)

    def set_pulse_gen_ramp(self, pull_in_v_bias_value, ramp_width_value):
        """
        Configures the signal generator for a ramp waveform.
        """
        scripts_and_functions.configuration_sig_gen_pull_in(amplitude=pull_in_v_bias_value,
                                                            ramp_length=ramp_width_value)

    def set_pulse_gen_ramp_and_bias(self, pull_in_v_bias_value, ramp_width_value):
        """
        Configures the signal generator for a ramp waveform and sets the bias voltage for the pull-in measurement.
        """
        scripts_and_functions.bias_pull_in_voltage(pull_in_v_bias_value)
        scripts_and_functions.ramp_width(ramp_width_value)

    def set_pulse_gen_pulse_mode(self, amplitude: float, pulse_width: float, prf: float):
        """
        Configures the signal generator for pulse mode.
        """
        scripts_and_functions.bias_voltage(voltage=amplitude)
        scripts_and_functions.set_signal_generator_pulse_parameters(pulse_width=pulse_width,
                                                                    pulse_period=1 / prf,
                                                                    burst_mode=True)

    def set_pulse_width(self, pulse_width):
        scripts_and_functions.signal_generator.write(f"SOURce1:FUNCtion:PULSe:WIDTh {pulse_width}S")

    def acquire_pull_down_data(self, filename: str, text_widget: tk.Text):
        """
        Acquires pull-down data from the oscilloscope and saves it to a file.
        """

        if not filename:
            print("Filename is empty. Cannot acquire data.")
            return

        directory = self.test_pull_in_dir.get()
        os.chdir(directory)
        try:

            scripts_and_functions.send_trig()
            scripts_and_functions.measure_pull_down_voltage(filename)
            text_widget.delete("1.0", "end-1c")
            text_widget.insert("1.0", f"Pull-in data saved as {filename}\n")
            self.trace_pull_down(filename, directory=directory)
        except Exception as e:
            print(f"Error acquiring pull-down data: {e}")
            text_widget.insert("1.0", f"Error: {e}\n")

    def acquire_pull_down_data_pulsed(self):
        """
        Acquires pulsed pull-down data from the oscilloscope and saves it.
        """
        filename = self.text_pulsed_file_name_pull_in_test.get("1.0", "end-1c")
        if not filename:
            print("Filename is empty. Cannot acquire data.")
            return

        try:
            os.chdir(self.test_pulsed_pull_in_dir.get())
            scripts_and_functions.measure_pull_down_voltage_pulsed(filename)
            self.text_gen_controls_pull_in_debug.insert("1.0", f"Pulsed pull-in data saved as {filename}\n")
        except Exception as e:
            print(f"Error acquiring pulsed pull-down data: {e}")
            self.text_gen_controls_pull_in_debug.insert("1.0", f"Error: {e}\n")

    def trace_pull_in_pulsed(self):
        """
        Traces the pulsed pull-in waveform on the plot.
        """
        filename = self.text_pulsed_file_name_pull_in_test.get("1.0", "end-1c")
        if not filename:
            return

        try:
            data = pd.read_csv(filepath_or_buffer=filename, sep='\t', header=0)
            self.ax_pulsed_pull_in_wf.clear()
            data.plot(x='Time (s)', y='V bias (V)', ax=self.ax_pulsed_pull_in_wf, grid=True,
                      label='V bias')
            data.plot(x='Time (s)', y='Detector voltage (V)', ax=self.ax_pulsed_pull_in_wf, grid=True,
                      label='V detector', secondary_y=True)
            self.fig_pulsed_pull_in_meas.canvas.draw()
        except Exception as e:
            print(f"Error tracing pulsed pull-in: {e}")

    def reset_zva(self, text_widget: tk.Text):
        """
        Resets and re-initializes the ZVA instrument.
        """
        try:
            scripts_and_functions.setup_zva_with_rst(self.zva_inst.get())
            text_widget.insert("1.0", "ZVA reset and initialized.\n")
        except Exception as e:
            print(f"Error resetting ZVA: {e}")
            text_widget.insert("1.0", f"Error: {e}\n")

    def reset_zva_no_setup(self, text_widget: tk.Text):
        """
        Reconnects to the ZVA without performing a full reset.
        """
        try:
            scripts_and_functions.setup_zva_no_rst(self.zva_inst.get())
            text_widget.insert("1.0", "ZVA reconnected.\n")
        except Exception as e:
            print(f"Error reconnecting to ZVA: {e}")
            text_widget.insert("1.0", f"Error: {e}\n")

    def reset_signal_generator(self, text_widget: tk.Text):
        """
        Resets the signal generator.
        """
        try:
            scripts_and_functions.setup_signal_generator_pulsed_with_rst(self.signal_generator_instance.get())
            text_widget.insert("1.0", "Signal generator reset.\n")
        except Exception as e:
            print(f"Error resetting signal generator: {e}")
            text_widget.insert("1.0", f"Error: {e}\n")

    def reset_signal_generator_ramp(self, text_widget: tk.Text):
        """
                Resets the signal generator.
                """
        try:
            scripts_and_functions.configuration_sig_gen_pull_in()
            text_widget.insert("1.0", "Signal generator reset.\n")
        except Exception as e:
            print(f"Error resetting signal generator: {e}")
            text_widget.insert("1.0", f"Error: {e}\n")

    def set_symmetrical_voltage_bias(self, voltage: str):
        """
        Sets a symmetrical voltage bias on the signal generator.
        """
        try:
            v_high = float(voltage)
            v_low = -v_high
            scripts_and_functions.set_voltage_sym(v_high=v_high, v_low=v_low)
        except ValueError:
            print("Invalid voltage value.")
        except Exception as e:
            print(f"Error setting symmetrical voltage: {e}")

    def cycling_test(self):
        """
        Starts the cycling test in a new thread.
        """
        if self.is_cycling:
            print("Cycling is already in progress.")
            return

        # Clear the previous data and plots before starting a new test
        self.file_df = pd.DataFrame(
            columns=["vpullin_plus", "vpullin_minus", "vpullout_plus", "vpullout_minus", "t_on_time",
                     "insertion_loss", "t_off_time", "isolation", "cycles", "sticking events"])
        self.update_cycling_plot()

        # Create and start the cycling thread
        self.cycling_thread = threading.Thread(target=self.run_cycling_sequence_)
        self.cycling_thread.daemon = True
        self.cycling_thread.start()

    def stop_cycling_test(self):
        """
        Sets the stop_requested flag to True to interrupt the cycling test.
        """
        self.stop_requested = True
        print("Stop requested by user.")

    def run_cycling_sequence_(self):
        scripts_and_functions.cycling_sequence_with_escape_interrupt(
            self, self.new_data_event, number_of_cycles=(self.test_cycling_var_nb_cycles.get()) * 1e5,
            number_of_pulses_in_wf=1000,
            filename=r'{}-{}-{}-{}-{}-x10e5'.format(
                self.test_cycling_project.get(),
                self.test_cycling_ret.get(),
                self.test_cycling_cell.get(),
                self.test_cycling_device.get(),
                int(self.test_cycling_var_nb_cycles.get()),
                self.test_cycling_var_bias.get()), events=self.test_cycling_events.get(),
            header=r"Comment:{},frequency:10GHz".format(
                self.test_cycling_file_comment.get()),
            df_path=self.test_cycling_dir.get())

    # def run_cycling_sequence_(self):
    #     """
    #     The main sequence for the cycling test.
    #     """
    #     self.is_cycling = True
    #     self.stop_requested = False
    #     print("Cycling started.")
    #
    #     try:
    #         # Get parameters from the GUI
    #         directory = self.entered_cycling_dir.get()
    #         project = self.entered_var_cycling_project.get()
    #         cell = self.entered_var_cycling_cell.get()
    #         reticule = self.entered_cycling_ret.get()
    #         device = self.entered_cycling_device.get()
    #         comment = self.entered_file_name.get()
    #         num_cycles_10_5 = self.entered_cycling_var_bias.get()
    #
    #         # Create filename
    #         filename = f"{project}-{cell}-{reticule}-{device}-{comment}-{num_cycles_10_5}e5.txt"
    #         filepath = os.path.join(directory, filename)
    #
    #         # Write header to file
    #         with open(filepath, 'w') as f:
    #             f.write("vpullin_plus\tvpullin_minus\tvpullout_plus\tvpullout_minus\tt_on_time\t"
    #                     "insertion_loss\tt_off_time\tisolation\tcycles\tsticking_events\n")
    #
    #         # Main cycling loop
    #         while not self.stop_requested:
    #             # Perform one cycle of measurements
    #             data_row = self.perform_cycling_measurement()
    #             if data_row:
    #                 # Append data to file
    #                 with open(filepath, 'a') as f:
    #                     f.write('\t'.join(map(str, data_row.values())) + '\n')
    #
    #                 # Update the main DataFrame and signal for plot update
    #                 new_df = pd.DataFrame([data_row])
    #                 self.file_df = pd.concat([self.file_df, new_df], ignore_index=True)
    #                 self.new_data_event.set()
    #
    #             # Wait for the next cycle or check for stop request
    #             time.sleep(self.update_interval / 1000)
    #
    #     except Exception as e:
    #         print(f"An error occurred during cycling: {e}")
    #     finally:
    #         self.is_cycling = False
    #         print("Cycling stopped.")

    def perform_cycling_measurement(self):
        """
        Performs a single set of measurements for one cycling point.
        This is a placeholder for the actual measurement logic.
        """
        # This function should contain the logic to get:
        # vpullin_plus, vpullin_minus, vpullout_plus, vpullout_minus,
        # t_on_time, insertion_loss, t_off_time, isolation,
        # cycles, sticking_events
        #
        # For now, it returns random data for demonstration.
        data = {
            "vpullin_plus": np.random.uniform(20, 25),
            "vpullin_minus": np.random.uniform(-25, -20),
            "vpullout_plus": np.random.uniform(10, 15),
            "vpullout_minus": np.random.uniform(-15, -10),
            "t_on_time": np.random.uniform(1e-6, 5e-6),
            "insertion_loss": np.random.uniform(0.5, 1.5),
            "t_off_time": np.random.uniform(1e-6, 5e-6),
            "isolation": np.random.uniform(20, 30),
            "cycles": self.file_df['cycles'].max() + 1000 if not self.file_df.empty else 1000,
            "sticking_events": 0
        }
        return data

    def run_new_data_event(self):
        """
        Periodically checks for new data and updates the plot.
        """
        while True:
            if self.new_data_event.wait(timeout=1):
                self.new_data_event.clear()
                self.update_cycling_plot()
            if self.new_data_event_power_sweep.wait(timeout=1):
                self.new_data_event_power_sweep.clear()
                self.update_power_sweep_plot()

    def update_cycling_plot(self):
        """
        Updates the cycling plot with the latest data from self.file_df.
        """
        if self.file_df.empty:
            return

        # Clear previous plots
        self.ax_cycling_pull_in.clear()
        self.ax_cycling_pull_out.clear()
        self.ax_cycling_isolation.clear()
        self.ax_cycling_insertion_loss.clear()
        self.ax_cycling_t_down.clear()
        self.ax_cycling_t_up.clear()

        # Plot updated data
        self.file_df.plot(x='cycles', y='vpullin_plus', ax=self.ax_cycling_pull_in, label='Vpullin+')
        self.file_df.plot(x='cycles', y='vpullin_minus', ax=self.ax_cycling_pull_in, label='Vpullin-')

        self.file_df.plot(x='cycles', y='vpullout_plus', ax=self.ax_cycling_pull_out, label='Vpullout+')
        self.file_df.plot(x='cycles', y='vpullout_minus', ax=self.ax_cycling_pull_out, label='Vpullout-')

        self.file_df.plot(x='cycles', y='isolation', ax=self.ax_cycling_isolation)
        self.file_df.plot(x='cycles', y='insertion_loss', ax=self.ax_cycling_insertion_loss)
        self.file_df.plot(x='cycles', y='t_off_time', ax=self.ax_cycling_t_down)
        self.file_df.plot(x='cycles', y='t_on_time', ax=self.ax_cycling_t_up)
        for axes in self.fig_cycling.axes:
            axes.set_xscale('log')
            axes.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))
            axes.grid('both')

        # Redraw canvas
        self.canvas_cycling.draw()

    def start_power_test_sequence(self, *args, **kwargs):
        """
        Starts the power test sequence in a new thread.
        """
        if self.is_power_sweeping:
            print("Power sweeping is already in progress.")
            return

        # Create and start the power sweeping thread
        self.power_sweep_thread = threading.Thread(target=self.run_power_sweep_sequence, args=args, kwargs=kwargs)
        self.power_sweep_thread.daemon = True
        self.power_sweep_thread.start()

    def run_power_sweep_sequence(self, *args, **kwargs):
        """
        The main sequence for the power sweep test.
        """
        self.is_power_sweeping = True
        self.stop_requested = False
        print("Power sweep started.")

        try:
            # This is where the actual power sweep logic from scripts_and_functions would be called.
            # For now, we simulate it.
            start = kwargs.get('start', -20)
            stop = kwargs.get('stop', 10)
            step = kwargs.get('step', 1)

            for power_in in np.arange(start, stop + step, step):
                if self.stop_requested:
                    break
                # Simulate measurement
                power_out = power_in - np.random.uniform(0.5, 1.5)  # Simulate some loss
                data_row = {'Power Input DUT Avg (dBm)': power_in, 'Power Output DUT Avg (dBm)': power_out}

                # Update DataFrame and signal for plot update
                new_df = pd.DataFrame([data_row])
                self.file_power_sweep = pd.concat([self.file_power_sweep, new_df], ignore_index=True)
                self.new_data_event_power_sweep.set()
                time.sleep(0.5)

        except Exception as e:
            print(f"An error occurred during power sweep: {e}")
        finally:
            self.is_power_sweeping = False
            print("Power sweep stopped.")

    def update_power_sweep_plot(self):
        """
        Updates the power sweep plot with the latest data.
        """
        if self.file_power_sweep.empty:
            return

        self.ax_power_meas.clear()
        self.file_power_sweep.plot(x='Power Input DUT Avg (dBm)', y='Power Output DUT Avg (dBm)', ax=self.ax_power_meas)
        self.fig_power_meas.canvas.draw_idle()

    def send_trig_osc(self):
        scripts_and_functions.force_trigger_osc()
        print("Sending oscilloscope trigger", end="\n-------------------------------------------------------------\n")

    def send_trig_sig_gen(self):
        scripts_and_functions.send_trig()
        print("Sending Signal generator trigger",
              end="\n-------------------------------------------------------------\n", )

    def setup_oscilloscope_pull_in_test(self):
        scripts_and_functions.osc_pullin_config()
        print("Loading Oscilloscope Pull in voltage measurement Configuration",
              end="\n-------------------------------------------------------------\n", )

    def setup_rf_gen_pull_in_setup(self):
        scripts_and_functions.rf_gen_pull_in_setup()
        print("Loading RF generator Pull in voltage measurement Configuration",
              end="\n-------------------------------------------------------------\n", )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SUMMIT 11K Machine Interface")
    parser.add_argument('--offline', action='store_true', help='Run in offline mode without connecting to hardware.')
    args = parser.parse_args()
    # Create the main window
    root = ttk.Window(themename=default_style)
    app = Window(root, offline_mode=False)
    # app = Window(root, offline_mode=args.offline)
    root.mainloop()
