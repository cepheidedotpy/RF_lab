### Thursday, 19 February 2026

**Docker Installation Issue - Hyper-V Enablement**
- **Issue:** Unable to install Docker Desktop due to an error enabling the `Microsoft-Hyper-V` feature via DISM, with the error message "DISM could not be initialized in the local folder." This suggests a problem with Windows system files or DISM itself. Command-line attempts to repair system files and enable Hyper-V were unsuccessful due to administrator privilege issues in the execution environment.
- **Resolution (Suggested):** User instructed to enable Hyper-V manually through the Windows Graphical User Interface (GUI):
    1.  Open "Turn Windows features on or off" (`optionalfeatures.exe`).
    2.  Check the "Hyper-V" box (including "Hyper-V Management Tools" and "Hyper-V Platform").
    3.  Click OK and restart the computer if prompted.
- **Next Step:** User to restart PC and attempt Docker installation again.

### Tuesday, 20 January 2026

**Cycling Test - Clear Previous Data**
- **Issue:** Cycling axes were not clearing previous data between test runs.
- **Fix:** Modified `dev/main.py`. The `cycling_test` method now resets `self.file_df` to an empty Pandas DataFrame before starting a new test, ensuring a clean plot for each run. `self.update_cycling_plot()` is called after clearing `self.file_df`.

**Cycling Test - Stop Functionality (Keyboard Interrupt -> Stop Button)**
- **Issue:** The cycling test lacked a reliable way to be interrupted by the user. An initial attempt was made to implement a keyboard interrupt using the Escape key.
- **Attempted Keyboard Interrupt (Escape Key):**
    - Introduced `self.stop_event = threading.Event()` in `dev/main.py` to signal a stop request.
    - Modified `on_escape_press` in `dev/main.py` to set this event.
    - Passed the `stop_event` to `scripts_and_functions.cycling_sequence_with_escape_interrupt` in `dev/scripts_and_functions.py`.
    - In `dev/scripts_and_functions.py`, the main loop was updated to check `stop_event.is_set()` and break if true. `app.update_idletasks()` was temporarily added for debugging Tkinter event processing in threads.
    - **Outcome:** This approach proved problematic due to Tkinter's event handling in multi-threaded contexts and led to `SyntaxError` (due to an indentation error introduced by the agent during a `replace` call) and `AttributeError` (due to accidental deletion of `configure_window` method during `on_escape_press` method removal). The keyboard interrupt was not consistently registered.
- **Implemented Stop Button (Replaced Keyboard Interrupt):**
    - **Reverted all changes related to the `threading.Event` based keyboard interrupt:** All modifications in both `dev/main.py` and `dev/scripts_and_functions.py` concerning `self.stop_event`, `on_escape_press`, `app.update_idletasks()`, and related debug statements were reverted. The original `self.stop_requested` boolean flag was reinstated as the primary stop mechanism. The accidentally deleted `configure_window` method was re-added to `dev/main.py`.
    - **New Stop Button Implementation:**
        - Added a new method `stop_cycling_test()` to `dev/main.py`. This method sets `self.stop_requested = True`.
        - A "Stop Cycling" button was added to the `gui_components/cycling_test_window.py` GUI, with its command linked to `self.app.stop_cycling_test()`.
    - **Outcome:** The stop button functionality is now successfully implemented and working as intended, allowing users to gracefully interrupt the cycling test.

# Changes Log

## 2025-11-13

### `main.py` modifications:

1.  **`configure_window` function:**
    *   **Description:** Added `justify='center'` to the `TButton` style to ensure button text is centered, addressing the user's feedback about uncentered buttons.
    *   **Old Code:**
        ```python
                s.configure('TButton', anchor='center')
        ```
    *   **New Code:**
        ```python
                s.configure('TButton', anchor='center', justify='center')
        ```

2.  **`setup_power_measurement` function:**
    *   **Description:** Added `grid_columnconfigure` calls with `weight=1` to relevant columns within various frames to ensure buttons in the same column have uniform size.
    *   **Old Code (excerpt):**
        ```python
                frame_test_power_measurement = ttk.Frame(frame_power_meas_graph)
                frame_test_power_measurement.pack(anchor='nw')
        ```
    *   **New Code (excerpt):**
        ```python
                frame_test_power_measurement = ttk.Frame(frame_power_meas_graph)
                frame_test_power_measurement.pack(anchor='nw')

                frame_power_compo_info.grid_columnconfigure(2, weight=1)
                frame_power_meas.grid_columnconfigure(1, weight=1)
                frame_power_measurement_signal_generator.grid_columnconfigure(0, weight=1)
                frame_power_meas_powermeter.grid_columnconfigure(0, weight=1)
                frame_power_meas_rf_gen.grid_columnconfigure(0, weight=1)
        ```

