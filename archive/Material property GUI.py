import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import skrf as rf
from scipy.constants import epsilon_0, pi


class PermittivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Permittivity Extractor")
        self.create_widgets()

    def create_widgets(self):
        # Input panel
        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.file1_var = tk.StringVar()
        self.file2_var = tk.StringVar()
        self.ylim_eps_entry_var = tk.StringVar(value='0, 40')
        self.ylim_tan_entry_var = tk.StringVar(value='0, 1')
        self.ylim_q_entry_var = tk.StringVar(value='0, 20')

        self.create_file_input(frame_inputs, "S-Parameter File (r1):", 0, self.file1_var)
        self.create_file_input(frame_inputs, "S-Parameter File (r2):", 1, self.file2_var)

        self.r1_entry = self.create_labeled_entry(frame_inputs, "Radius r1 (µm):", 2)
        self.r2_entry = self.create_labeled_entry(frame_inputs, "Radius r2 (µm):", 3)
        self.d_entry = self.create_labeled_entry(frame_inputs, "Dielectric Thickness (nm):", 4)
        self.Rs_entry = self.create_labeled_entry(frame_inputs, "Sheet Resistance (Ω/sq):", 5)

        self.ylim_eps_entry = self.create_labeled_entry(frame_inputs, "ε' Y-Limits (min,max):", 6)
        self.ylim_eps_entry.config(textvariable=self.ylim_eps_entry_var)
        self.ylim_tan_entry = self.create_labeled_entry(frame_inputs, "tanδ Y-Limits (min,max):", 7)
        self.ylim_tan_entry.config(textvariable=self.ylim_tan_entry_var)
        self.ylim_q_entry = self.create_labeled_entry(frame_inputs, "Q-Factor Y-Limits (min,max):", 8)
        self.ylim_q_entry.config(textvariable=self.ylim_q_entry_var)

        tk.Button(frame_inputs, text="Run", command=self.on_run).grid(row=9, column=1, pady=5)
        tk.Button(frame_inputs, text="Exit", command=self.root.quit).grid(row=9, column=2, pady=5)

        # Plot area
        self.fig, self.axs = plt.subplots(3, 1, figsize=(7, 9))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def create_file_input(self, parent, label, row, var):
        tk.Label(parent, text=label).grid(row=row, column=0, sticky='e')
        entry = tk.Entry(parent, textvariable=var, width=50)
        entry.grid(row=row, column=1)
        tk.Button(parent, text="Browse", command=lambda: self.select_file(var)).grid(row=row, column=2)

    def create_labeled_entry(self, parent, label, row):
        tk.Label(parent, text=label).grid(row=row, column=0, sticky='e')
        entry = tk.Entry(parent)
        entry.grid(row=row, column=1)
        return entry

    def select_file(self, var):
        filename = filedialog.askopenfilename(filetypes=[("Touchstone files", "*.s1p")])
        if filename:
            var.set(filename)

    def on_run(self):
        try:
            file1 = self.file1_var.get()
            file2 = self.file2_var.get()
            r1 = float(self.r1_entry.get()) * 1e-6
            r2 = float(self.r2_entry.get()) * 1e-6
            d = float(self.d_entry.get()) * 1e-9
            Rs = float(self.Rs_entry.get())

            ylim_eps = self.parse_ylim(self.ylim_eps_entry.get())
            ylim_tan = self.parse_ylim(self.ylim_tan_entry.get())
            ylim_q = self.parse_ylim(self.ylim_q_entry.get())

            self.calculate_and_plot(file1, file2, r1, r2, d, Rs, ylim_eps, ylim_tan, ylim_q)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def parse_ylim(self, text):
        try:
            if text.strip() == "":
                return None
            parts = list(map(float, text.split(',')))
            if len(parts) != 2:
                raise ValueError("Enter limits as min,max")
            return parts
        except Exception:
            raise ValueError(f"Invalid Y-axis limits: {text}")

    def calculate_and_plot(self, file1, file2, r1, r2, d, Rs, ylim_eps, ylim_tan, ylim_q):
        ntw1 = rf.Network(file1)
        ntw2 = rf.Network(file2)

        freq = ntw1.f  # frequency in Hz
        freq_ghz = freq / 1e9
        omega = 2 * pi * freq

        Z1 = ntw1.z[:, 0, 0]
        Z2 = ntw2.z[:, 0, 0]

        R1, X1 = Z1.real, Z1.imag
        R2, X2 = Z2.real, Z2.imag

        dR_2 = R1 - R2 - (Rs / (2 * pi)) * np.log(r2 / r1)

        dR = R1 - R2
        dX = X2 - X1
        geom_factor = (1 / r1 ** 2 - 1 / r2 ** 2)

        eps_real_2 = (dX * d * geom_factor) / (omega * pi * epsilon_0 * (dR_2 ** 2 + dX ** 2))
        eps_imag_2 = (dR_2 * d * geom_factor) / ((omega * pi * epsilon_0) * (dR_2 ** 2 + dX ** 2))
        eps_real = d * geom_factor * (1 / (epsilon_0 * pi * omega * dX))

        tan_delta = dR / dX
        tan_delta_2 = eps_imag_2 / eps_real_2

        Q_factor = 1 / tan_delta

        # Clear previous plots
        for ax in self.axs:
            ax.clear()

        # Real permittivity
        self.axs[0].plot(freq_ghz, eps_real, label='real permittivity', color='black')
        self.axs[0].plot(freq_ghz, eps_real_2, label='real permittivity with sheet resistance', color='gray')
        self.axs[0].plot(freq_ghz, eps_imag_2, label='imaginary permittivity with sheet resistance', color='darkblue')
        self.axs[0].set_title("Real Permittivity vs Frequency")
        self.axs[0].set_xlabel("Frequency (GHz)")
        self.axs[0].set_ylabel("ε'")
        self.axs[0].set(xlim=[0, 20])
        self.axs[0].grid()
        self.axs[0].legend()
        if ylim_eps:
            self.axs[0].set_ylim(ylim_eps)

        # Loss tangent
        self.axs[1].plot(freq_ghz, tan_delta, label='loss tangent', color='black')
        self.axs[1].plot(freq_ghz, tan_delta_2, label='loss tangent with sheet resistance', color='darkblue')
        self.axs[1].set_title("Loss Tangent vs Frequency")
        self.axs[1].set_xlabel("Frequency (GHz)")
        self.axs[1].set_ylabel("tan δ")
        self.axs[1].set(xlim=[0, 20])
        self.axs[1].grid()
        self.axs[1].legend()
        if ylim_tan:
            self.axs[1].set_ylim(ylim_tan)

        # Q-factor
        self.axs[2].plot(freq_ghz, Q_factor, color='black')
        self.axs[2].set_title("Q Factor vs Frequency")
        self.axs[2].set_xlabel("Frequency (GHz)")
        self.axs[2].set_ylabel("Q")
        self.axs[2].set(xlim=[0, 20])
        self.axs[2].grid()
        if ylim_q:
            self.axs[2].set_ylim(ylim_q)

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = PermittivityApp(root)
    root.mainloop()
