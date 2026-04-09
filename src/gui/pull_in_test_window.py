from __future__ import annotations

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import scrolledtext
from src.core import scripts_and_functions
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from typing import Optional, Literal, TYPE_CHECKING
from src.gui.gui_utils import add_label_frame, add_button, add_label, add_entry, create_canvas, \
    file_name_creation, browse_directory, \
    close_resources, tab_pad_x


class PullInTestWindow(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()
        self.text_pull_out_plus_test: tk.Text
        self.text_pull_in_plus_test: tk.Text

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        tab_pad_x = 5
        tab_pad_y = 5
        # This TAB is for Pull down voltage vs isolation measurement
        frame_test_pull_in_comp_info = add_label_frame(self, frame_name='Component information', col=0,
                                                       row=0)
        frame_test_pull_in_signal_generator = add_label_frame(self, frame_name='Signal Generator',
                                                              col=0,
                                                              row=1)
        frame_test_pull_in_gen_controls = add_label_frame(self, frame_name='General controls',
                                                          col=2,
                                                          row=0)
        frame_osc_pull_in_test = add_label_frame(self, frame_name='Oscilloscope Tecktronix',
                                                 col=1, row=0, row_span=3, sticky="nsew")
        frame_test_pull_in_measurement = add_label_frame(self, frame_name='Measurement', col=2,
                                                         row=1,
                                                         row_span=2)
        frame_test_measurement = ttk.Frame(frame_test_pull_in_measurement)
        frame_oscilloscope = add_label_frame(self, frame_name='Oscilloscope & RF Gen', col=0, row=2,
                                             row_span=1)

        frame_test_pull_in_comp_info.grid_columnconfigure(2, weight=1)
        frame_oscilloscope.grid_columnconfigure(0, weight=1)
        frame_test_pull_in_gen_controls.grid_columnconfigure(0, weight=1)
        frame_test_pull_in_gen_controls.grid_columnconfigure(1, weight=1)

        # Adding labels to component info Labelframe
        add_label(frame_test_pull_in_comp_info, label_name='DIR', col=0, row=0)
        add_label(frame_test_pull_in_comp_info, label_name='Project', col=0, row=1)
        add_label(frame_test_pull_in_comp_info, label_name='Cell', col=0, row=2)
        add_label(frame_test_pull_in_comp_info, label_name='Reticule', col=0, row=3)
        add_label(frame_test_pull_in_comp_info, label_name='Device', col=0, row=4)
        add_label(frame_test_pull_in_comp_info, label_name='Bias Voltage', col=0, row=5)
        # Variables for the TAB
        self.test_pull_in_dir = tk.StringVar(
            value=self.app.pull_in_dir_name.get())
        self.test_pull_in_project = tk.StringVar(value=r'Project_Name')
        self.test_pull_in_cell = tk.StringVar(value=r'Cell_Name')
        self.test_pull_in_reticule = tk.StringVar(value=r'Reticule')
        self.test_pull_in_device = tk.StringVar(value=r'Device_name')
        self.test_pull_in_file_created = tk.StringVar(value=r'EMPTY')
        self.test_pull_in_bias_voltage = tk.StringVar(value=r'Bias_Voltage')

        self.app.test_pull_in_dir = add_entry(tab=frame_test_pull_in_comp_info,
                                              text_var=self.test_pull_in_dir, width=20, col=1, row=0)
        add_button(frame_test_pull_in_comp_info, "Browse", lambda: browse_directory(self.test_pull_in_dir), col=2, row=0)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_project, width=20, col=1, row=1)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_cell, width=20, col=1, row=2)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_reticule, width=20, col=1, row=3)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_device, width=20, col=1, row=4)
        add_entry(tab=frame_test_pull_in_comp_info, text_var=self.test_pull_in_bias_voltage, width=20, col=1, row=5)

        # Adding entry for file directory

        # Signal Generator Labelframe
        frame_signal_gen_measurement = ttk.Frame(frame_test_pull_in_signal_generator)
        frame_signal_gen_measurement.pack()

        self.pull_in_v_bias = tk.DoubleVar(value=10)  # Peak bias voltage for ramp function
        self.ramp_width = tk.DoubleVar(value=100)  # Ramp length for ramp function
        self.chosen_bias_voltage_pull_in = add_entry(tab=frame_test_pull_in_comp_info, text_var=self.pull_in_v_bias,
                                                     width=20, col=1, row=5)
        add_label(frame_signal_gen_measurement, label_name='Bias Voltage', col=0, row=0)
        add_label(frame_signal_gen_measurement, label_name='Ramp length', col=0, row=1)
        self.entered_ramp_volt = add_entry(frame_signal_gen_measurement, text_var=self.pull_in_v_bias, width=10,
                                           col=1,
                                           row=0)
        self.txt_file_name_meas_combobox = tk.StringVar(value=r'test')

        add_button(tab=frame_test_pull_in_comp_info, button_name='Create-file',
                   command=lambda: [file_name_creation(data_list=[self.test_pull_in_project.get(),
                                                                  self.test_pull_in_cell.get(),
                                                                  self.test_pull_in_reticule.get(),
                                                                  self.test_pull_in_device.get(),
                                                                  self.entered_ramp_volt.get()],
                                                       text=self.text_file_name_pull_in_test, end_characters='V')],
                   col=3, row=0)
        add_button(tab=frame_test_pull_in_comp_info,
                   button_name='Send trigger',
                   command=lambda: [self.app.send_trig_sig_gen()], col=3, row=1)
        add_button(tab=frame_test_pull_in_comp_info,
                   button_name='Osc trigger',
                   command=lambda: [self.app.send_trig_osc()], col=3, row=2)

        self.entered_ramp_width = add_entry(frame_signal_gen_measurement, text_var=self.ramp_width, width=10, col=1,
                                            row=1)
        add_label(frame_signal_gen_measurement, label_name='(V)', col=2, row=0)
        add_label(frame_signal_gen_measurement, label_name='(µs)', col=2, row=1)
        add_button(tab=frame_signal_gen_measurement, button_name='Set Bias Voltage',
                   command=lambda: self.app.set_bias_pull_in(self.pull_in_v_bias.get()),
                   col=3, row=0)
        add_button(tab=frame_signal_gen_measurement, button_name='Set Ramp Width',
                   command=lambda: self.app.set_ramp_width(self.ramp_width.get()),
                   col=3,
                   row=1)
        add_button(tab=frame_signal_gen_measurement, button_name='Set Pulse Gen',
                   command=lambda: self.app.set_pulse_gen_ramp_and_bias(self.pull_in_v_bias.get(),
                                                                        self.ramp_width.get()),
                   col=3, row=3)
        # Oscilloscope
        add_button(tab=frame_oscilloscope, button_name='Setup Oscilloscope',
                   command=lambda: self.app.setup_oscilloscope_pull_in_test(),
                   col=0, row=0)
        add_button(tab=frame_oscilloscope, button_name='Setup RF Gen',
                   command=lambda: self.app.setup_rf_gen_pull_in_setup(),
                   col=0, row=1)
        # General controls Labelframe
        self.text_file_name_pull_in_test = tk.Text(frame_test_pull_in_gen_controls, width=40, height=1,
                                                   wrap=tk.WORD,
                                                   border=4, borderwidth=2,
                                                   relief=tk.SUNKEN, font=('Bahnschrift Light', 10))  # Filename
        self.text_file_name_pull_in_test.grid(column=0, row=0, sticky='n', columnspan=5)
        self.text_gen_controls_pull_in_debug = tk.Text(frame_test_pull_in_gen_controls, width=40, height=10,
                                                       wrap=tk.WORD, border=4,
                                                       borderwidth=2, relief=tk.SUNKEN,
                                                       font=('Bahnschrift Light', 10))
        # Debug text_file_name_s3p_test display
        self.text_gen_controls_pull_in_debug.grid(column=0, row=3, sticky='n', columnspan=4)

        add_button(tab=frame_test_pull_in_gen_controls, button_name='Reset Signal Generator',
                   command=lambda: [
                       self.app.reset_signal_generator_ramp(text_widget=self.text_gen_controls_pull_in_debug)], col=0,
                   row=1)
        add_button(tab=frame_test_pull_in_gen_controls, button_name='Exit', command=self.app._quit,
                   col=1,
                   row=1)
        add_button(tab=frame_test_pull_in_gen_controls, button_name='Iso vs V',
                   command=lambda: [file_name_creation([self.test_pull_in_project.get(),
                                                        self.test_pull_in_cell.get(),
                                                        self.test_pull_in_reticule.get(),
                                                        self.test_pull_in_device.get(),
                                                        self.entered_ramp_volt.get()],
                                                       text=self.text_file_name_pull_in_test, end_characters='V'),
                                    self.app.acquire_pull_down_data(
                                        filename=self.text_file_name_pull_in_test.get("1.0", "end-1c"),
                                        text_widget=self.text_gen_controls_pull_in_debug),
                                    self.app.trace_pull_down(
                                        filename=self.text_file_name_pull_in_test.get("1.0", "end-1c"))],
                   col=1,
                   row=5)
        # -------------------------------------------------------------------------------------------------------------
        self.canvas_v_pull_in_meas = create_canvas(figure=self.app.fig_pull_in_meas,
                                                   frame=frame_osc_pull_in_test,
                                                   toolbar_frame=frame_osc_pull_in_test, toolbar=True,
                                                   toolbar_side=tk.BOTTOM, canvas_side=tk.TOP)

        add_label(frame_test_measurement,
                  label_name='Positive-Pull-in', col=0, row=0)
        self.text_pull_in_plus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                              border=4, borderwidth=2,
                                              relief=tk.SUNKEN, font=('Bahnschrift Light', 10))  # Positive Pull-in
        self.text_pull_in_plus_test.grid(column=1, row=0, sticky='n', columnspan=5)

        add_label(frame_test_measurement,
                  label_name='Negative-Pull-in', col=0, row=1)
        self.text_pull_in_minus_test = tk.Text(frame_test_measurement, width=15,
                                               height=1, wrap=tk.WORD, border=4, borderwidth=2, relief=tk.SUNKEN,
                                               font=('Bahnschrift Light', 10))  # Negative Pull-in
        self.text_pull_in_minus_test.grid(column=1, row=1, sticky='n', columnspan=5)

        add_label(frame_test_measurement,
                  label_name='Positive-Pull-out', col=0, row=2)
        self.text_pull_out_plus_test = tk.Text(frame_test_measurement,
                                               width=15, height=1, wrap=tk.WORD, border=4,
                                               borderwidth=2, relief=tk.SUNKEN,
                                               font=('Bahnschrift Light', 10))  # Positive Pull-out
        self.text_pull_out_plus_test.grid(column=1, row=2, sticky='n', columnspan=5)

        add_label(frame_test_measurement, label_name='Negative-Pull-out', col=0, row=3)
        self.text_pull_out_minus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                border=4, borderwidth=2,
                                                relief=tk.SUNKEN,
                                                font=('Bahnschrift Light', 10))  # Negative Pull-out
        self.text_pull_out_minus_test.grid(column=1, row=3, sticky='n', columnspan=5)

        add_label(frame_test_measurement, label_name='Isolation at PI(+)', col=0, row=4)

        self.text_iso_pull_in_plus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                  border=4, borderwidth=2,
                                                  relief=tk.SUNKEN,
                                                  font=('Bahnschrift Light', 10))  # Isolation at PI (+)
        self.text_iso_pull_in_plus_test.grid(column=1, row=4, sticky='n', columnspan=5)

        add_label(frame_test_measurement, label_name='Isolation at PI (-)', col=0, row=6)
        self.text_iso_pull_in_minus_test = tk.Text(frame_test_measurement, width=15, height=1, wrap=tk.WORD,
                                                   border=4,
                                                   borderwidth=2, relief=tk.SUNKEN,
                                                   font=('Bahnschrift Light', 10))  # Isolation at PI (-)
        self.text_iso_pull_in_minus_test.grid(column=1, row=6, sticky='n', columnspan=5)

        frame_test_measurement.pack(fill='both')
