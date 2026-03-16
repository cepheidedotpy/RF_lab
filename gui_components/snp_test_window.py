from __future__ import annotations
# gui_components/snp_test_window.py

import skrf as rf
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import scrolledtext
from dev import scripts_and_functions
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from typing import Optional, Literal, TYPE_CHECKING
import os
from dir_and_var_declaration import zva_parameters
import dir_and_var_declaration
from gui_components.gui_utils import add_label_frame, add_button, add_label, add_entry, add_combobox, create_canvas, \
    file_name_creation, close_resources, call_s3p_config, call_s2p_config, call_s1p_config, tab_pad_x


class SnpTestWindow(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        tab_pad_x = 5
        tab_pad_y = 5
        frame_snp_compo_info = add_label_frame(self, frame_name='Component information', col=0,
                                               row=0)  # s3p frame
        frame_snp_signal_generator = add_label_frame(self, frame_name='Signal Generator', col=0, row=1)
        frame_snp_zva = add_label_frame(self, frame_name='ZVA', col=3, row=1)
        frame_snp_gene_controls = add_label_frame(self, frame_name='General controls', col=3, row=0)
        frame_snp_measurement = add_label_frame(self, frame_name='SNP measurement', col=1, row=0,
                                                row_span=2, sticky="nsew")
        frame_test_snp_measurement = ttk.Frame(frame_snp_measurement)
        frame_test_snp_measurement.pack(anchor='nw')

        frame_snp_compo_info.grid_columnconfigure(2, weight=1)
        frame_snp_signal_generator.grid_columnconfigure(3, weight=1)
        frame_snp_zva.grid_columnconfigure(1, weight=1)
        frame_snp_zva.grid_columnconfigure(2, weight=1)
        frame_snp_zva.grid_columnconfigure(3, weight=1)
        frame_snp_gene_controls.grid_columnconfigure(0, weight=1)
        frame_snp_gene_controls.grid_columnconfigure(1, weight=1)
        frame_snp_gene_controls.grid_columnconfigure(2, weight=1)

        add_label(frame_snp_compo_info, label_name='DIR', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                             ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Project', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                 ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Cell', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                              ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                                  ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Device', col=0, row=4).grid(sticky='e', ipadx=tab_pad_x,
                                                                                ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Status', col=0, row=5).grid(sticky='e', ipadx=tab_pad_x,
                                                                                ipady=tab_pad_x)
        add_label(frame_snp_compo_info, label_name='Bias Voltage', col=0, row=6).grid(sticky='e', ipadx=tab_pad_x,
                                                                                      ipady=tab_pad_x)

        self.test_s3p_dir = tk.StringVar(
            value=r'C:\Users\TEMIS\PycharmProjects\pythonProject\venv\TEMIS MEMS LAB\dummy_data')
        self.test_s3p_project = tk.StringVar(value=r'Project_Name')
        self.test_s3p_cell = tk.StringVar(value=r'Cell_Name')
        self.test_s3p_reticule = tk.StringVar(value=r'Reticule')
        self.test_s3p_device = tk.StringVar(value=r'Device_name')
        self.test_s3p_file_created = tk.StringVar(value=r'EMPTY')
        self.test_s3p_state = tk.StringVar(value=r'Active')

        self.bias_voltage_s3p = tk.StringVar(value=r'Bias_Voltage')

        self.chosen_component_state = add_combobox(frame_snp_compo_info, text=self.test_s3p_state, col=1, row=5,
                                                   width=20)
        self.chosen_component_state['values'] = ('Active', 'Frozen')
        self.chosen_component_state.current(0)

        self.vna_connected = tk.StringVar(value=r'ZNA67')

        self.chosen_vna = add_combobox(frame_snp_zva, text=self.vna_connected, col=0, row=5,
                                       width=20)
        self.chosen_vna['values'] = ('ZNA67', 'ZVA50')

        self.chosen_vna.current(0)

        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_dir, width=20, col=1, row=0)
        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_project, width=20, col=1, row=1)
        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_cell, width=20, col=1, row=2)
        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_reticule, width=20, col=1, row=3)
        add_entry(tab=frame_snp_compo_info, text_var=self.test_s3p_device, width=20, col=1, row=4)

        #  ------------------------------------------------------------------------------
        self.text_file_name_s3p_test = tk.Text(frame_snp_gene_controls, width=40, height=1, wrap=tk.WORD, border=4,
                                               borderwidth=2,
                                               relief=tk.SUNKEN, font=('Bahnschrift Light', 10))

        self.pull_in_v = tk.DoubleVar(value=10)
        self.pulse_width = tk.DoubleVar(value=5)
        self.pulse_freq = tk.DoubleVar(value=0.1)
        self.chosen_bias_voltage = add_entry(tab=frame_snp_compo_info, text_var=self.pull_in_v, width=20, col=1,
                                             row=6)

        self.file_s3p = tk.StringVar(value=r'test')

        add_button(tab=frame_snp_compo_info, button_name='Create-file',
                   command=lambda: [file_name_creation(
                       data_list=[self.test_s3p_project.get(), self.test_s3p_cell.get(),
                                  self.test_s3p_reticule.get(),
                                  self.test_s3p_device.get(), self.chosen_component_state.get(),
                                  self.chosen_bias_voltage.get()], text=self.text_file_name_s3p_test,
                       end_characters='V')], col=2,
                   row=0)
        add_button(tab=frame_snp_compo_info,
                   button_name='Send trigger',
                   command=lambda: [scripts_and_functions.send_trig()], col=2, row=1)

        add_button(tab=frame_snp_compo_info,
                   button_name='Osc trigger',
                   command=lambda: [scripts_and_functions.force_trigger_osc()], col=2, row=2)

        add_label(frame_snp_signal_generator, label_name='Bias Voltage', col=0, row=0).grid(sticky='e',
                                                                                            ipadx=tab_pad_x,
                                                                                            ipady=tab_pad_x)
        add_label(frame_snp_signal_generator, label_name='Pulse Width', col=0, row=1).grid(sticky='e',
                                                                                           ipadx=tab_pad_x,
                                                                                           ipady=tab_pad_x)
        self.entered_pull_in_volt = add_entry(frame_snp_signal_generator, text_var=self.pull_in_v, width=10, col=1,
                                              row=0)
        self.entered_pulse_width = add_entry(frame_snp_signal_generator, text_var=self.pulse_width, width=10, col=1,
                                             row=1)
        add_label(frame_snp_signal_generator, label_name='(V)', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                                                   ipady=tab_pad_x)
        add_label(frame_snp_signal_generator, label_name='(s)', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x,
                                                                                   ipady=tab_pad_x)

        add_label(frame_snp_signal_generator, label_name='Pulse Frequency', col=0, row=2).grid(sticky='e',
                                                                                               ipadx=tab_pad_x,
                                                                                               ipady=tab_pad_x)
        self.entered_pulse_freq = add_entry(frame_snp_signal_generator, text_var=self.pulse_freq, width=10, col=1,
                                            row=2)
        add_label(frame_snp_signal_generator, label_name='(Hz)', col=2, row=2).grid(sticky='w', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_x)

        add_button(tab=frame_snp_signal_generator, button_name='Set Bias Voltage',
                   command=lambda: scripts_and_functions.bias_voltage(self.pull_in_v.get()),
                   col=3,
                   row=0).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_signal_generator, button_name='Set Pulse Width',
                   command=lambda: scripts_and_functions.set_pulse_width(self.pulse_width.get()),
                   col=3,
                   row=1).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_signal_generator,
                   button_name='Set PRF', command=lambda: scripts_and_functions.set_prf(self.pulse_freq.get()), col=3,
                   row=2).grid(
            sticky='e', ipadx=tab_pad_x,
            ipady=tab_pad_x)
        add_button(tab=frame_snp_signal_generator, button_name='Set Pulse Gen',
                   command=lambda: [
                       scripts_and_functions.set_signal_generator_pulse_parameters(pulse_width=self.pulse_width.get(),
                                                                                   pulse_period=1 / self.pulse_freq.get()),
                       scripts_and_functions.bias_voltage(self.pull_in_v.get())],
                   col=3,
                   row=3).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        # ------------------------------------------------------------------------------
        self.canvas_snp_meas = create_canvas(figure=self.app.fig_snp_meas, frame=frame_snp_measurement,
                                             toolbar_frame=frame_test_snp_measurement, toolbar=True)
        # ------------------------------------------------------------------------------

        self.text_file_name_s3p_test.grid(column=0, row=0, sticky='n', columnspan=5)
        self.f_start = tk.DoubleVar(value=1)
        self.f_stop = tk.DoubleVar(value=10)
        self.nb_points = tk.DoubleVar(value=100)

        add_label(frame_snp_zva, label_name='Fstart', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                         ipady=tab_pad_x)
        add_label(frame_snp_zva, label_name='Fstop', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                        ipady=tab_pad_x)
        add_label(frame_snp_zva, label_name='Nb Points', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
        self.entered_f_start = add_entry(frame_snp_zva, text_var=self.f_start, width=10, col=1, row=0)
        self.entered_fstop = add_entry(frame_snp_zva, text_var=self.f_stop, width=10, col=1, row=1)
        self.entered_nb_points = add_entry(frame_snp_zva, text_var=self.nb_points, width=10, col=1, row=2)
        add_label(frame_snp_zva, label_name='(GHz)', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                                        ipady=tab_pad_x)
        add_label(frame_snp_zva, label_name='(GHz)', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x,
                                                                        ipady=tab_pad_x)
        add_label(frame_snp_zva, label_name='(Pts)', col=2, row=2).grid(sticky='w', ipadx=tab_pad_x,
                                                                        ipady=tab_pad_x)

        add_button(tab=frame_snp_zva, button_name='Set Fstart',
                   command=lambda: self.app.set_f_start(self.f_start.get()), col=3, row=0).grid(sticky='e',
                                                                                                ipadx=tab_pad_x,
                                                                                                ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Set Fstop',
                   command=lambda: self.app.set_fstop(self.f_stop.get()), col=3, row=1).grid(sticky='e',
                                                                                             ipadx=tab_pad_x,
                                                                                             ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Set Nb points',
                   command=lambda: self.app.set_nb_points(self.nb_points.get()), col=3, row=2).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Set ZVA',
                   command=lambda: self.app.set_zva(self.f_start.get(), self.f_stop.get(), self.nb_points.get()), col=3,
                   row=3).grid(sticky='e',
                               ipadx=tab_pad_x,
                               ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Capture S3P', command=lambda: [file_name_creation(data_list=[
            self.test_s3p_project.get(),
            self.test_s3p_cell.get(),
            self.test_s3p_reticule.get(),
            self.test_s3p_device.get(),
            self.chosen_component_state.get(),
            self.chosen_bias_voltage.get()
        ], text=self.text_file_name_s3p_test, end_characters='V'), self.data_acquire(), self.trace_snp_meas('.s3p')],
                   col=1,
                   row=4).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Capture S2P', command=lambda: [file_name_creation(data_list=[
            self.test_s3p_project.get(),
            self.test_s3p_cell.get(),
            self.test_s3p_reticule.get(),
            self.test_s3p_device.get(),
            self.chosen_component_state.get(),
            self.chosen_bias_voltage.get()
        ], text=self.text_file_name_s3p_test, end_characters='V'), self.data_acquire_s2p(),
            self.trace_snp_meas('.s2p')],
                   col=2, row=4).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_zva, button_name='Capture S1P', command=lambda: [file_name_creation(data_list=[
            self.test_s3p_project.get(),
            self.test_s3p_cell.get(),
            self.test_s3p_reticule.get(),
            self.test_s3p_device.get(),
            self.chosen_component_state.get(),
            self.chosen_bias_voltage.get()
        ], text=self.text_file_name_s3p_test, end_characters='V'), self.data_acquire_s1p(),
            self.trace_snp_meas('.s1p')],
                   col=3, row=4).grid(
            sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

        # ------------------------------------------------------------------------------
        self.text_snp_debug = tk.Text(frame_snp_gene_controls, width=40, height=10, wrap=tk.WORD, border=4,
                                      borderwidth=2,
                                      relief=tk.SUNKEN,
                                      font=('Bahnschrift Light', 10))
        self.text_snp_debug.grid(column=0, row=3, sticky='n', columnspan=4)

        add_button(tab=frame_snp_gene_controls, button_name='Comms prep', command=scripts_and_functions.comprep_zva,
                   col=0, row=1).grid(
            ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='Reset ZVA',
                   command=lambda: [self.app.reset_zva(self.text_snp_debug)], col=0,
                   row=2).grid(
            ipadx=tab_pad_x,
            ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='Reconnect ZVA',
                   command=lambda: [self.app.reset_zva_no_setup(self.text_snp_debug)],
                   col=2,
                   row=2).grid(
            ipadx=tab_pad_x,
            ipady=tab_pad_x)

        add_button(tab=frame_snp_gene_controls, button_name='Exit',
                   command=lambda: [self.app._quit(), close_resources()],
                   col=1,
                   row=1).grid(ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_snp_gene_controls, button_name='Reset Signal Gen',
                   command=lambda: self.app.reset_signal_generator(text_widget=self.text_snp_debug),
                   col=1,
                   row=2).grid(ipadx=tab_pad_x, ipady=tab_pad_x)

    def data_acquire(self):
        """
        Acquires S3P data from the ZVA and saves it to a file.
        """
        filename = self.get_filename_s3p()
        if not filename:
            print("Filename is empty. Cannot acquire data.")
            return

        try:
            os.chdir(self.test_s3p_dir.get())
            scripts_and_functions.triggered_data_acquisition(pc_file_dir=f'{self.test_s3p_dir.get()}',
                                                             filename=filename,
                                                             file_format='s3p')
            self.text_snp_debug.insert("1.0", f"S3P file saved as {filename}\n")
            self.app.trace_s3p(filename + '.s3p', self.app.s_parameter_s3p.get())
        except Exception as e:
            print(f"Error during S3P data acquisition: {e}")
            self.text_snp_debug.insert("1.0", f"Error: {e}\n")

    def data_acquire_s2p(self):
        """
        Acquires S2P data from the ZVA and saves it to a file.
        """
        filename = self.get_filename_s3p()
        if not filename:
            print("Filename is empty. Cannot acquire data.")
            return

        try:
            os.chdir(self.test_s3p_dir.get())
            scripts_and_functions.triggered_data_acquisition(pc_file_dir=f'{self.test_s3p_dir.get()}',
                                                             filename=filename,
                                                             file_format='s2p')
            self.text_snp_debug.insert("1.0", f"S2P file saved as {filename}\n")
            self.app.trace_s2p(filename + '.s2p', self.app.s_parameter_s2p.get())
        except Exception as e:
            print(f"Error during S2P data acquisition: {e}\n")
            self.text_snp_debug.insert("1.0", f"Error: {e}\n")

    def data_acquire_s1p(self):
        """
        Acquires S1P data from the ZVA and saves it to a file.
        """
        filename = self.get_filename_s3p()
        if not filename:
            print("Filename is empty. Cannot acquire data.")
            return

        try:
            os.chdir(self.test_s3p_dir.get())
            scripts_and_functions.triggered_data_acquisition(pc_file_dir=f'{self.test_s3p_dir.get()}',
                                                             filename=filename,
                                                             file_format='s1p')
            self.text_snp_debug.insert("1.0", f"S1P file saved as {filename}\n")
            self.app.trace_s1p(filename + '.s1p', self.app.s_parameter_s2p.get())
        except Exception as e:
            print(f"Error during S1P data acquisition: {e}")
            self.text_snp_debug.insert("1.0", f"Error: {e}\n")

    def get_filename_s3p(self) -> str:
        return self.text_file_name_s3p_test.get("1.0", "end-1c")

    def trace_snp_meas(self, suffix: str):
        """
        Reads an SNP file, plots the All S-parameters, and updates the canvas.
        """

        # Clear the previous plot
        self.app.ax_snp_meas.clear()

        try:
            filepath = os.path.join(self.test_s3p_dir.get(),
                                    self.text_file_name_s3p_test.get(index1="1.0", index2="1.end") + f'{suffix}')
            # Read the S3P file using skrf
            network = rf.Network(filepath)
            network.frequency.unit = 'GHz'
            # Plot the specified S-parameter
            network.plot_s_db(ax=self.app.ax_snp_meas)
            self.app.ax_snp_meas.grid()
        except Exception as e:
            print(f"Error plotting S2P file: {e}")
            self.app.ax_snp_meas.text(0.5, 0.5, f"Error: {e}", ha='center', va='center')

        # Redraw the canvas
        self.app.fig_snp_meas.canvas.draw()

    def reset_signal_generator(self):
        """
        Resets the signal generator.
        """
        try:
            address = self.app.signal_generator_instance.get()
            scripts_and_functions.setup_signal_generator_pulsed_with_rst(ip=address)
            self.text_snp_debug.insert("1.0", "Signal generator reset.\n")
        except Exception as e:
            print(f"Error resetting signal generator: {e}")
            self.text_snp_debug.insert("1.0", f"Error: {e}\n")
