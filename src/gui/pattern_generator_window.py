import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

from src.core.pattern_generator import stimulus_wf
from src.core.hardware_control import upload_arb_binary
import numpy as np
from src.gui.gui_utils import add_label_frame, add_button, add_label, add_entry, create_canvas, tab_pad_x, default_style

class PatternGeneratorWindow(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Pattern Generator")
        self.geometry("1000x800")
        
        # Variables
        self.pulse_width_var = tk.StringVar(value="100")
        self.duty_cycle_var = tk.StringVar(value="10")
        self.num_pulses_var = tk.StringVar(value="1000")
        self.amp_top_var = tk.StringVar(value="36")
        self.amp_bottom_var = tk.StringVar(value="36")
        self.ramp_width_var = tk.StringVar(value="500")
        self.amp_ramp_var = tk.StringVar(value="40")
        self.length_top_var = tk.StringVar(value="0.1")
        self.sample_red_factor_var = tk.StringVar(value="100")
        
        self.current_wf = None
        self.current_filtered = None

        self._build_gui()

    def _build_gui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Parameters Frame
        params_frame = add_label_frame(main_frame, "Waveform Parameters", 0, 0)
        params_frame.grid(sticky="ew")
        
        row = 0
        add_label(params_frame, "Pulse Width (µs):", 0, row)
        add_entry(params_frame, self.pulse_width_var, 15, 1, row)
        add_label(params_frame, "Duty Cycle (%):", 2, row)
        add_entry(params_frame, self.duty_cycle_var, 15, 3, row)
        
        row += 1
        add_label(params_frame, "Number of Pulses:", 0, row)
        add_entry(params_frame, self.num_pulses_var, 15, 1, row)
        add_label(params_frame, "Length Top (µs):", 2, row)
        add_entry(params_frame, self.length_top_var, 15, 3, row)
        
        row += 1
        add_label(params_frame, "Amplitude Top (V):", 0, row)
        add_entry(params_frame, self.amp_top_var, 15, 1, row)
        add_label(params_frame, "Amplitude Bottom (V):", 2, row)
        add_entry(params_frame, self.amp_bottom_var, 15, 3, row)
        
        row += 1
        add_label(params_frame, "Ramp Width (µs):", 0, row)
        add_entry(params_frame, self.ramp_width_var, 15, 1, row)
        add_label(params_frame, "Amplitude Ramp (V):", 2, row)
        add_entry(params_frame, self.amp_ramp_var, 15, 3, row)

        row += 1
        add_label(params_frame, "Sample Red. Factor:", 0, row)
        add_entry(params_frame, self.sample_red_factor_var, 15, 1, row)

        # Control Frame
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.grid(row=1, column=0, pady=10, sticky="ew")
        
        add_button(ctrl_frame, "Preview Plot", self.plot_waveform, 0, 0, style=default_style)
        add_button(ctrl_frame, "Export to .arb", self.export_arb, 0, 1, style=default_style)
        add_button(ctrl_frame, "Upload to Instrument", self.upload_to_instrument, 0, 2, style=default_style)

        # Plot Frame
        plot_wrapper = ttk.Frame(main_frame)
        plot_wrapper.grid(row=2, column=0, sticky="nsew", pady=10)
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_wrapper)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_wrapper)
        self.toolbar.update()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def _get_params(self):
        try:
            pw = float(self.pulse_width_var.get()) / (10**6)
            dc = float(self.duty_cycle_var.get()) / 100.0
            npulses = float(self.num_pulses_var.get())
            # Scale voltages
            atop = float(self.amp_top_var.get()) / 20.0
            abot = float(self.amp_bottom_var.get()) / 20.0
            rw = float(self.ramp_width_var.get()) / (10**6)
            aramp = float(self.amp_ramp_var.get()) / 20.0
            ltop = float(self.length_top_var.get()) / (10**6)
            red_factor = int(self.sample_red_factor_var.get())
            
            return {
                'pulse_width': pw,
                'duty_cycle': dc,
                'number_of_pulses': npulses,
                'amplitude_sq_a1': atop,
                'amplitude_sq_a2': abot,
                'ramp_width': rw,
                'amplitude_ramp': aramp,
                'length_top': ltop,
                'sample_rate_red_factor': red_factor
            }
        except ValueError:
            messagebox.showerror("Invalid Input", "Make sure all fields contain valid numbers.")
            return None

    def plot_waveform(self):
        p = self._get_params()
        if not p: return
        
        try:
            vt = stimulus_wf(**p)
            self.current_wf = vt
            self.current_filtered = vt.filter_file_data(window_pts=20)
            
            self.ax.clear()
            
            # Calculate indices to show last 2 pulses + entire ramp section
            pulse_len = len(vt.t_pulse)
            samples_per_cycle = vt.number_of_sample_in_periode
            start_idx = max(0, pulse_len - 2 * samples_per_cycle)
            
            # Slice the data for preview
            view_time = vt.time[start_idx:]
            view_wf = self.current_filtered[start_idx:start_idx + len(view_time)]
            
            self.ax.plot(view_time, view_wf, label='Filtered Waveform (Last 2 pulses + Ramps)')
            
            self.ax.grid(linestyle='--', linewidth=1)
            self.ax.set_title('Waveform Preview (Verification View)')
            self.ax.set_xlabel('Time (s)')
            self.ax.set_ylabel('Amplitude (Unnormalized)')
            self.ax.legend()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Failed to calculate waveform: {str(e)}")

    def export_arb(self):
        p = self._get_params()
        if not p: return

        save_dir = filedialog.askdirectory(title="Select Destination Folder")
        if not save_dir:
            return

        try:
            vt = self.current_wf if self.current_wf else stimulus_wf(**p)
            pw_us = int(float(self.pulse_width_var.get()))
            dc_pct = int(float(self.duty_cycle_var.get()))
            top_v = int(float(self.amp_top_var.get()))
            bot_v = int(float(self.amp_bottom_var.get()))
            
            name = f"{int(vt.number_of_pulses)}pulses_{pw_us}us_pulse_dc{dc_pct}percent_{top_v}Vtop{bot_v}V"
            path1, path2 = vt.create_file(save_dir, name=name)
            
            messagebox.showinfo("Success", f"Successfully exported ARB files:\n\n{path1}\n{path2}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export files: {str(e)}")

    def upload_to_instrument(self):
        p = self._get_params()
        if not p: return

        try:
            vt = self.current_wf if self.current_wf else stimulus_wf(**p)
            # Keysight 33500 series expects 16-bit integers
            data_to_send = np.around(vt.filter_file_data(window_pts=20), decimals=0).astype('int16')
            
            # The convolution adds window_pts-1 samples. We'll clip it to match the time vector if strictly necessary, 
            # but usually it's better to send the whole filtered tail.
            effective_srate = vt.sample_rate / vt.sample_rate_red_factor
            
            upload_arb_binary(data_to_send, arb_name="TEMP_ARB", sample_rate=effective_srate)
            # messagebox.showinfo("Success", "Waveform uploaded via SCPI to Signal Generator volatile memory.")
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload to instrument: {str(e)}")
