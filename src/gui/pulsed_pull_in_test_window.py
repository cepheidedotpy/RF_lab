from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from src.core import scripts_and_functions
from typing import TYPE_CHECKING

# if TYPE_CHECKING:
# from main_refactored import Window
from .gui_utils import add_label_frame, add_button, add_label, add_entry, create_canvas, file_name_creation, tab_pad_x


class PulsedPullInTestWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)
        master.grid_rowconfigure(2, weight=1)
        master.grid_columnconfigure(1, weight=1)

        # This TAB is for Pull down voltage vs isolation measurement
        frame_test_pulsed_pull_in_comp_info = add_label_frame(master,
                                                              frame_name='Component information', col=0,
                                                              row=0)
        frame_test_pulsed_pull_in_signal_generator = add_label_frame(tab=master,
                                                                     frame_name='Signal Generator',
                                                                     col=0,
                                                                     row=1)
        frame_test_pulsed_pull_in_gen_controls = add_label_frame(tab=master,
                                                                 frame_name='General controls',
                                                                 col=2,
                                                                 row=0)
        frame_test_pulsed_osc_pull_in = add_label_frame(tab=master,
                                                        frame_name='Oscilloscope Tecktronix',
                                                        col=1, row=0, row_span=3, sticky="nsew")
        frame_test_pulsed_pull_in_measurement = add_label_frame(tab=master,
                                                                frame_name='Measurement', col=2,
                                                                row=1,
                                                                row_span=2)
        frame_pulsed_test_measurement = ttk.Frame(frame_test_pulsed_pull_in_measurement)
        frame_test_pulsed_pull_in_oscilloscope = add_label_frame(tab=master,
                                                                 frame_name='Oscilloscope & RF Gen', col=0,
                                                                 row=2,
                                                                 row_span=1)
        frame_test_pulsed_pull_in_comp_info.grid_columnconfigure(2, weight=1)
        # frame_pulsed_signal_gen_measurement.grid_columnconfigure(3, weight=1)
        frame_test_pulsed_pull_in_oscilloscope.grid_columnconfigure(0, weight=1)
        frame_test_pulsed_pull_in_gen_controls.grid_columnconfigure(0, weight=1)
        frame_test_pulsed_pull_in_gen_controls.grid_columnconfigure(1, weight=1)
        # Adding labels to component info Labelframe
        add_label(frame_test_pulsed_pull_in_comp_info, label_name='DIR', col=0, row=0).grid(sticky='e',

                                                                                            ipadx=tab_pad_x,
                                                                                            ipady=tab_pad_x)
        add_label(frame_test_pulsed_pull_in_comp_info, label_name='Project', col=0, row=1).grid(sticky='e',
                                                                                                ipadx=tab_pad_x,
                                                                                                ipady=tab_pad_x)
        add_label(frame_test_pulsed_pull_in_comp_info, label_name='Cell', col=0, row=2).grid(sticky='e',
                                                                                             ipadx=tab_pad_x,
                                                                                             ipady=tab_pad_x)
        add_label(frame_test_pulsed_pull_in_comp_info, label_name='Reticule', col=0, row=3).grid(sticky='e',
                                                                                                 ipadx=tab_pad_x,
                                                                                                 ipady=tab_pad_x)
        add_label(frame_test_pulsed_pull_in_comp_info, label_name='Device', col=0, row=4).grid(sticky='e',
                                                                                               ipadx=tab_pad_x,
                                                                                               ipady=tab_pad_x)
        add_label(frame_test_pulsed_pull_in_comp_info, label_name='Bias Voltage', col=0, row=5).grid(sticky='e',
                                                                                                     ipadx=tab_pad_x,
                                                                                                     ipady=tab_pad_x)
        self.app.test_pulsed_pull_in_dir = tk.StringVar(
            value=r'C:\Users\TEMIS\PycharmProjects\pythonProject\venv\TEMIS MEMS LAB\dummy_data')
        self.app.test_pulsed_pull_in_project = tk.StringVar(value=r'Project_Name')
        self.app.test_pulsed_pull_in_cell = tk.StringVar(value=r'Cell_Name')
        self.app.test_pulsed_pull_in_reticule = tk.StringVar(value=r'Reticule')
        self.app.test_pulsed_pull_in_device = tk.StringVar(value=r'Device_name')
        self.app.test_pulsed_pull_in_file_created = tk.StringVar(value=r'EMPTY')
        self.app.test_pulsed_pull_in_bias_voltage = tk.StringVar(value=r'Bias_Voltage')

        add_entry(tab=frame_test_pulsed_pull_in_comp_info, text_var=self.app.test_pulsed_pull_in_dir, width=20, col=1,
                  row=0)
        add_entry(tab=frame_test_pulsed_pull_in_comp_info, text_var=self.app.test_pulsed_pull_in_project, width=20,
                  col=1,
                  row=1)
        add_entry(tab=frame_test_pulsed_pull_in_comp_info, text_var=self.app.test_pulsed_pull_in_cell, width=20, col=1,
                  row=2)
        add_entry(tab=frame_test_pulsed_pull_in_comp_info, text_var=self.app.test_pulsed_pull_in_reticule, width=20,
                  col=1,
                  row=3)
        add_entry(tab=frame_test_pulsed_pull_in_comp_info, text_var=self.app.test_pulsed_pull_in_device, width=20,
                  col=1,
                  row=4)
        add_entry(tab=frame_test_pulsed_pull_in_comp_info, text_var=self.app.test_pulsed_pull_in_bias_voltage, width=20,
                  col=1,
                  row=5)

        # Signal Generator Labelframe
        frame_pulsed_signal_gen_measurement = ttk.Frame(frame_test_pulsed_pull_in_signal_generator)
        frame_pulsed_signal_gen_measurement.pack()
        self.app.pulsed_pulse_width = tk.DoubleVar(value=100)  # Ramp length for ramp function

        self.app.entered_pulsed_pulse_width = add_entry(frame_pulsed_signal_gen_measurement,
                                                        text_var=self.app.pulsed_pulse_width, width=10, col=1,
                                                        row=1)
        self.app.pulsed_pull_in_v_bias = tk.DoubleVar(value=10)  # Peak bias voltage for ramp function
        self.app.pulsed_chosen_bias_voltage_pull_in = add_entry(tab=frame_test_pulsed_pull_in_comp_info,
                                                                text_var=self.app.pulsed_pull_in_v_bias,
                                                                width=20, col=1, row=5)
        add_label(frame_pulsed_signal_gen_measurement, label_name='Bias Voltage', col=0, row=0).grid(sticky='e',
                                                                                                     ipadx=tab_pad_x,
                                                                                                     ipady=tab_pad_x)
        add_label(frame_pulsed_signal_gen_measurement, label_name='Ramp length', col=0, row=1).grid(sticky='e',
                                                                                                    ipadx=tab_pad_x,
                                                                                                    ipady=tab_pad_x)
        self.app.entered_pulsed_pull_in_v_bias = add_entry(frame_pulsed_signal_gen_measurement,
                                                           text_var=self.app.pulsed_pull_in_v_bias,
                                                           width=10,
                                                           col=1,
                                                           row=0)
        # self.app.text_pulsed_file_name_pull_in_test = tk.StringVar(value=r'test')

        add_button(tab=frame_test_pulsed_pull_in_comp_info, button_name='Create-file',
                   command=lambda: [file_name_creation(data_list=[self.app.test_pulsed_pull_in_project.get(),
                                                                  self.app.test_pulsed_pull_in_cell.get(),
                                                                  self.app.test_pulsed_pull_in_reticule.get(),
                                                                  self.app.test_pulsed_pull_in_device.get(),
                                                                  self.app.entered_pulsed_pull_in_v_bias.get()],
                                                       text=self.app.text_pulsed_file_name_pull_in_test,
                                                       end_characters='V')],
                   col=2, row=0)
        add_button(tab=frame_test_pulsed_pull_in_comp_info,
                   button_name='Send trigger',
                   command=lambda: [scripts_and_functions.send_trig()], col=2, row=1)
        add_button(tab=frame_test_pulsed_pull_in_comp_info,
                   button_name='Osc trigger',
                   command=lambda: [scripts_and_functions.force_trigger_osc()], col=2, row=2)

        add_label(frame_pulsed_signal_gen_measurement, label_name='(V)', col=2, row=0).grid(sticky='w',
                                                                                            ipadx=tab_pad_x,
                                                                                            ipady=tab_pad_x)
        add_label(frame_pulsed_signal_gen_measurement, label_name='(µs)', col=2, row=1).grid(sticky='w',
                                                                                             ipadx=tab_pad_x,
                                                                                             ipady=tab_pad_x)
        add_button(tab=frame_pulsed_signal_gen_measurement, button_name='Set Bias Voltage',
                   command=lambda: [scripts_and_functions.create_pulsed_pull_in_test_waveform(
                       amplitude=int(self.app.entered_pulsed_pull_in_v_bias.get()),
                       pulse_width=int(self.app.pulsed_pulse_width.get()))],
                   col=3, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_pulsed_signal_gen_measurement, button_name='Set Ramp Width',
                   command=lambda: [scripts_and_functions.create_pulsed_pull_in_test_waveform(
                       amplitude=int(self.app.entered_pulsed_pull_in_v_bias.get()),
                       pulse_width=int(self.app.pulsed_pulse_width.get()))],
                   col=3,
                   row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_pulsed_signal_gen_measurement, button_name='Set Pulse Gen',
                   command=None,
                   col=3, row=3).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        # Oscilloscope
        add_button(tab=frame_test_pulsed_pull_in_oscilloscope, button_name='Setup Oscilloscope',
                   command=lambda: scripts_and_functions.osc_pullin_config(),
                   col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_test_pulsed_pull_in_oscilloscope, button_name='Setup RF Gen',
                   command=lambda: scripts_and_functions.rf_gen_pull_in_setup(),
                   col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        # General controls Labelframe
        self.app.text_pulsed_file_name_pull_in_test = tk.Text(frame_test_pulsed_pull_in_gen_controls, width=40,
                                                              height=1,
                                                              wrap=tk.WORD,
                                                              border=4, borderwidth=2,
                                                              relief=tk.SUNKEN,
                                                              font=('Bahnschrift Light', 10))  # Filename
        self.app.text_pulsed_file_name_pull_in_test.grid(column=0, row=0, sticky='n', columnspan=5)
        self.app.text_gen_controls_pull_in_debug = tk.Text(frame_test_pulsed_pull_in_gen_controls, width=40, height=10,
                                                           wrap=tk.WORD, border=4,
                                                           borderwidth=2, relief=tk.SUNKEN,
                                                           font=('Bahnschrift Light', 10))
        # Debug text_file_name_s3p_test display
        self.app.text_gen_controls_pull_in_debug.grid(column=0, row=3, sticky='n', columnspan=4)

        add_button(tab=frame_test_pulsed_pull_in_gen_controls, button_name='Reset Signal Generator',
                   command=lambda: [scripts_and_functions.create_pulsed_pull_in_test_waveform(
                       amplitude=int(self.app.entered_pulsed_pull_in_v_bias.get()),
                       pulse_width=int(self.app.pulsed_pulse_width.get()))], col=0, row=1).grid(ipadx=tab_pad_x,
                                                                                                ipady=tab_pad_x)
        add_button(tab=frame_test_pulsed_pull_in_gen_controls, button_name='Exit', command=lambda: [self.app._quit(),
                                                                                                    self.app.close_resources()],
                   col=1,
                   row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_test_pulsed_pull_in_gen_controls, button_name='Iso vs V',
                   command=lambda: [self.app.acquire_pull_down_data_pulsed(
                       filename=file_name_creation([
                           self.app.test_pulsed_pull_in_project.get(),
                           self.app.test_pulsed_pull_in_cell.get(),
                           self.app.test_pulsed_pull_in_reticule.get(),
                           self.app.test_pulsed_pull_in_device.get(),
                           str(int(self.app.entered_pulsed_pull_in_v_bias.get()))], end_characters='V',
                           text=self.app.text_pulsed_file_name_pull_in_test)), self.app.trace_pull_in_pulsed()], col=1,
                   row=5).grid(
            ipadx=tab_pad_x, ipady=tab_pad_x)
        # -------------------------------------------------------------------------------------------------------------
        self.app.canvas_v_pull_in_meas_pulsed = create_canvas(figure=self.app.fig_pulsed_pull_in_meas,
                                                              frame=frame_test_pulsed_osc_pull_in,
                                                              toolbar_frame=frame_test_pulsed_osc_pull_in,
                                                              toolbar=True, toolbar_side=tk.BOTTOM, canvas_side=tk.TOP)
