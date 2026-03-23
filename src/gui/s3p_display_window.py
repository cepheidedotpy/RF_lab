
from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_refactored import Window
from .gui_utils import (add_label_frame, add_button, add_label, add_entry, add_combobox, create_canvas,
    add_slider, update_entries, update_button, filetypes_dir, tab_pad_x, close_resources,
    add_listbox, update_listbox, get_listbox_selection, browse_directory)


class S3pDisplayWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # TAB1 S3P parameter display
        frame_s3p_dir = add_label_frame(master, 's3p Directory', 0, 0)  # s3p Frame
        frame_s3p_dir.grid_columnconfigure(3, weight=1)
        frame_s3p_dir.grid_columnconfigure(5, weight=1)
        frame_s3p_display = add_label_frame(master, frame_name='s3p Display', col=0, row=1, sticky="nsew")
        frame_s3p_sliders = add_label_frame(master, frame_name='Frequency Range', col=0, row=2)

        # Adding String variables

        self.app.s_parameter_s3p = tk.StringVar(value='S11')  # Entry variable for s parameter dir

        # Adding labels and frame_s3p_display
        add_label(frame_s3p_dir, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                            ipady=tab_pad_x)
        add_label(frame_s3p_dir, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                       ipady=tab_pad_x)
        add_label(frame_s3p_dir, label_name='S parameter', col=1, row=3).grid(sticky='e',
                                                                              ipadx=tab_pad_x,
                                                                              ipady=tab_pad_x)
        # Adding entry for file directory
        self.app.entered_var_s3p = add_entry(frame_s3p_dir, text_var=self.app.s3p_dir_name, width=70, col=2,
                                         row=1)
        self.app.s3p_file_name_listbox = add_listbox(frame_s3p_dir, col=2, row=2, width=100, height=5)
        update_listbox(self.app.entered_var_s3p.get(), self.app.s3p_file_name_listbox, '.s3p')
        self.app.s_parameter_chosen_s3p = add_combobox(frame_s3p_dir, text=self.app.s_parameter_s3p, col=2, row=3,
                                                   width=100)
        self.app.s_parameter_chosen_s3p['values'] = ('S11', 'S12', 'S13', 'S21', 'S22', 'S23', 'S31', 'S32', 'S33')

        def on_s3p_select(event=None):
            selection = get_listbox_selection(self.app.s3p_file_name_listbox)
            if selection:
                self.app.trace_s3p(filename=selection, s_param=self.app.s_parameter_chosen_s3p.get())

        self.app.s3p_file_name_listbox.bind('<<ListboxSelect>>', on_s3p_select)
        self.app.s_parameter_chosen_s3p.bind('<<ComboboxSelected>>', on_s3p_select)

        self.app.button_file_update = add_button(tab=frame_s3p_dir, button_name='Browse Folder',
                                             command=lambda: browse_directory(self.app.s3p_dir_name, 
                                                                              lambda: update_listbox(self.app.s3p_dir_name.get(), 
                                                                                                     self.app.s3p_file_name_listbox, '.s3p')), col=3,
                                             row=1)
        # Adding buttons
        add_button(tab=frame_s3p_dir, button_name='Delete graphs', command=self.app.delete_axs_s3p, col=3,
                   row=2)
        add_button(tab=frame_s3p_dir, button_name='Plot', command=on_s3p_select,
                   col=3, row=3)
        add_button(tab=frame_s3p_dir, button_name='Exit',
                   command=self.app._quit, col=3, row=4)
        # Canvas creation
        self.app.s3p_canvas = create_canvas(figure=self.app.fig_s3p, frame=frame_s3p_display,
                                        toolbar_frame=frame_s3p_sliders)

        # Sliders creation
        self.app.slider_amplitude = add_slider(frame=frame_s3p_display, _from=0, to=-50,
                                           name="Amplitude (dB)",
                                           variable=self.app.scale_amplitude_value, step=5, orientation=tk.VERTICAL)
        self.app.slider_frequency = add_slider(frame=frame_s3p_sliders, _from=1e9, to=50e9,
                                           name="Upper Frequency Limit (Hz)",
                                           variable=self.app.scale_frequency_upper_value, step=10e9)
        self.app.slider_lower_frequency = add_slider(frame=frame_s3p_sliders, _from=1e9, to=50e9,
                                                 name="Lower Frequency Limit (Hz)",
                                                 variable=self.app.scale_frequency_lower_value, step=10e9)
        self.app.slider_amplitude.pack(side='left', anchor="center")
        self.app.slider_frequency.pack(side='right')
        self.app.slider_lower_frequency.pack(side='left')
