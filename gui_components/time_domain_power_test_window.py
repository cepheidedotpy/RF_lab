# gui_components/time_domain_power_test_window.py

from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk
import os
import time
import pandas as pd
from typing import Optional, TYPE_CHECKING
import scripts_and_functions
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from .gui_utils import add_label_frame, add_button, add_label, add_entry, add_combobox, create_canvas, \
    file_name_creation, close_resources, tab_pad_x, default_style


class TimeDomainPowerTestWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()

    def acquire_and_plot_traces(self):
        """
        Acquires power meter traces and plots them on the GUI.
        """
        try:
            # Acquire trace data
            trace_a, trace_b = scripts_and_functions.powermeter_trace_acquisition_sequence()

            # Get trace duration from the GUI
            trace_duration = self.trace_duration.get()

            # Clear the axes
            self.app.ax_time_domain_power_meas_input.clear()
            self.app.ax_time_domain_power_meas_output.clear()

            # Create time axes
            time_axis_a = np.linspace(0, trace_duration, len(trace_a))
            time_axis_b = np.linspace(0, trace_duration, len(trace_b))

            # Plot the data
            self.app.ax_time_domain_power_meas_input.plot(time_axis_a, trace_a, label="Input Pulse (A)")
            self.app.ax_time_domain_power_meas_output.plot(time_axis_b, trace_b, label="Output Pulse (B)")

            # Set plot labels and titles
            self.app.ax_time_domain_power_meas_input.set(xlabel="Time (s)", ylabel="Power (dBm)",
                                                         title="Input Pulse")
            self.app.ax_time_domain_power_meas_output.set(xlabel="Time (s)", ylabel="Power (dBm)",
                                                          title="Output Pulse")
            self.app.ax_time_domain_power_meas_input.grid(True)
            self.app.ax_time_domain_power_meas_output.grid(True)
            self.app.ax_time_domain_power_meas_input.legend()
            self.app.ax_time_domain_power_meas_output.legend()

            # Redraw the canvas
            self.app.fig_time_domain_power_meas.canvas.draw_idle()

        except Exception as e:
            print(f"Error acquiring and plotting traces: {e}")
            # Optionally, show an error message in the GUI
            self.text_power_debug.insert(tk.END, f"Error: {e}\n")

    def clear_traces(self):
        """
        Clears the power meter trace plots.
        """
        self.app.ax_time_domain_power_meas_input.clear()
        self.app.ax_time_domain_power_meas_output.clear()
        self.app.ax_time_domain_power_meas_input.set(xlabel="Time (s)", ylabel="Power (dBm)",
                                                     title="Input Pulse")
        self.app.ax_time_domain_power_meas_output.set(xlabel="Time (s)", ylabel="Power (dBm)",
                                                      title="Output Pulse")
        self.app.ax_time_domain_power_meas_input.grid(True)
        self.app.ax_time_domain_power_meas_output.grid(True)
        self.app.fig_time_domain_power_meas.canvas.draw_idle()

    def launch_time_domain_power_sweep(self):
        """
        Performs a power sweep in the time domain and plots the results.
        """
        try:
            min_power = self.rf_gen_min_power.get()
            max_power = self.rf_gen_max_power.get()
            step = self.rf_gen_step.get()

            # Clear plots before starting
            self.clear_traces()

            power_levels = np.arange(min_power, max_power + step, step)
            all_traces_dfs = []

            for power in power_levels:
                scripts_and_functions.set_rf_power(power)
                time.sleep(0.5)  # Wait for power to settle

                # Acquire and plot traces for the current power level
                trace_a, trace_b = scripts_and_functions.powermeter_trace_acquisition_sequence()
                trace_duration = self.trace_duration.get()
                time_axis_a = np.linspace(0, trace_duration, len(trace_a))
                time_axis_b = np.linspace(0, trace_duration, len(trace_b))

                self.app.ax_time_domain_power_meas_input.plot(time_axis_a, trace_a, label=f"Input @ {power} dBm")
                self.app.ax_time_domain_power_meas_output.plot(time_axis_b, trace_b, label=f"Output @ {power} dBm")

                # Store data for saving
                df_a = pd.DataFrame(
                    {'power_level': power, 'time': time_axis_a, 'power': trace_a, 'channel': 'A'})
                df_b = pd.DataFrame(
                    {'power_level': power, 'time': time_axis_b, 'power': trace_b, 'channel': 'B'})
                all_traces_dfs.append(df_a)
                all_traces_dfs.append(df_b)

                # Update the plot
                self.app.fig_time_domain_power_meas.canvas.draw_idle()
                self.update()  # Process GUI events

            # Add legends
            self.app.ax_time_domain_power_meas_input.legend()
            self.app.ax_time_domain_power_meas_output.legend()
            self.app.fig_time_domain_power_meas.canvas.draw_idle()

            # Save the data
            if all_traces_dfs:
                final_df = pd.concat(all_traces_dfs, ignore_index=True)
                filename = file_name_creation(data_list=[self.test_pow_project.get(), self.test_pow_cell.get(),
                                                          self.test_pow_reticule.get(),
                                                          self.test_pow_device.get()],
                                              text=self.text_power_file_name, end_characters='V_power_sweep')
                filepath = os.path.join(self.directory.get(), f"{filename}.csv")
                final_df.to_csv(filepath, index=False)
                self.text_power_debug.insert(tk.END, f"Sweep data saved to {filepath}\n")

            self.text_power_debug.insert(tk.END, "Power sweep completed.\n")

            # Reset plot after a delay
            self.after(5000, self.clear_traces)

        except Exception as e:
            error_message = f"Error during power sweep: {e}\n"
            print(error_message)
            self.text_power_debug.insert(tk.END, error_message)


    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        tab_pad_x = 5
        tab_pad_y = 5
        frame_power_compo_info = add_label_frame(self, frame_name='Component information', col=0,
                                                 row=0)
        frame_power_meas = add_label_frame(self, frame_name='General controls', col=2, row=0)
        frame_power_meas_graph = add_label_frame(self, frame_name='Time Domain Power Test Graph', col=1, row=0,
                                                 row_span=3, sticky="nsew")
        frame_power_measurement_signal_generator = add_label_frame(self,
                                                                   frame_name='Signal Generator', col=0, row=1,
                                                                   row_span=1)
        frame_power_meas_rf_gen = add_label_frame(self, frame_name='RF Generator', col=2, row=1,
                                                  row_span=2)
        frame_power_meas_powermeter = add_label_frame(self, frame_name='Powermeter', col=0, row=2,
                                                      row_span=1)
        frame_test_power_measurement = ttk.Frame(frame_power_meas_graph)
        frame_test_power_measurement.pack(anchor='nw')

        frame_power_compo_info.grid_columnconfigure(2, weight=1)
        frame_power_meas.grid_columnconfigure(1, weight=1)
        frame_power_measurement_signal_generator.grid_columnconfigure(0, weight=1)
        frame_power_meas_powermeter.grid_columnconfigure(0, weight=1)
        frame_power_meas_rf_gen.grid_columnconfigure(0, weight=1)

        add_label(frame_power_compo_info, label_name='DIR', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                               ipady=tab_pad_y)
        add_label(frame_power_compo_info, label_name='Project', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                   ipady=tab_pad_x)
        add_label(frame_power_compo_info, label_name='Cell', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                ipady=tab_pad_y)
        add_label(frame_power_compo_info, label_name='Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_y)
        add_label(frame_power_compo_info, label_name='Device', col=0, row=4).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_y)
        add_label(frame_power_compo_info, label_name='Status', col=0, row=5).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_y)
        add_label(frame_power_compo_info, label_name='Bias Voltage', col=0, row=6).grid(sticky='e', ipadx=tab_pad_x,
                                                                                        ipady=tab_pad_y)

        add_label(frame_power_meas_powermeter, label_name='Input Attenuation (A)', col=0, row=0).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_label(frame_power_meas_powermeter, label_name='Output Attenuation (B)', col=0, row=1).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_label(frame_power_meas_powermeter, label_name='(dB)', col=2, row=0).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_label(frame_power_meas_powermeter, label_name='(dB)', col=2, row=1).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)

        add_label(frame_power_meas_powermeter, label_name='Trigger Delay', col=0, row=2).grid(sticky='e',
                                                                                              ipadx=tab_pad_x,
                                                                                              ipady=tab_pad_y)
        add_label(frame_power_meas_powermeter, label_name='Trace Duration', col=0, row=3).grid(sticky='e',
                                                                                               ipadx=tab_pad_x,
                                                                                               ipady=tab_pad_y)
        add_label(frame_power_meas_powermeter, label_name='Gate Duration', col=0, row=4).grid(sticky='e',
                                                                                              ipadx=tab_pad_x,
                                                                                              ipady=tab_pad_y)

        self.trigger_delay = tk.DoubleVar(value=0)

        self.trace_duration = tk.DoubleVar(value=200e-6)

        self.gate_duration = tk.DoubleVar(value=10e-6)

        self.amplitude = tk.DoubleVar(value=20)
        self.pulse_width = tk.DoubleVar(value=100.0e-6)
        self.prf = tk.DoubleVar(value=1)

        add_entry(tab=frame_power_meas_powermeter, text_var=self.trigger_delay, width=20, col=1, row=2)

        add_label(frame_power_meas_powermeter, label_name='(s)', col=2, row=2).grid(sticky='w', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_y)

        add_entry(tab=frame_power_meas_powermeter, text_var=self.trace_duration, width=20, col=1, row=3)

        add_label(frame_power_meas_powermeter, label_name='(s)', col=2, row=3).grid(sticky='w', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_y)

        add_entry(tab=frame_power_meas_powermeter, text_var=self.gate_duration, width=20, col=1, row=4)

        add_label(frame_power_meas_powermeter, label_name='(s)', col=2, row=4).grid(sticky='w', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_y)

        add_button(tab=frame_power_meas_powermeter, button_name='Set Time Domain Window',

                   command=lambda: scripts_and_functions.set_time_domain_window(

                       trigger_delay=self.trigger_delay.get(),

                       trace_duration=self.trace_duration.get(),

                       gate_duration=self.gate_duration.get()

                   ), col=0, row=6).grid()
        add_button(tab=frame_power_meas_powermeter,
                   button_name='Set Measurement Window',
                   command=lambda: [scripts_and_functions.define_powermeter_settings(
                       trigger_delay=self.trigger_delay.get(),
                       trace_duration=self.trace_duration.get(),
                       gate_duration=self.gate_duration.get(),
                       power_unit="DBM"
                   )], col=1, row=6).grid()

        self.directory = tk.StringVar(
            value=r'C:\Users\TEMIS\PycharmProjects\pythonProject\venv\TEMIS MEMS LAB\dummy_data')
        self.test_pow_project = tk.StringVar(value=r'Project_Name')
        self.test_pow_cell = tk.StringVar(value=r'Cell_Name')
        self.test_pow_reticule = tk.StringVar(value=r'Reticule')
        self.test_pow_device = tk.StringVar(value=r'Device_name')
        self.test_pow_file_created = tk.StringVar(value=r'EMPTY')
        self.test_pow_state = tk.StringVar(value=r'EMPTY')
        self.bias_voltage_pow = tk.StringVar(value=r'Bias_Voltage')
        self.test_pow_input_atten = tk.DoubleVar(value=0)
        self.test_pow_output_atten = tk.DoubleVar(value=0)

        self.chosen_component_state_pow = add_combobox(frame_power_compo_info, text=self.test_pow_state, col=1,
                                                       row=5,
                                                       width=20)
        self.chosen_component_state_pow['values'] = ('Active', 'Frozen')
        self.chosen_component_state_pow.current(0)

        add_entry(tab=frame_power_compo_info, text_var=self.directory, width=20, col=1, row=0)
        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_project, width=20, col=1, row=1)
        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_cell, width=20, col=1, row=2)
        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_reticule, width=20, col=1, row=3)
        add_entry(tab=frame_power_compo_info, text_var=self.test_pow_device, width=20, col=1, row=4)
        add_entry(tab=frame_power_compo_info, text_var=self.bias_voltage_pow, width=20, col=1, row=6)

        add_entry(tab=frame_power_meas_powermeter, text_var=self.test_pow_input_atten, width=20, col=1, row=0)
        add_entry(tab=frame_power_meas_powermeter, text_var=self.test_pow_output_atten, width=20, col=1, row=1)

        self.power_test_file_name = tk.StringVar(value=r'test')

        add_button(tab=frame_power_compo_info, button_name='Create-file',
                   command=lambda: [
                       file_name_creation(data_list=[self.test_pow_project.get(), self.test_pow_cell.get(),
                                                     self.test_pow_reticule.get(),
                                                     self.test_pow_device.get(),
                                                     self.chosen_component_state_pow.get(),
                                                     self.bias_voltage_pow.get()],
                                          text=self.text_power_file_name, end_characters='V')],
                   col=2, row=0)
        add_button(tab=frame_power_compo_info, button_name='Send trigger', command=scripts_and_functions.send_trig,
                   col=2, row=1)
        add_button(tab=frame_power_compo_info, button_name='Osc trigger',
                   command=lambda: [scripts_and_functions.force_trigger_osc()],
                   col=2, row=2)

        # General controls---------------------------------------------------------------

        self.rf_gen_min_power = tk.DoubleVar(value=-20)
        self.rf_gen_max_power = tk.DoubleVar(value=-10)
        self.rf_gen_step = tk.DoubleVar(value=1)
        rf_gen_frequency = tk.DoubleVar(value=10)
        add_entry(tab=frame_power_meas_rf_gen, text_var=self.rf_gen_min_power, width=20, col=1, row=0)
        add_entry(tab=frame_power_meas_rf_gen, text_var=self.rf_gen_max_power, width=20, col=1, row=1)
        add_entry(tab=frame_power_meas_rf_gen, text_var=self.rf_gen_step, width=20, col=1, row=2)
        add_entry(tab=frame_power_meas_rf_gen, text_var=rf_gen_frequency, width=20, col=1, row=3)

        add_label(tab=frame_power_meas_rf_gen, label_name="Min Power (dBm)", col=0, row=0)
        add_label(tab=frame_power_meas_rf_gen, label_name="Max Power (dBm)", col=0, row=1)
        add_label(tab=frame_power_meas_rf_gen, label_name="Step Power (dB)", col=0, row=2)
        add_label(tab=frame_power_meas_rf_gen, label_name="Frequency (GHz)", col=0, row=3)

        add_button(tab=frame_power_meas_rf_gen, button_name='Set RF Gen\nParameters',
                   command=lambda: scripts_and_functions.rf_gen_power_lim(), col=0, row=4).grid()

        self.text_power_file_name = tk.Text(frame_power_meas, width=40, height=1, wrap=tk.WORD, border=4,
                                            borderwidth=2, relief=tk.SUNKEN,
                                            font=('Bahnschrift Light', 10))  # Filename
        self.text_power_file_name.grid(column=0, row=0, sticky='n', columnspan=5)
        self.text_power_debug = tk.Text(frame_power_meas,
                                        width=40, height=10, wrap=tk.WORD, border=4, borderwidth=2,
                                        relief=tk.SUNKEN,
                                        font=('Bahnschrift Light', 10))  # Debug text_file_name_s3p_test display
        self.text_power_debug.grid(column=0, row=3, sticky='n', columnspan=4)

        add_button(tab=frame_power_measurement_signal_generator, button_name='Set Pulse\nParameters',
                   command=lambda: self.app.set_pulse_gen_pulse_mode(
                       amplitude=self.amplitude.get(),
                       pulse_width=self.pulse_width.get(),
                       prf=self.prf.get()
                   ), col=0,
                   row=0)
        add_label(frame_power_measurement_signal_generator, label_name='Amplitude', col=0, row=1).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_label(frame_power_measurement_signal_generator, label_name='(V)', col=2, row=1).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_entry(tab=frame_power_measurement_signal_generator, text_var=self.amplitude, width=20, col=1, row=1)

        add_label(frame_power_measurement_signal_generator, label_name='Pulse Width', col=0, row=2).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_label(frame_power_measurement_signal_generator, label_name='(µs)', col=2, row=2).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_entry(tab=frame_power_measurement_signal_generator, text_var=self.pulse_width, width=20, col=1, row=2)

        add_label(frame_power_measurement_signal_generator, label_name='PRF', col=0, row=3).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_label(frame_power_measurement_signal_generator, label_name='(Hz)', col=2, row=3).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_y)
        add_entry(tab=frame_power_measurement_signal_generator, text_var=self.prf, width=20, col=1, row=3)

        add_button(tab=frame_power_meas, button_name='Exit', command=lambda: [self.app._quit(), close_resources()],
                   col=1,
                   row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_y)

        add_button(tab=frame_power_meas, button_name='Acquire Traces',
                   command=self.acquire_and_plot_traces, col=0, row=4).grid(ipadx=tab_pad_x, ipady=tab_pad_y)
        add_button(tab=frame_power_meas, button_name='Clear Traces',
                   command=self.clear_traces, col=1, row=4).grid(ipadx=tab_pad_x, ipady=tab_pad_y)

        add_button(tab=frame_power_meas, button_name='Launch Test',
                   command=self.launch_time_domain_power_sweep, col=1, row=5).grid(ipadx=tab_pad_x, ipady=tab_pad_y)

        add_button(tab=frame_power_measurement_signal_generator,
                   button_name='Power Handling\nTest setup'.format(align="=", fill=' '),
                   command=lambda: [scripts_and_functions.setup_power_test_sequence()], col=1, row=0).grid()

        add_button(tab=frame_power_meas_powermeter, button_name='Attenuation\nConfig',
                   command=lambda: [scripts_and_functions.set_channel_attenuation(
                       atts={"A": self.test_pow_input_atten.get(), "B": self.test_pow_output_atten.get()})],
                   col=1, row=5).grid()

        add_button(tab=frame_power_meas_rf_gen, button_name="Reset RF gen",
                   command=lambda: [scripts_and_functions.rf_gen_power_setup()], col=0, row=5)

        add_button(tab=frame_power_meas_rf_gen, button_name="Set RF gen\nFrequency",
                   command=lambda: [scripts_and_functions.rf_gen_set_freq(rf_gen_frequency.get())], col=0,
                   row=6)
        add_button(tab=frame_power_meas_rf_gen, button_name="Config time\ndomain\n RF pulses ",
                   command=lambda: [scripts_and_functions.rf_gen_time_domain_setup()], col=0,
                   row=7)

        add_button(tab=frame_power_meas_powermeter, button_name='Biased time\ndomain Power\nConfig',
                   command=lambda: [scripts_and_functions.powermeter_config_power_bias()],
                   col=0, row=5).grid()

        create_canvas(figure=self.app.fig_time_domain_power_meas, frame=frame_power_meas_graph,
                      toolbar_frame=frame_test_power_measurement, toolbar=True)
