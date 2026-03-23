import tkinter as tk
from tkinter import filedialog, simpledialog, ttk, colorchooser
import skrf as rf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# plt.style.use('seaborn-v0_8-darkgrid')  # Scientific style


# plt.style.use('fivethirtyeight')  # Scientific style
# plt.style.use('ggplot')  # Scientific style


class SParamPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("S-Parameter Viewer")
        self.networks = []
        self.labels = []
        self.colors = []
        self.marker_styles = []
        self.marker_spacings = []
        self.marker_colors = []
        self.show_markers = []
        self.default_font = ("Arial", 10)
        self.last_removed = None  # store last removed plot info
        self.inset_ax = None

        # UI Layout Containers
        section_title = tk.Label(root, text="Edit Plot Settings", font=("Arial", 10, "bold"), anchor="w")
        section_title.pack(fill='x', padx=5, pady=(10, 0))

        top_frame = tk.Frame(root)
        top_frame.pack(fill='x', pady=5)

        mid_frame = tk.Frame(root)
        mid_frame.pack(fill='x', pady=5)

        edit_frame = tk.Frame(root)
        edit_frame.pack(fill='x', pady=5)

        self.remove_button = tk.Button(edit_frame, text="Remove Selected Plot", command=self.remove_selected_plot)
        self.remove_button.pack(side='left', padx=10)

        self.status_label = tk.Label(root, text="No file selected", fg="blue", anchor="w", relief="sunken")
        self.status_label.pack(fill='x', padx=5, pady=2)

        self.undo_button = tk.Button(edit_frame, text="Undo Remove", command=self.undo_remove)
        self.undo_button.pack(side='left', padx=5)
        self.undo_button.config(state='disabled')

        # Marker options
        marker_frame = tk.Frame(root)
        marker_frame.pack(fill='x', pady=5)

        self.marker_var = tk.IntVar()
        self.marker_check = tk.Checkbutton(marker_frame, text="Show Markers", variable=self.marker_var,
                                           command=self.update_marker_settings)
        self.marker_check.pack(side='left', padx=5)

        tk.Label(marker_frame, text="Style:").pack(side='left')
        self.marker_style = ttk.Combobox(marker_frame, values=['o', 's', '^', 'x', '+', '*', 'D'], width=5,
                                         state="readonly")
        self.marker_style.set('o')
        self.marker_style.pack(side='left', padx=5)

        tk.Label(marker_frame, text="Spacing:").pack(side='left')
        self.marker_spacing = tk.Spinbox(marker_frame, from_=1, to=100, width=5)
        self.marker_spacing.pack(side='left', padx=5)

        self.marker_color_btn = tk.Button(marker_frame, text="Marker Color", command=self.choose_marker_color)
        self.marker_color_btn.pack(side='left', padx=5)

        freq_frame = tk.Frame(root)
        freq_frame.pack(fill='x', pady=5)

        tk.Label(freq_frame, text="Freq (GHz):").pack(side='left', padx=5)
        self.freq_entry = tk.Entry(freq_frame, width=10)
        self.freq_entry.pack(side='left', padx=5)

        self.freq_button = tk.Button(freq_frame, text="Get Magnitude", command=self.get_magnitude_at_freq)
        self.freq_button.pack(side='left', padx=5)

        self.freq_result_label = tk.Label(freq_frame, text="", fg="darkgreen", anchor="w")
        self.freq_result_label.pack(side='left', padx=10)

        zoom_frame = tk.Frame(root)
        zoom_frame.pack(fill='x', pady=5)

        self.zoom_var = tk.IntVar()
        self.zoom_check = tk.Checkbutton(zoom_frame, text="Enable Zoom Inset", variable=self.zoom_var,
                                         command=self.toggle_zoom_inset)
        self.zoom_check.pack(side='left', padx=5)

        # Input fields for frequency and amplitude ranges
        for label_text, attr in [
            ("Min Freq (GHz):", "min_freq_entry"),
            ("Max Freq (GHz):", "max_freq_entry"),
            ("Min Amp (dB):", "min_amp_entry"),
            ("Max Amp (dB):", "max_amp_entry")
        ]:
            tk.Label(zoom_frame, text=label_text).pack(side='left')
            setattr(self, attr, tk.Entry(zoom_frame, width=6))
            getattr(self, attr).pack(side='left', padx=2)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill='x', pady=5)

        # Top: Load button
        self.load_button = tk.Button(top_frame, text="Load S-Parameter File(s)", command=self.load_files)
        self.load_button.pack(pady=2)

        # Middle: S-parameter selector
        tk.Label(mid_frame, text="Select S-Parameter:").pack(side='left', padx=5)
        self.sparam_selector = ttk.Combobox(mid_frame, values=[], state="readonly", width=10)
        self.sparam_selector.bind("<<ComboboxSelected>>", self.plot_selected_sparam)
        self.sparam_selector.pack(side='left', padx=5)

        # Plot selector
        tk.Label(mid_frame, text="Select Plot:").pack(side='left', padx=5)
        self.plot_selector = ttk.Combobox(mid_frame, values=[], state="readonly", width=20)
        self.plot_selector.bind("<<ComboboxSelected>>", self.update_label_color_ui)
        self.plot_selector.pack(side='left', padx=5)

        # Editing: label entry and color button
        tk.Label(edit_frame, text="Edit Label:").pack(side='left', padx=5)
        self.label_entry = tk.Entry(edit_frame)
        self.label_entry.pack(side='left', padx=5)
        self.update_label_button = tk.Button(edit_frame, text="Update Label", command=self.update_label)
        self.update_label_button.pack(side='left', padx=5)
        self.color_button = tk.Button(edit_frame, text="Choose Color", command=self.choose_color)
        self.color_button.pack(side='left', padx=5)

        # Canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Exit Button
        self.exit_button = tk.Button(bottom_frame, text="Exit", command=self.root.quit)
        self.exit_button.pack(pady=5)

        self.save_button = tk.Button(bottom_frame, text="Save Figure", command=self.save_figure)
        self.save_button.pack(pady=2)

    def load_files(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("Touchstone files", "*.s*p")])
        for filepath in filepaths:
            net = rf.Network(filepath)
            label = simpledialog.askstring("Input", f"Enter label for {filepath}:", parent=self.root)
            label = label if label else filepath  # fallback to filename
            color = None  # Default color
            self.networks.append(net)
            self.labels.append(label)
            self.colors.append(color)
            self.marker_styles.append('o')
            self.marker_spacings.append(1)
            self.marker_colors.append(None)
            self.show_markers.append(False)
            if self.labels:
                self.status_label.config(text=f"Working with: {self.labels[0]} ({self.networks[0].name})")

        if not self.networks:
            return

        # Extract S-parameters from the first network (assumes all same format)
        n_ports = self.networks[0].number_of_ports
        sparams = [f"S{i + 1}{j + 1}" for i in range(n_ports) for j in range(n_ports)]
        self.sparam_selector["values"] = sparams
        self.sparam_selector.set(sparams[0])

        self.plot_selector["values"] = self.labels
        if self.labels:
            self.plot_selector.set(self.labels[0])
            self.label_entry.delete(0, tk.END)
            self.label_entry.insert(0, self.labels[0])

        self.plot_selected_sparam()

    def plot_selected_sparam(self, event=None):
        selection = self.sparam_selector.get()
        if not selection or not self.networks:
            return

        i, j = int(selection[1]) - 1, int(selection[2]) - 1

        self.ax.clear()
        for idx, (net, label, color) in enumerate(zip(self.networks, self.labels, self.colors)):
            freq = net.f / 1e9  # GHz
            s_db = net.s_db[:, i, j]

            kwargs = {'label': label}
            if color:
                kwargs['color'] = color

            if self.show_markers[idx]:
                marker = self.marker_styles[idx]
                spacing = self.marker_spacings[idx]
                marker_color = self.marker_colors[idx]
                kwargs['marker'] = marker
                kwargs['markevery'] = int(spacing)
                if marker_color:
                    kwargs['markerfacecolor'] = marker_color
                    kwargs['markeredgecolor'] = marker_color

            self.ax.plot(freq, s_db, **kwargs)

        self.ax.set_title(f"Magnitude of {selection} (dB)")
        self.ax.set_xlabel("Frequency (GHz)")
        self.ax.set_ylabel("dB")
        self.ax.grid(True)
        self.ax.legend()

        # Inset zoom logic
        if self.zoom_var.get():
            try:
                min_f = float(self.min_freq_entry.get())
                max_f = float(self.max_freq_entry.get())
                min_a = float(self.min_amp_entry.get())
                max_a = float(self.max_amp_entry.get())
            except ValueError:
                self.inset_ax = None
                self.canvas.draw()
                return

            from mpl_toolkits.axes_grid1.inset_locator import inset_axes

            # Clear previous inset if any
            if self.inset_ax:
                self.inset_ax.remove()
                self.inset_ax = None

            self.inset_ax = inset_axes(self.ax, width="30%", height="30%", loc='upper right')
            for idx, (net, label, color) in enumerate(zip(self.networks, self.labels, self.colors)):
                freq = net.f / 1e9
                s_db = net.s_db[:, i, j]

                kwargs = {'label': label}
                if color:
                    kwargs['color'] = color

                if self.show_markers[idx]:
                    kwargs['marker'] = self.marker_styles[idx]
                    kwargs['markevery'] = int(self.marker_spacings[idx])
                    if self.marker_colors[idx]:
                        kwargs['markerfacecolor'] = self.marker_colors[idx]
                        kwargs['markeredgecolor'] = self.marker_colors[idx]

                self.inset_ax.plot(freq, s_db, **kwargs)

            self.inset_ax.set_xlim(min_f, max_f)
            self.inset_ax.set_ylim(min_a, max_a)
            self.inset_ax.set_title("Zoom")
            self.inset_ax.grid(True)

        else:
            # Remove inset if toggle is off
            if self.inset_ax:
                self.inset_ax.remove()
                self.inset_ax = None

        self.canvas.draw()

    def update_label_color_ui(self, event=None):
        idx = self.plot_selector.current()
        if idx >= 0:
            # Update label entry with the current label
            self.label_entry.delete(0, tk.END)
            self.label_entry.insert(0, self.labels[idx])

            # Update marker settings
            self.marker_var.set(self.show_markers[idx])
            self.marker_style.set(self.marker_styles[idx])
            self.marker_spacing.delete(0, tk.END)
            self.marker_spacing.insert(0, self.marker_spacings[idx])

            # Update status label with file info
            net = self.networks[idx]
            self.status_label.config(text=f"Working with: {self.labels[idx]} ({net.name})")

    def update_label(self):
        idx = self.plot_selector.current()
        new_label = self.label_entry.get()
        if idx >= 0 and new_label:
            self.labels[idx] = new_label
            self.plot_selector["values"] = self.labels
            self.plot_selector.set(new_label)
            self.update_label_color_ui()  # Reapply all label-related updates
            self.plot_selected_sparam()  # Redraw with updated label

    def choose_color(self):
        idx = self.plot_selector.current()
        if idx >= 0:
            color = colorchooser.askcolor()[1]  # Get hex color
            if color:
                self.colors[idx] = color
                self.plot_selected_sparam()

    def save_figure(self):
        filetypes = [("PNG", "*.png"), ("JPEG", "*.jpg"), ("SVG", "*.svg"), ("PDF", "*.pdf"), ("All files", "*.*")]
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
        if filepath:
            self.figure.savefig(filepath, bbox_inches='tight')

    def update_marker_settings(self):
        idx = self.plot_selector.current()
        if idx >= 0:
            self.show_markers[idx] = bool(self.marker_var.get())
            self.marker_styles[idx] = self.marker_style.get()
            try:
                self.marker_spacings[idx] = int(self.marker_spacing.get())
            except ValueError:
                self.marker_spacings[idx] = 1
            self.plot_selected_sparam()

    def choose_marker_color(self):
        idx = self.plot_selector.current()
        if idx >= 0:
            color = colorchooser.askcolor()[1]
            if color:
                self.marker_colors[idx] = color
                self.plot_selected_sparam()

    def get_magnitude_at_freq(self):
        try:
            freq_ghz = float(self.freq_entry.get())
        except ValueError:
            self.freq_result_label.config(text="Invalid frequency.")
            return

        idx_net = self.plot_selector.current()
        if idx_net < 0 or not self.networks:
            self.freq_result_label.config(text="No network selected.")
            return

        selection = self.sparam_selector.get()
        if not selection:
            self.freq_result_label.config(text="No S-param selected.")
            return

        i, j = int(selection[1]) - 1, int(selection[2]) - 1
        net = self.networks[idx_net]

        # Interpolate the frequency response
        s_db = net.s_db[:, i, j]
        freq = net.f / 1e9  # GHz

        if freq_ghz < freq[0] or freq_ghz > freq[-1]:
            self.freq_result_label.config(text="Freq out of range.")
            return

        import numpy as np
        magnitude = np.interp(freq_ghz, freq, s_db)
        self.freq_result_label.config(text=f"|{selection}| @ {freq_ghz:.2f} GHz = {magnitude:.2f} dB")

    def remove_selected_plot(self):
        idx = self.plot_selector.current()
        if idx < 0 or idx >= len(self.networks):
            return

        # Store removed data for undo
        self.last_removed = {
            "index": idx,
            "network": self.networks.pop(idx),
            "label": self.labels.pop(idx),
            "color": self.colors.pop(idx),
            "marker_style": self.marker_styles.pop(idx),
            "marker_spacing": self.marker_spacings.pop(idx),
            "marker_color": self.marker_colors.pop(idx),
            "show_marker": self.show_markers.pop(idx),
        }

        self.undo_button.config(state='normal')  # Enable Undo button

        if self.labels:
            self.plot_selector["values"] = self.labels
            self.plot_selector.current(min(idx, len(self.labels) - 1))
            self.update_label_color_ui()
        else:
            self.plot_selector["values"] = []
            self.label_entry.delete(0, tk.END)
            self.status_label.config(text="No file selected")

        self.plot_selected_sparam()

    def undo_remove(self):
        if not self.last_removed:
            return

        # Restore data in proper order
        idx = self.last_removed["index"]
        self.networks.insert(idx, self.last_removed["network"])
        self.labels.insert(idx, self.last_removed["label"])
        self.colors.insert(idx, self.last_removed["color"])
        self.marker_styles.insert(idx, self.last_removed["marker_style"])
        self.marker_spacings.insert(idx, self.last_removed["marker_spacing"])
        self.marker_colors.insert(idx, self.last_removed["marker_color"])
        self.show_markers.insert(idx, self.last_removed["show_marker"])

        self.plot_selector["values"] = self.labels
        self.plot_selector.current(idx)
        self.update_label_color_ui()
        self.plot_selected_sparam()

        self.last_removed = None
        self.undo_button.config(state='disabled')

    def toggle_zoom_inset(self):
        self.plot_selected_sparam()


if __name__ == '__main__':
    root = tk.Tk()
    app = SParamPlotterApp(root)
    root.mainloop()
