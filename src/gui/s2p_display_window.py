from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk
from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from main_refactored import Window
from src.gui.gui_utils import (add_label_frame, add_button, add_label, add_entry, add_combobox, create_canvas,
    add_slider, update_entries, update_button, filetypes_dir, tab_pad_x, close_resources,
    add_listbox, update_listbox, get_listbox_selection, browse_directory)

class S2pDisplayWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # TAB2 S2P parameter display
        frame_s2p_dir = add_label_frame(master, 's2p Directory', 0, 0)  # s2p Frame
        frame_s2p_dir.grid_columnconfigure(3, weight=1)
        frame_s2p_dir.grid_columnconfigure(5, weight=1)
        frame_s2p_display = add_label_frame(master, frame_name='s2p Display', col=0, row=1, sticky="nsew")
        frame_s2p_sliders = add_label_frame(master, frame_name='Frequency Range', col=0, row=2)

        # Adding String variables

        add_label(frame_s2p_dir, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
        add_label(frame_s2p_dir, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                       ipady=tab_pad_x)
        add_label(frame_s2p_dir, label_name='S parameter', col=1, row=3).grid(sticky='e', ipadx=tab_pad_x,
                                                                              ipady=tab_pad_x)

        # Adding entry for file directory
        self.app.entered_var_s2p = add_entry(frame_s2p_dir, text_var=self.app.s2p_dir_name, width=70, col=2, row=1)

        self.app.s2p_file_name_listbox = add_listbox(frame_s2p_dir, col=2, row=2, width=100, height=5)
        update_listbox(self.app.entered_var_s2p.get(), self.app.s2p_file_name_listbox, '.s2p')
        self.app.s_parameter_chosen_s2p = add_combobox(frame_s2p_dir, text=self.app.s_parameter_s2p, col=2, row=3,
                                                       width=100)
        self.app.s_parameter_chosen_s2p['values'] = ('S11', 'S12', 'S21', 'S22')

        def on_s2p_select(event=None):
            selection = get_listbox_selection(self.app.s2p_file_name_listbox)
            if selection:
                self.app.trace_s2p(filename=selection, s_param=self.app.s_parameter_chosen_s2p.get())

        self.app.s2p_file_name_listbox.bind('<<ListboxSelect>>', on_s2p_select)
        
        self.app.s_parameter_chosen_s2p.bind('<<ComboboxSelected>>', on_s2p_select)

        # Adding buttons
        self.app.update_s2p_button = add_button(tab=frame_s2p_dir, button_name=' Browse Folder ',
                                                command=lambda: browse_directory(self.app.s2p_dir_name, 
                                                                                 lambda: update_listbox(self.app.s2p_dir_name.get(), 
                                                                                                        self.app.s2p_file_name_listbox, '.s2p')), col=3, row=1)
        add_button(frame_s2p_dir, button_name='Delete Graphs',
                   command=self.app.delete_axs_s2p, col=3, row=2)
        add_button(frame_s2p_dir, button_name='Plot',
                   command=on_s2p_select, col=3, row=3)
        add_button(frame_s2p_dir, button_name='Exit',
                   command=self.app._quit, col=3, row=4)

        # Canvas creation
        self.app.s2p_canvas = create_canvas(figure=self.app.fig_s2p, frame=frame_s2p_display,
                                            toolbar_frame=frame_s2p_sliders)

        # Sliders creation
        self.app.slider_amplitude_s2p = add_slider(frame=frame_s2p_display, _from=0, to=-80,
                                                   name="Amplitude (dB)",
                                                   variable=self.app.scale_amplitude_value, step=5,
                                                   orientation=tk.VERTICAL,
                                                   command=self.app.update_s2p_plot_limits,
                                                   unit="dB")
        self.app.slider_frequency_s2p = add_slider(frame=frame_s2p_sliders, _from=0, to=110e9,
                                                   name="Upper Frequency limit (Hz)",
                                                   variable=self.app.scale_frequency_upper_value, step=10e9,
                                                   command=self.app.update_s2p_plot_limits,
                                                   multiplier=1e-9, unit="GHz")
        self.app.slider_lower_frequency_s2p = add_slider(frame=frame_s2p_sliders, _from=0, to=40e9,
                                                         name=" Lower Frequency Limit (Hz)",
                                                         variable=self.app.scale_frequency_lower_value, step=10e9,
                                                         command=self.app.update_s2p_plot_limits,
                                                         multiplier=1e-9, unit="GHz")

        self.app.slider_amplitude_s2p.pack(side='left', anchor='center')
        self.app.slider_frequency_s2p.pack(side='right')
        self.app.slider_lower_frequency_s2p.pack(side='left')