3.  **`setup_pull_in_measurement_pulsed` function:**
    *   **Description:** Added `grid_columnconfigure` calls with `weight=1` to relevant columns within various frames for uniform button sizing.
    *   **Old Code (excerpt):**
        ```python
                frame_test_pulsed_pull_in_oscilloscope = add_label_frame(tab=window,
                                                                         frame_name='Oscilloscope & RF Gen', col=0,
                                                                         row=2,
                                                                         row_span=1)
        ```
    *   **New Code (excerpt):**
        ```python
                frame_test_pulsed_pull_in_oscilloscope = add_label_frame(tab=window,
                                                                         frame_name='Oscilloscope & RF Gen', col=0,
                                                                         row=2,
                                                                         row_span=1)
                frame_test_pulsed_pull_in_comp_info.grid_columnconfigure(2, weight=1)
                # frame_pulsed_signal_gen_measurement.grid_columnconfigure(3, weight=1)
                frame_test_pulsed_pull_in_oscilloscope.grid_columnconfigure(0, weight=1)
                frame_test_pulsed_pull_in_gen_controls.grid_columnconfigure(0, weight=1)
                frame_test_pulsed_pull_in_gen_controls.grid_columnconfigure(1, weight=1)
        ```

4.  **`setup_cycling_measurement` function:**
    *   **Description:** Added `grid_columnconfigure` calls with `weight=1` to relevant columns within various frames for uniform button sizing.
    *   **Old Code (excerpt):**
        ```python
                frame_osc_toolbar = ttk.Frame(frame_cycling_monitor, style=default_style)
                frame_osc_toolbar.pack(anchor='nw')
        ```
    *   **New Code (excerpt):**
        ```python
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
        ```

5.  **`setup_snp_measurement` function:**
    *   **Description:** Added `grid_columnconfigure` calls with `weight=1` to relevant columns within various frames for uniform button sizing.
    *   **Old Code (excerpt):**
        ```python
                frame_test_snp_measurement = ttk.Frame(frame_snp_measurement)
                frame_test_snp_measurement.pack(anchor='nw')
        ```
    *   **New Code (excerpt):**
        ```python
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
        ```

6.  **`setup_pull_in_measurement` function:**
    *   **Description:** Added `grid_columnconfigure` calls with `weight=1` to relevant columns within various frames for uniform button sizing.
    *   **Old Code (excerpt):**
        ```python
                frame_test_measurement = ttk.Frame(frame_test_pull_in_measurement)
                frame_oscilloscope = add_label_frame(window, frame_name='Oscilloscope & RF Gen', col=0, row=2,
                                                     row_span=1)
        ```
    *   **New Code (excerpt):**
        ```python
                frame_test_measurement = ttk.Frame(frame_test_pull_in_measurement)
                frame_oscilloscope = add_label_frame(window, frame_name='Oscilloscope & RF Gen', col=0, row=2,
                                                     row_span=1)

                frame_test_pull_in_comp_info.grid_columnconfigure(2, weight=1)
                # frame_signal_gen_measurement.grid_columnconfigure(3, weight=1)
                frame_oscilloscope.grid_columnconfigure(0, weight=1)
                frame_test_pull_in_gen_controls.grid_columnconfigure(0, weight=1)
                frame_test_pull_in_gen_controls.grid_columnconfigure(1, weight=1)
        ```

