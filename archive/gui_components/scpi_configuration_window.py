
from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_refactored import Window
from .gui_utils import add_label_frame, add_label, add_entry, tab_pad_x


class ScpiConfigurationWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")

        frame_resources = add_label_frame(master, frame_name='Ressouce Configuration', col=0, row=0, sticky="nsew")
        frame_resources.grid_columnconfigure(2, weight=1)
        # Resource frame

        self.app.zva_inst.set(os.getenv('ZVA_IP', r'TCPIP0::ZNA67-101810::inst0::INSTR'))
        self.app.signal_generator_instance.set(os.getenv('SIG_GEN_IP', r'TCPIP0::A-33521B-00526::inst0::INSTR'))
        self.app.osc_inst.set(os.getenv('OSC_IP', r'TCPIP0::DPO5054-C011738::inst0::INSTR'))
        self.app.powermeter_inst.set(os.getenv('POWERMETER_IP', u'TCPIP0::A-N1912A-00589::inst0::INSTR'))
        self.app.rf_gen_inst.set(os.getenv('RF_GEN_IP', u'TCPIP0::rssmb100a179766::inst0::INSTR'))

        add_label(frame_resources, label_name='ZVA', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                        ipady=tab_pad_x)
        add_label(frame_resources, label_name='Signal Generator', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                     ipady=tab_pad_x)
        add_label(frame_resources,
                  label_name='Oscilloscope', col=1, row=3).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_resources,
                  label_name='Powermeter', col=1, row=4).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)
        add_label(frame_resources,
                  label_name='RF Generator', col=1, row=5).grid(sticky='e', ipadx=tab_pad_x, ipady=tab_pad_x)

        self.app.entered_var_zva_address = add_entry(frame_resources, text_var=self.app.zva_inst, width=70, col=2, row=1)
        self.app.entered_variable_signal_generator_address = add_entry(frame_resources,
                                                                   text_var=self.app.signal_generator_instance,
                                                                   width=70,
                                                                   col=2,
                                                                   row=2)
        self.app.entered_var_osc_address = add_entry(frame_resources, text_var=self.app.osc_inst, width=70, col=2, row=3)
        self.app.entered_var_powermeter_address = add_entry(frame_resources, text_var=self.app.powermeter_inst, width=70,
                                                        col=2,
                                                        row=4)
        self.app.entered_var_rf_gen_address = add_entry(frame_resources, text_var=self.app.rf_gen_inst, width=70, col=2,
                                                    row=5)
