from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk

from src.gui.gui_utils import (add_label_frame, add_button, add_scrolled_text, create_canvas, add_slider,
                                      update_entries, update_button, filetypes_dir, add_entry, add_combobox,
                                      close_resources, add_listbox, update_listbox, get_listbox_selection, browse_directory)


class PullInDisplayWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(3, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # TAB is for Pull voltage vs isolation display
        frame_v_pull_in_dir = add_label_frame(master, frame_name='Vpull-in Directory', col=0,
                                              row=0)  # s2p Frame
        frame_v_pull_in_dir.grid_columnconfigure(3, weight=1)
        frame_v_pull_in_dir.grid_columnconfigure(5, weight=1)
        frame_v_pull_in_graph = add_label_frame(master, frame_name='Graph', col=0, row=3, sticky="nsew")  # s2p Frame
        frame_v_pull_in_sliders = add_label_frame(master, frame_name='Voltage limit', col=0, row=4)
        frame_v_pull_in_display = add_label_frame(master, frame_name='Pull-in Display', col=0, row=1)

        # Adding entry for file directory
        self.app.entered_var_txt = add_entry(frame_v_pull_in_dir, text_var=self.app.pull_in_dir_name, width=70, col=2,
                                             row=1)

        self.app.txt_file_name_listbox = add_listbox(frame_v_pull_in_dir, col=2, row=2, width=100, height=5, rowspan=2)
        update_listbox(self.app.entered_var_txt.get(), self.app.txt_file_name_listbox, '.txt')

        def on_txt_select(event=None):
            selection = get_listbox_selection(self.app.txt_file_name_listbox)
            if selection:
                self.app.trace_pull_down(filename=selection)

        self.app.txt_file_name_listbox.bind('<<ListboxSelect>>', on_txt_select)

        # Adding buttons
        self.app.update_pull_in_button = add_button(tab=frame_v_pull_in_dir, button_name=' Browse Folder ',
                                                    command=lambda: browse_directory(self.app.pull_in_dir_name, 
                                                                                     lambda: update_listbox(self.app.pull_in_dir_name.get(), 
                                                                                                            self.app.txt_file_name_listbox, '.txt')),
                                                    col=3, row=1)
        add_button(frame_v_pull_in_dir, button_name='Delete Graphs', command=self.app.delete_axs_vpullin, col=3,
                   row=2)
        add_button(frame_v_pull_in_dir, button_name='Plot',
                   command=on_txt_select,
                   col=3, row=3)
        add_button(frame_v_pull_in_dir, button_name='Exit', command=self.app._quit,
                   col=3, row=4).grid_anchor('e')
        # Scrolled text creation
        self.app.text_scroll = add_scrolled_text(tab=frame_v_pull_in_display, scrolled_width=100,
                                                 scrolled_height=3)
        # Canvas creation
        self.app.canvas_v_pull_in_display = create_canvas(figure=self.app.fig_pull_in, frame=frame_v_pull_in_graph,
                                                          toolbar_frame=frame_v_pull_in_sliders)

        # Sliders creation
        self.app.slider_isolation = add_slider(frame=frame_v_pull_in_graph, _from=0, to=-20,
                                               name="Detector voltage (dB)", variable=self.app.scale_isolation_value,
                                               step=1,
                                               orientation=tk.VERTICAL)
        self.app.slider_voltage = add_slider(frame=frame_v_pull_in_sliders, _from=0, to=100,
                                             name="Voltage upper limit (V)", variable=self.app.scale_voltage_value,
                                             step=10)

        self.app.slider_isolation.pack(side='left')
        self.app.slider_voltage.pack(side='left')