7.  **`setup_pull_in_display_tab` function:**
    *   **Description:** Corrected indentation of `add_label` calls and ensured `grid_columnconfigure` calls are placed after frame definition to resolve `IndentationError` and `NameError`.
    *   **Old Code (excerpt):**
        ```python
                frame_v_pull_in_dir = add_label_frame(window, frame_name='Vpull-in Directory', col=0,
                                                      row=0)  # s2p Frame
                frame_v_pull_in_dir.grid_columnconfigure(3, weight=1)
                frame_v_pull_in_dir.grid_columnconfigure(5, weight=1)
                frame_v_pull_in_graph = add_label_frame(window, frame_name='Graph', col=0, row=3)  # s2p Frame
                frame_v_pull_in_sliders = add_label_frame(window, frame_name='Voltage limit', col=0, row=4)
                frame_v_pull_in_display = add_label_frame(window, frame_name='Pull-in Display', col=0, row=1)

                # Adding entry for file directory
                self.entered_var_txt = add_entry(frame_v_pull_in_dir, text_var=self.pull_in_dir_name, width=70, col=2,
                                                 row=1)

                file_txt = filetypes_dir(self.entered_var_txt.get())[2]
                self.txt_file_name_combobox = add_combobox(frame_v_pull_in_dir, text=file_txt, col=2, row=2, width=100)

                # Adding buttons
                self.update_pull_in_button = add_button(tab=frame_v_pull_in_dir, button_name=' Update Files ',
                                                        command=lambda: [
                                                            update_entries(directory=self.entered_var_txt.get(),
                                                                           combobox=self.txt_file_name_combobox,
                                                                           filetype='.txt'),
                                                            update_button(self.update_pull_in_button)],
                                                        col=3, row=1)
                add_button(frame_v_pull_in_dir, button_name='Exit', command=window.destroy, col=5, row=1).grid_anchor('e')
                add_button(frame_v_pull_in_dir, button_name='Plot', command=lambda: [self.plot_v_pull_in(),
                                                                                     self.calculate_pull_in_out_voltage()],
                           col=3, row=3)
                add_button(frame_v_pull_in_dir, button_name='Delete Graphs', command=self.delete_axs_vpullin, col=3,
                           row=2)
        ```
    *   **New Code (excerpt):**
        ```python
                frame_v_pull_in_dir = add_label_frame(window, frame_name='Vpull-in Directory', col=0,
                                                      row=0)  # s2p Frame
                frame_v_pull_in_dir.grid_columnconfigure(3, weight=1)
                frame_v_pull_in_dir.grid_columnconfigure(5, weight=1)
                frame_v_pull_in_graph = add_label_frame(window, frame_name='Graph', col=0, row=3)  # s2p Frame
                frame_v_pull_in_in_sliders = add_label_frame(window, frame_name='Voltage limit', col=0, row=4)
                frame_v_pull_in_display = add_label_frame(window, frame_name='Pull-in Display', col=0, row=1)

                add_label(frame_v_pull_in_dir, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                          ipady=tab_pad_x)
                add_label(frame_v_pull_in_dir, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                                     ipady=tab_pad_x)

                # Adding entry for file directory
                self.entered_var_txt = add_entry(frame_v_pull_in_dir, text_var=self.pull_in_dir_name, width=70, col=2,
                                                 row=1)

                file_txt = filetypes_dir(self.entered_var_txt.get())[2]
                self.txt_file_name_combobox = add_combobox(frame_v_pull_in_dir, text=file_txt, col=2, row=2, width=100)

                # Adding buttons
                self.update_pull_in_button = add_button(tab=frame_v_pull_in_dir, button_name=' Update Files ',
                                                        command=lambda: [
                                                            update_entries(directory=self.entered_var_txt.get(),
                                                                           combobox=self.txt_file_name_combobox,
                                                                           filetype='.txt'),
                                                                           update_button(self.update_pull_in_button)],
                                                        col=3, row=1)
                add_button(frame_v_pull_in_dir, button_name='Exit', command=window.destroy, col=5, row=1).grid_anchor('e')
                add_button(frame_v_pull_in_dir, button_name='Plot', command=lambda: [self.plot_v_pull_in(),
                                                                                     self.calculate_pull_in_out_voltage()],
                           col=3, row=3)
                add_button(frame_v_pull_in_dir, button_name='Delete Graphs', command=self.delete_axs_vpullin, col=3,
                           row=2)
        ```

8.  **`setup_s2p_display_tab` function:**
    *   **Description:** Corrected indentation of `add_label` calls and ensured `grid_columnconfigure` calls are placed after frame definition to resolve `IndentationError` and `NameError`.
    *   **Old Code (excerpt):**
        ```python
                frame_s2p_dir = add_label_frame(window, 's2p Directory', 0, 0)  # s2p Frame
                frame_s2p_display = add_label_frame(window, frame_name='s2p Display', col=0, row=1)
                frame_s2p_sliders = add_label_frame(window, frame_name='Frequency Range', col=0, row=2)

                frame_s2p_dir.grid_columnconfigure(3, weight=1)
                frame_s2p_dir.grid_columnconfigure(5, weight=1)

                # Adding String variables
        ```
    *   **New Code (excerpt):**
        ```python
                frame_s2p_dir = add_label_frame(window, 's2p Directory', 0, 0)  # s2p Frame
                frame_s2p_dir.grid_columnconfigure(3, weight=1)
                frame_s2p_dir.grid_columnconfigure(5, weight=1)
                frame_s2p_display = add_label_frame(window, frame_name='s2p Display', col=0, row=1)
                frame_s2p_sliders = add_label_frame(window, frame_name='Frequency Range', col=0, row=2)

                add_label(frame_s2p_dir, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_x)
                add_label(frame_s2p_dir, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                               ipady=tab_pad_x)

                # Adding String variables
        ```

