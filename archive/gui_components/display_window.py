# gui_components/display_window.py

from __future__ import annotations
import tkinter as tk
import ttkbootstrap as ttk
from typing import TYPE_CHECKING

from gui_components.gui_utils import add_label_frame, add_button, add_label, add_entry, add_combobox, create_canvas, \
    add_slider, \
    update_entries, update_button, filetypes_dir, tab_pad_x
from gui_components.s2p_display_window import S2pDisplayWindow
from gui_components.s3p_display_window import S3pDisplayWindow
from gui_components.pull_in_display_window import PullInDisplayWindow


class DisplayWindow(ttk.Frame):
    def __init__(self, master, app: "Window"):
        super().__init__(master)
        self.app = app
        self.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        s2p_tab = ttk.Frame(notebook)
        s3p_tab = ttk.Frame(notebook)
        pull_in_tab = ttk.Frame(notebook)

        notebook.add(s2p_tab, text='S2P Display')
        notebook.add(s3p_tab, text='S3P Display')
        notebook.add(pull_in_tab, text='Pull-in Display')

        S2pDisplayWindow(s2p_tab, self.app)
        S3pDisplayWindow(s3p_tab, self.app)
        self.app.pull_in_display_window_instance = PullInDisplayWindow(pull_in_tab, self.app)
