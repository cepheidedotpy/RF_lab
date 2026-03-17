import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

from src.core import scripts_and_functions
# from typing import TYPE_CHECKING


# if TYPE_CHECKING:
#     from main_refactored import Window
from src.gui.gui_utils import add_label_frame, add_button, add_label, add_entry, add_Checkbutton, create_canvas, \
    tab_pad_x, \
    default_style


class CyclingTestWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)

        frame_cycling_comp_info = add_label_frame(tab=master, frame_name='Component information', col=0,
                                                  row=0)  # Resource frame
        frame_oscilloscope = add_label_frame(tab=master, frame_name='Oscilloscope', col=0, row=2)
        frame_signal_generator = add_label_frame(tab=master, frame_name='Signal Generator', col=0, row=1)
        frame_cycling_monitor = add_label_frame(tab=master, frame_name='Cycling monitor', col=1, row=0,
                                                row_span=4, sticky="nsew")
        frame_rf_gen = add_label_frame(tab=master, frame_name='RF generator', col=0, row=3)

        frame_osc_toolbar = ttk.Frame(frame_cycling_monitor, style=default_style)
        frame_osc_toolbar.pack(anchor='nw')

        frame_cycling_comp_info.grid_columnconfigure(0, weight=1)
        frame_cycling_comp_info.grid_columnconfigure(1, weight=1)
        frame_signal_generator.grid_columnconfigure(0, weight=1)
        frame_signal_generator.grid_columnconfigure(1, weight=1)
        frame_signal_generator.grid_columnconfigure(2, weight=1)
        frame_oscilloscope.grid_columnconfigure(0, weight=1)
        frame_oscilloscope.grid_columnconfigure(1, weight=1)
        frame_oscilloscope.grid_columnconfigure(2, weight=1)
        frame_oscilloscope.grid_columnconfigure(3, weight=1)
        frame_rf_gen.grid_columnconfigure(0, weight=1)

        add_label(frame_cycling_comp_info,
                  label_name='DIR', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Project', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Cell', col=0, row=2).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Reticule', col=0, row=3).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Device', col=0, row=4).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Cycles', col=0, row=5).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Events', col=0, row=6).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='Header info', col=0, row=7).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_cycling_comp_info,
                  label_name='x10^5', col=2, row=5).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

        add_button(tab=frame_cycling_comp_info, button_name="Exit", command=self.app._quit,
                   col=0, row=8)
        add_button(tab=frame_cycling_comp_info, button_name="Start Cycling",
                   command=lambda: [self.app.cycling_test()],
                   col=1, row=8)
        add_button(tab=frame_cycling_comp_info, button_name="Stop Cycling",
                   command=lambda: [self.app.stop_cycling_test()],
                   col=0, row=9)

        self.entered_cycling_dir = tk.StringVar(
            value=r'C:\Users\TEMIS\PycharmProjects\pythonProject\venv\TEMIS MEMS LAB\dummy_data')
        self.app.test_cycling_project = tk.StringVar(value=r'Project_Name')
        self.app.test_cycling_cell = tk.StringVar(value='Cell_name')
        self.app.test_cycling_ret = tk.StringVar(value='Reticule')
        self.app.test_cycling_device = tk.StringVar(value='Device_Name')
        self.app.test_cycling_var_bias = tk.StringVar(value='Bias_voltage')
        self.app.test_cycling_var_nb_cycles = tk.DoubleVar(value=1)
        self.app.test_cycling_file_comment = tk.StringVar(value='')
        self.app.test_cycling_events = tk.DoubleVar(value=100)
        self.app.test_cycling_gen_power = tk.DoubleVar(value=0)
        self.app.test_cycling_gen_frequency = tk.DoubleVar(value=10)
        self.app.test_cycling_cursor_1_position = tk.StringVar(value='0.203')
        self.app.test_cycling_cursor_2_position = tk.StringVar(value='0.203')
        # Define the Checkbutton
        self.app.toggle_state = tk.BooleanVar()
        self.app.toggle_state.set(False)  # Set initial state to OFF

        self.app.entered_cycling_dir = add_entry(
            frame_cycling_comp_info, text_var=self.app.test_cycling_dir, width=20, col=1, row=0)
        self.app.entered_var_cycling_project = add_entry(
            frame_cycling_comp_info, text_var=self.app.test_cycling_project, width=20, col=1, row=1)
        self.app.entered_var_cycling_cell = add_entry(
            frame_cycling_comp_info, text_var=self.app.test_cycling_cell, width=20, col=1, row=2)
        self.app.entered_cycling_ret = add_entry(
            frame_cycling_comp_info, text_var=self.app.test_cycling_ret, width=15, col=1, row=3)
        self.app.entered_cycling_device = add_entry(
            frame_cycling_comp_info, text_var=self.app.test_cycling_device, width=20, col=1, row=4)
        self.app.entered_cycling_var_bias = add_entry(
            frame_cycling_comp_info, text_var=self.app.test_cycling_var_nb_cycles, width=20, col=1, row=5)
        self.app.entered_test_cycling_events = add_entry(
            frame_cycling_comp_info, text_var=self.app.test_cycling_events, width=20, col=1, row=6)
        self.app.entered_file_name = add_entry(
            frame_cycling_comp_info, text_var=self.app.test_cycling_file_comment, width=20, col=1, row=7)

        add_label(frame_signal_generator, label_name='Bias voltage', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                                        ipady=tab_pad_x)
        add_label(frame_signal_generator, label_name='V', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                                             ipady=tab_pad_x)
        add_label(frame_signal_generator, label_name='Number of Cycles', col=0, row=1).grid(sticky='e',
                                                                                            ipadx=tab_pad_x,
                                                                                            ipady=tab_pad_x)
        add_label(frame_signal_generator, label_name='Cycles (x10^5)', col=2, row=1).grid(sticky='e',
                                                                                          ipadx=tab_pad_x,
                                                                                          ipady=tab_pad_x)
        self.app.test_cycling_var_bias = tk.StringVar(value='40')

        self.app.entered_var_cycling_bias = add_entry(frame_signal_generator, text_var=self.app.test_cycling_var_bias,
                                                      width=15,
                                                      col=1,
                                                      row=0)
        self.app.entered_var_cycling_nb_cycles = add_entry(frame_signal_generator,
                                                           text_var=self.app.test_cycling_var_nb_cycles,
                                                           width=15, col=1, row=1)

        add_button(tab=frame_signal_generator, button_name='Cycling config',
                   command=lambda: [scripts_and_functions.signal_Generator_cycling_config()], col=0,
                   row=2)

        add_button(tab=frame_signal_generator, button_name='Set Bias Voltage',
                   command=lambda: self.app.set_symmetrical_voltage_bias(voltage=self.app.test_cycling_var_bias.get()),
                   col=1,
                   row=2)
        add_button(tab=frame_signal_generator, button_name='Output ON/OFF',
                   command=lambda: [scripts_and_functions.on_off_signal_generator_switch()], col=2,
                   row=2)
        add_button(tab=frame_signal_generator, button_name='1kHz-1000pulses\n100us-1%',
                   command=lambda: [scripts_and_functions.load_pattern(
                       r"1000pulses_100us_pulse_dc1%_36Vtop40V_triangle.arb")], col=0,
                   row=3)
        add_button(tab=frame_signal_generator, button_name='2kHz-1000pulses\n100us-5%',
                   command=lambda: [scripts_and_functions.load_pattern(
                       r"1000pulses_100us_pulse_dc5%_36Vtop40V_triangle.arb")], col=1,
                   row=3)
        add_button(tab=frame_signal_generator, button_name='4kHz-1000pulses\n100us-10%',
                   command=lambda: [scripts_and_functions.load_pattern(
                       r"1000pulses_100us_pulse_dc10%_36Vtop40V_triangle.arb")], col=2,
                   row=3)

        add_label(frame_oscilloscope,
                  label_name='Set cursor 1 position', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x,
                                                                         ipady=tab_pad_x)
        add_label(frame_oscilloscope,
                  label_name='Set cursor 2 position', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                         ipady=tab_pad_x)
        self.app.entered_var_cycling_cursor_1 = add_entry(frame_oscilloscope,
                                                          text_var=self.app.test_cycling_cursor_1_position,
                                                          width=15, col=1, row=0)
        self.app.entered_var_cycling_cursor_2 = add_entry(frame_oscilloscope,
                                                          text_var=self.app.test_cycling_cursor_2_position,
                                                          width=15, col=1, row=1)
        add_label(frame_oscilloscope,
                  label_name='s', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x,
                                                     ipady=tab_pad_x)
        add_label(frame_oscilloscope,
                  label_name='s', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x,
                                                     ipady=tab_pad_x)
        add_button(tab=frame_oscilloscope, button_name='Set Cursor 1',
                   command=lambda: [scripts_and_functions.move_oscilloscope_cursor(
                       cursor_number=1, cursor_type='X',
                       position=self.app.entered_var_cycling_cursor_1.get())], col=3,
                   row=0)

        add_button(tab=frame_oscilloscope, button_name='Set Cursor 2',
                   command=lambda: [scripts_and_functions.move_oscilloscope_cursor(
                       cursor_number=2, cursor_type='X',
                       position=self.app.entered_var_cycling_cursor_2.get())], col=3,
                   row=1)

        add_button(tab=frame_oscilloscope, button_name='Cycling config',
                   command=scripts_and_functions.osc_cycling_config, col=0,
                   row=2)
        add_button(tab=frame_oscilloscope, button_name="Set event count",
                   command=lambda: [scripts_and_functions.set_osc_event_count(self.app.test_cycling_events.get())],
                   col=1, row=2)

        add_Checkbutton(tab=frame_oscilloscope,
                        text=self.app.toggle_state,
                        col=2, row=2, off_value=0,
                        on_value=1, command=lambda: [self.app.on_checkbutton_toggle()])

        add_label(frame_rf_gen,
                  label_name='RF Power', col=0, row=0).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_rf_gen,
                  label_name='dBm', col=2, row=0).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_rf_gen,
                  label_name='Frequency', col=0, row=1).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_rf_gen,
                  label_name='GHz', col=2, row=1).grid(sticky='w', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_button(tab=frame_rf_gen, button_name='Gen config',
                   command=lambda: scripts_and_functions.rf_gen_cycling_setup(
                       power=self.app.test_cycling_gen_power.get(),
                       frequency=self.app.test_cycling_gen_frequency.get()), col=0,
                   row=2)
        self.app.entered_gen_power = add_entry(
            frame_rf_gen, text_var=self.app.test_cycling_gen_power, width=20, col=1, row=0)
        self.app.entered_gen_power = add_entry(
            frame_rf_gen, text_var=self.app.test_cycling_gen_frequency, width=20, col=1, row=1)

        self.app.canvas_cycling = create_canvas(figure=self.app.fig_cycling, frame=frame_cycling_monitor,
                                                toolbar_frame=frame_osc_toolbar, toolbar=True)