9.  **`setup_s3p_display_tab` function:**
    *   **Description:** Corrected indentation of `add_label` calls and ensured `grid_columnconfigure` calls are placed after frame definition to resolve `IndentationError` and `NameError`.
    *   **Old Code (excerpt):**
        ```python
                frame_s3p_dir = add_label_frame(window, 's3p Directory', 0, 0)  # s3p Frame
                frame_s3p_display = add_label_frame(window, frame_name='s3p Display', col=0, row=1)
                frame_s3p_sliders = add_label_frame(window, frame_name='Frequency Range', col=0, row=2)

                frame_s3p_dir.grid_columnconfigure(3, weight=1)
                frame_s3p_dir.grid_columnconfigure(5, weight=1)

                # Adding String variables
        ```
    *   **New Code (excerpt):**
        ```python
                frame_s3p_dir = add_label_frame(window, 's3p Directory', 0, 0)  # s3p Frame
                frame_s3p_dir.grid_columnconfigure(3, weight=1)
                frame_s3p_dir.grid_columnconfigure(5, weight=1)
                frame_s3p_display = add_label_frame(window, frame_name='s3p Display', col=0, row=1)
                frame_s3p_sliders = add_label_frame(window, frame_name='Frequency Range', col=0, row=2)

                add_label(frame_s3p_dir, label_name='Directory', col=1, row=1).grid(sticky='e', ipadx=tab_pad_x,
                                                                                    ipady=tab_pad_x)
                add_label(frame_s3p_dir, label_name='File', col=1, row=2).grid(sticky='e', ipadx=tab_pad_x,
                                                                               ipady=tab_pad_x)

                # Adding String variables
        ```

## 2025-12-18

### `dev/scripts_and_functions.py` modifications:

1.  **Bug Fix: RF Generator `ALC unlocked` error**
    *   **Description:** The RF generator was encountering an `ALC unlocked` error because its output was turned ON before a valid power level was set. This led to a "Settings conflict;Pep value greater than defined limit" error when `powermeter_trace_acquisition_sequence` was called.
    *   **Change:** Modified `powermeter_trace_acquisition_sequence` to query the RF generator's power limit (`SOUR:POW:LIM:AMPL?`), set the immediate power level to `limit - 1 dBm` (with a fallback to -20 dBm if querying fails) *before* turning on the output.

2.  **New Function: `set_rf_power(power: float)`**
    *   **Description:** Added a new utility function to programmatically set the RF generator's power level.
    *   **Change:** Implemented `set_rf_power` which sends the `SOURce:POWer:LEVel:IMMediate:AMPLitude {power}DBM` command to the RF generator.

### `gui_components/time_domain_power_test_window.py` modifications:

1.  **New Feature: Time Domain Power Sweep**
    *   **Description:** Implemented a new function `launch_time_domain_power_sweep` to perform a power sweep in the time domain, acquiring and plotting traces for each power step, and saving the results to a CSV file.
    *   **Change:**
        *   Added `import time` and `import pandas as pd`.
        *   Created `launch_time_domain_power_sweep` method:
            *   Reads min, max, and step power from GUI inputs (`self.rf_gen_min_power`, `self.rf_gen_max_power`, `self.rf_gen_step`).
            *   Clears existing plots.
            *   Iterates through power levels, calling `scripts_and_functions.set_rf_power()` and `scripts_and_functions.powermeter_trace_acquisition_sequence()`.
            *   Plots acquired traces with unique labels on the input/output axes.
            *   Stores trace data in a list of pandas DataFrames (long format: `power_level`, `time`, `power`, `channel`).
            *   Concatenates DataFrames and saves them to a CSV file (e.g., `Project_Name-Cell_Name-Reticule-Device_nameV_power_sweep.csv`) in the specified directory (`self.directory.get()`).
            *   Adds legends to plots and redraws the canvas.
            *   Clears plots after a 5-second delay.
        *   Modified `create_widgets` to make `rf_gen_min_power`, `rf_gen_max_power`, and `rf_gen_step` instance variables (`self.rf_gen_min_power`, etc.).
        *   Re-wired the "Launch Test" button command to `self.launch_time_domain_power_sweep`.
