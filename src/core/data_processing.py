import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, get_window, convolve, find_peaks

def timing_wrapper(func):
    """
    A decorator that times the execution of the given function and
    displays the result in days, hours, minutes, and seconds.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the function
        end_time = time.time()  # Record the end time

        # Calculate elapsed time in seconds
        elapsed_time = end_time - start_time

        # Convert to days, hours, minutes, seconds
        days = int(elapsed_time // (24 * 3600))
        hours = int((elapsed_time % (24 * 3600)) // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = elapsed_time % 60

        # Display the result in a formatted string
        print(f"Execution time for {func.__name__}: "
              f"{days}d {hours}h {minutes}m {seconds:.2f}s")
        return result

    return wrapper

def extract_data(rf_detector_channel, v_bias_channel, ramp_start=0.20383, ramp_stop=0.20437, ramp_start_minus=0.2046,
                 ramp_stop_minus=0.20519, delay=0.2, conversion_coeff=0.047):
    """
    Returns the MEMS Characteristics including Positive & Negative Pull-in voltages,
    Positive & Negative Pull-out voltages, Switching time, isolation and insertion loss variation during
    cycling sequence
    :param rf_detector_channel: Detector channel array
    :param v_bias_channel: Bias channel array
    :param ramp_start: Starting time of the positive ramp
    :param ramp_stop: End time of the positive ramp
    :param ramp_start_minus: Starting time of the negative ramp
    :param ramp_stop_minus: End time of the negative ramp
    :param delay: Input delay of the oscilloscope to position at the end of the cycling waveform
    :param conversion_coeff: Conversion coefficient from power to voltage of the detector
    :return: Dataframe containing all the MEMS characteristics
    """

    delay = float(osc.query('HORizontal:MAIn:DELay:TIMe?'))
    switching_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
    release_time = float(osc.query('MEASUrement:MEAS2:VALue?'))
    amplitude_t0 = float(osc.query('MEASUrement:MEAS4:VALue?'))
    relative_amplitude = amplitude_t0 - float(osc.query('MEASUrement:MEAS4:VALue?'))

    # Insert the get curve data with ramp position to calculate pull_in, pull_out and insertion loss + isolation
    # Assign the different curves to variables
    t = rf_detector_channel[:, 1] + delay
    rf_detector_curve = rf_detector_channel[:, 0]
    v_bias_curve = v_bias_channel[:, 0]

    trigger_offset = int(t.size / (float(osc.query('HORIZONTAL:POSITION?'))))
    # Define a ramp voltage curve to calculate pull in and pull out curve.
    # This is done by time gating using ramp_start and ramp_stop

    t0_ramp = np.where(t > ramp_start)[0][0] + trigger_offset
    t0_plus_rampwidth = list(np.where(t < ramp_stop))[0][-1] + trigger_offset

    # Define a ramp voltage curve to calculate pull in and pull out curve of negative ramp.
    # This is done by time gating using ramp_start_minus and ramp_stop_minus
    t0_ramp_minus = list(np.where(t > ramp_start_minus))[0][0] + trigger_offset
    t0_plus_rampwidth_minus = list(np.where(t < ramp_stop_minus))[0][-1] + trigger_offset

    # We then calculate the index corresponding to the Max voltage of our ramp
    max_positive_bias_index = np.argmax(v_bias_curve)
    min_negative_bias_index = np.argmin(v_bias_curve)

    # From the time gating we extract the ramp voltage curve ascent and descent
    ramp_voltage_curve = v_bias_curve[t0_ramp:t0_plus_rampwidth]
    negative_ramp_voltage_curve = v_bias_curve[t0_ramp_minus:t0_plus_rampwidth_minus]

    # Then comes the definition of an ascent and descent portion of the curves
    ramp_voltage_ascent = v_bias_curve[t0_ramp:max_positive_bias_index]
    ramp_voltage_descent = v_bias_curve[max_positive_bias_index:t0_plus_rampwidth]

    # Same is done for the negative portion of the curve
    ramp_voltage_descent_minus = v_bias_curve[t0_ramp_minus:min_negative_bias_index]
    ramp_voltage_ascent_minus = v_bias_curve[min_negative_bias_index:t0_plus_rampwidth_minus]

    # plt.figure(ramp_voltage_curve, label='ramp_voltage_curve')
    # plt.figure(negative_ramp_voltage_curve, label='negative_ramp_voltage_curve')
    # plt.figure(ramp_voltage_ascent, label='ramp_voltage_ascent')
    # plt.figure(ramp_voltage_descent, label='ramp_voltage_descent')
    # plt.figure(ramp_voltage_descent_minus, label='ramp_voltage_descent_minus')
    # plt.figure(ramp_voltage_ascent_minus, label='ramp_voltage_ascent_minus')
    # plt.legend()
    # plt.show()

    # Calculating the normalization value for the isolation
    normalized_isolation_plus = np.max(3 * rf_detector_curve[t0_ramp: t0_plus_rampwidth] / conversion_coeff)
    normalized_isolation_minus = np.max(
        3 * rf_detector_curve[t0_ramp_minus: t0_plus_rampwidth_minus] / conversion_coeff)

    # iso_ascent is the ascent portion of the rf_detector waveform for positive ramp
    iso_ascent = 3 * rf_detector_curve[
                     t0_ramp: max_positive_bias_index] / conversion_coeff - normalized_isolation_plus
    iso_max_ascent = np.min(iso_ascent)

    # iso_descent is the descent portion of the rf_detector waveform for positive ramp
    iso_descent = 3 * rf_detector_curve[
                      max_positive_bias_index:t0_plus_rampwidth] / conversion_coeff - normalized_isolation_plus
    iso_min_descent = np.min(iso_descent)

    # iso_descent_minus is the descent portion of the rf_detector waveform for negative ramp
    iso_descent_minus = 3 * rf_detector_curve[
                            t0_ramp_minus: min_negative_bias_index] / conversion_coeff - normalized_isolation_minus
    iso_max_descent_minus = np.min(iso_descent_minus)

    # iso_ascent_minus is the ascent portion of the rf_detector waveform for negative ramp
    iso_ascent_minus = (3 * rf_detector_curve[
                            min_negative_bias_index: t0_plus_rampwidth_minus] / conversion_coeff
                        - normalized_isolation_minus)
    iso_min_ascent_minus = np.min(iso_ascent_minus)

    # ==============================================================================
    # Calculation Vpull in as isolation passing below 90% max isolation in dB mark
    # Calculation Vpull out as isolation passing above 90% max isolation in dB mark
    # Positive Pull-in
    pullin_index_pos = int(np.where(iso_ascent <= 0.9 * iso_max_ascent)[0][0])
    Vpullin_plus = round(ramp_voltage_ascent[pullin_index_pos], ndigits=2)
    # Negative Pull-in
    pullin_index_neg = int(np.where(iso_descent_minus <= 0.9 * iso_max_descent_minus)[0][0])
    Vpullin_minus = round(ramp_voltage_descent_minus[pullin_index_neg], ndigits=2)

    tenpercent_iso_plus = round(0.1 * iso_min_descent, ndigits=2)
    ninetypercent_iso_plus = round(0.9 * iso_max_ascent, ndigits=2)
    _100percent_iso_plus = round(iso_min_descent, ndigits=2)

    pullout_index_pos = int(np.where(iso_descent >= 0.1 * iso_min_descent)[0][0])
    vpullout_plus = round(ramp_voltage_descent[pullout_index_pos], ndigits=2)

    pullout_index_neg = int(np.where(iso_ascent_minus >= 0.1 * iso_min_ascent_minus)[0][0])
    vpullout_minus = round(ramp_voltage_ascent_minus[pullout_index_neg], ndigits=2)

    tenpercent_iso_neg = round(0.1 * iso_min_descent, ndigits=2)
    ninetypercent_iso_neg = round(0.9 * iso_max_descent_minus, ndigits=2)

    dict_ = {'vpullin_plus': [Vpullin_plus], 'vpullin_minus': [Vpullin_minus], 'vpullout_plus': [vpullout_plus],
             'vpullout_minus': [vpullout_minus], 'iso_ascent': [ninetypercent_iso_plus],
             'iso_descent_minus': [ninetypercent_iso_neg], 'switching_time': [switching_time],
             'amplitude_variation': [relative_amplitude], 'release_time': [release_time]}
    try:
        mems_characteristics = pd.DataFrame(data=dict_)
    except:
        print('Dataframe creation Error')
    print(mems_characteristics)

    return mems_characteristics

def format_duration(seconds):
    # Ensure the input is a float or integer
    if not isinstance(seconds, (float, int)):
        raise ValueError("Input should be a float or an integer representing seconds.")

    # Calculate the days, hours, minutes, and seconds
    minutes, sec = divmod(seconds, 60)
    hours, min = divmod(minutes, 60)
    days, hrs = divmod(hours, 24)

    # Format the result as d:hh:mm:ss
    formatted_time = f"{int(days):02}d {int(hrs):02}h {int(min):02}m {sec:05.2f}s"

    return formatted_time

def detect_sticking_events(df, thresholds):
    """
    Detect sticking events based on thresholds and append a 'sticking events' column to the dataframe.

    :param df: The dataframe containing the test data.
    :param thresholds: Dictionary with column names as keys and threshold values as values.
    :return: DataFrame with the 'sticking events' column appended.
    """
    sticking_events = []

    for i in range(len(df)):
        event_detected = False
        for col, threshold in thresholds.items():
            if df.at[i, col] > threshold or df.at[i, col] < 0:
                event_detected = True
                break
        sticking_events.append(1 if event_detected else 0)

    df['sticking events'] = sticking_events
    return df

def calculate_actuation_and_release_voltages(v_bias, v_logamp, detector_coefficient=1, step=20):
    """


    Calculates pull-in and pull-out voltages, as well as isolations for both the positive


    and negative bias cycles of a MEMS device based on the second derivative of the log amp voltage.



    Parameters

    ----------



    v_bias : numpy.ndarray

        Numpy array of floats representing the bias voltage applied to the MEMS.



    v_logamp : numpy.ndarray

        Numpy array of floats representing the output of the logarithmic amplifier detector.



    detector_coefficient : float, optional (default=1)

        The coefficient that relates the detector's RF to voltage characteristic, converting the voltage to dB.



    Returns

    -------



    calculations : dict

        A dictionary containing the calculated pull-in and pull-out voltages for both positive and

        negative bias, along with the ascent and descent isolations.

        Structure:

        {

            'vpullin_plus': float,



            'vpullout_plus': float,



            'vpullin_minus': float,



            'vpullout_minus': float,



            'ninetypercent_iso_ascent': float,



            'ninetypercent_iso_descent': float

        }

        :param step:
    """

    # Set the parameters for the Savitzky-Golay filter

    window_length = 31  # Improved smoothing

    polyorder = 4  # Order of the polynomial to fit within each window

    # Compute the first finite difference over the step size

    # This approximates the first derivative of log amp voltage spaced `step` points apart

    v_logamp_t = v_logamp[:-step * 2]

    v_bias_t = v_bias[:-step * 2]

    diff_logamp = (v_logamp_t[step:] - v_logamp_t[:-step])

    # Compute the second finite difference, which approximates the second derivative

    diff_logamp_2 = (diff_logamp[step:] - diff_logamp[:-step])

    # Smooth the original log amplifier voltage data using the Savitzky-Golay filter

    smoothed_v_logamp_pre = savgol_filter(v_logamp_t, window_length, polyorder)

    min_smoothed_v_logamp = np.max(smoothed_v_logamp_pre)

    smoothed_v_logamp = smoothed_v_logamp_pre - min_smoothed_v_logamp

    # Smooth the second derivative (diff_logamp_2) using the same Savitzky-Golay filter

    smoothed_diff_logamp_2_core = savgol_filter(diff_logamp_2, window_length, polyorder)

    # Pad to match original v_bias length for consistent plotting and indexing
    smoothed_diff_logamp_2 = np.zeros(v_bias.shape)
    start_idx = step * 2
    end_idx = start_idx + len(smoothed_diff_logamp_2_core)
    smoothed_diff_logamp_2[start_idx:end_idx] = smoothed_diff_logamp_2_core

    # Initialize variables with default values in case no positive/negative bias is found

    vpullin = np.nan

    vpullout = np.nan

    vpullin_neg = np.nan

    vpullout_neg = np.nan

    ninetypercent_iso_ascent = 0.0

    ninetypercent_iso_descent = 0.0

    # Extracting positive bias values (> 2V) and negative bias values (< -2V)

    positive_bias = np.extract((v_bias > 2), v_bias)

    negative_bias = np.extract((v_bias < -2), v_bias)

    if positive_bias.size > 0:

        # Finding the first index of positive bias in v_bias array

        first_index_pos = np.where(v_bias == positive_bias[0])[0]

        # Finding the index of the maximum positive bias (top of the triangle waveform)

        max_positive_bias_index = np.argmax(positive_bias)

        # Normalizing the log amplifier voltage over the ascent (positive bias portion)

        normalize_iso = np.max(v_logamp[first_index_pos[0]: max_positive_bias_index] / detector_coefficient)

        # Calculate isolation during the positive ascent and descent by normalizing the log amp voltage

        iso_ascent = v_logamp[

                     first_index_pos[0]:first_index_pos[
                                            0] + max_positive_bias_index] / detector_coefficient - normalize_iso

        iso_descent = v_logamp[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(

            positive_bias)] / detector_coefficient - normalize_iso

        # =========================================================================

        # Positive Bias: Calculate pull-in and pull-out voltages using second derivative method

        # =========================================================================

        # Find the maximum and minimum of the second derivative in the positive bias cycle

        # Finding the first index of positive bias in v_bias array

        first_index_pos = np.where(v_bias == positive_bias[0])[0]

        # Finding the index of the maximum positive bias (top of the triangle waveform)

        max_positive_bias_index = np.argmax(positive_bias)

        # Normalizing the log amplifier voltage over the ascent (positive bias portion)

        normalize_iso = np.max(v_logamp[first_index_pos[0]: max_positive_bias_index] / detector_coefficient)

        # Calculate isolation during the positive ascent and descent by normalizing the log amp voltage

        iso_ascent = v_logamp[

                     first_index_pos[0]:first_index_pos[
                                            0] + max_positive_bias_index] / detector_coefficient - normalize_iso

        iso_descent = v_logamp[first_index_pos[0] + max_positive_bias_index:first_index_pos[0] + len(

            positive_bias)] / detector_coefficient - normalize_iso

        # =========================================================================

        # Positive Bias: Calculate pull-in and pull-out voltages using second derivative method

        # =========================================================================

        # Find the maximum and minimum of the second derivative in the positive bias cycle
 
        pos_region_ascent = slice(first_index_pos[0], first_index_pos[0] + max_positive_bias_index)
        pos_region_descent = slice(first_index_pos[0] + max_positive_bias_index, first_index_pos[0] + len(positive_bias))
 
        diff2_ascent = smoothed_diff_logamp_2[pos_region_ascent]
        diff2_descent = smoothed_diff_logamp_2[pos_region_descent]
 
        max_diff2_ascent = np.max(diff2_ascent)
        min_diff2_descent = np.min(diff2_descent)
 
        # Pull-in voltage: Find peaks in second derivative with a prominence threshold
        try:
            # Increased prominence to 0.5 * max to be less sensitive to small glitches
            peaks, _ = find_peaks(diff2_ascent, prominence=max_diff2_ascent * 0.5)
            
            if peaks.size > 0:
                # Of the peaks found, pick the one with the highest derivative value 
                # OR the one that corresponds to the most significant drop in isolation
                pullin_index_pos = peaks[np.argmax(diff2_ascent[peaks])]
            else:
                pullin_index_pos = int(np.where(diff2_ascent >= max_diff2_ascent)[0][0])
            
            vpullin = positive_bias[pullin_index_pos]
            ninetypercent_iso_ascent = round(0.9 * np.min(iso_ascent), 2)
        except (IndexError, ValueError):
            print('Did not find an index for pull-in voltage (positive bias)')
            vpullin = np.nan
 
        # Pull-out voltage: Find significant valleys in second derivative
        try:
            # Use a more aggressive prominence for pull-out as well
            valleys, _ = find_peaks(-diff2_descent, prominence=abs(min_diff2_descent) * 0.5)
            
            if valleys.size > 0:
                # Pick the most significant valley
                idx_in_valleys = valleys[np.argmax(-diff2_descent[valleys])]
                pullout_index_pos = idx_in_valleys
            else:
                pullout_index_pos = int(np.where(diff2_descent <= min_diff2_descent)[0][0])
            
            # Additional check: pull-out should happen when isolation has recovered significantly
            # Use 50% recovery threshold to avoid early small glitches
            max_iso_pos = np.min(iso_descent)
            if iso_descent[pullout_index_pos] < 0.5 * max_iso_pos:
                 # Fallback to thresholding (10%)
                 threshold_iso = 0.1 * max_iso_pos
                 fb_indices = np.where(iso_descent >= threshold_iso)[0]
                 if fb_indices.size > 0:
                     pullout_index_pos = fb_indices[0]
            
            vpullout = positive_bias[max_positive_bias_index + pullout_index_pos]
 
        except (IndexError, ValueError):
            print('Did not find an index for pull-out voltage (positive bias)')
            vpullout = np.nan

    if negative_bias.size > 0:

        # Finding the first and last indexes of negative bias in v_bias array

        first_index_neg = np.where(v_bias == negative_bias[0])[0]

        last_index_neg = np.where(v_bias == negative_bias[-1])[0]

        # Finding the index of the minimum negative bias (bottom of the negative triangle waveform)

        min_negative_bias_index = np.argmin(negative_bias)

        # Normalizing the log amplifier voltage over the ascent (positive bias portion)

        normalized_iso_minus = np.max(v_logamp[first_index_neg[0]:first_index_neg[

                                                                      0] + min_negative_bias_index] / detector_coefficient)

        iso_descent_minus = v_logamp[first_index_neg[0]:first_index_neg[0] + min_negative_bias_index] / (

                detector_coefficient - normalized_iso_minus)

        iso_ascent_minus = v_logamp[first_index_neg[0] + min_negative_bias_index:last_index_neg[

            0]] / detector_coefficient - normalized_iso_minus

        # Find the maximum and minimum of the second derivative in the negative bias cycle
 
        neg_region_ascent = slice(first_index_neg[0] + min_negative_bias_index, last_index_neg[0])
        neg_region_descent = slice(first_index_neg[0], first_index_neg[0] + min_negative_bias_index)
 
        diff2_ascent_neg = smoothed_diff_logamp_2[neg_region_ascent]
        diff2_descent_neg = smoothed_diff_logamp_2[neg_region_descent]
 
        max_diff2_descent_neg = np.max(diff2_descent_neg)
        min_diff2_ascent_neg = np.min(diff2_ascent_neg)
 
        # Negative Pull-in (occurs during descent to negative values)
        try:
            # Increased prominence to 0.5 * max
            peaks, _ = find_peaks(diff2_descent_neg, prominence=max_diff2_descent_neg * 0.5)
            
            if peaks.size > 0:
                # Pick the most significant peak to avoid small pre-pull-in glitches
                pullin_index_neg = peaks[np.argmax(diff2_descent_neg[peaks])]
            else:
                pullin_index_neg = int(np.where(diff2_descent_neg >= max_diff2_descent_neg)[0][0])
            
            vpullin_neg = negative_bias[pullin_index_neg]
            ninetypercent_iso_descent = round(0.9 * np.min(iso_descent_minus), 2)
        except (IndexError, ValueError):
            print('Did not find an index for pull-in voltage (negative bias)')
            vpullin_neg = np.nan
 
        # Negative Pull-out (occurs during ascent from negative values)
        try:
            # Increased prominence to 0.5 * abs(min)
            valleys, _ = find_peaks(-diff2_ascent_neg, prominence=abs(min_diff2_ascent_neg) * 0.5)
            
            if valleys.size > 0:
                # Pick the most significant valley
                idx_in_valleys = valleys[np.argmax(-diff2_ascent_neg[valleys])]
                pullout_index_neg = idx_in_valleys
            else:
                pullout_index_neg = int(np.where(diff2_ascent_neg <= min_diff2_ascent_neg)[0][0])
            
            # Check for isolation recovery (pull-out should happen when isolation is rising)
            # Use 50% recovery threshold to avoid early small glitches
            max_iso_neg = np.min(iso_ascent_minus)
            if iso_ascent_minus[pullout_index_neg] < 0.5 * max_iso_neg:
                # Fallback to thresholding (10%)
                threshold_iso_neg = 0.1 * max_iso_neg
                fb_indices_neg = np.where(iso_ascent_minus >= threshold_iso_neg)[0]
                if fb_indices_neg.size > 0:
                    pullout_index_neg = fb_indices_neg[0]
            
            vpullout_neg = negative_bias[min_negative_bias_index + pullout_index_neg]
 
        except (IndexError, ValueError):
            print('Did not find an index for pull-out voltage (negative bias)')
            vpullout_neg = np.nan

    # =========================================================================

    # Store the results in a dictionary for both positive and negative bias cycles

    # =========================================================================

    calculations = {

        'vpullin_plus': round(vpullin, 2) if not np.isnan(vpullin) else vpullin,  # Pull-in voltage (positive)

        'vpullout_plus': round(vpullout, 2) if not np.isnan(vpullout) else vpullout,  # Pull-out voltage (positive)

        'vpullin_minus': round(vpullin_neg, 2) if not np.isnan(vpullin_neg) else vpullin_neg,
        # Pull-in voltage (negative)

        'vpullout_minus': round(vpullout_neg, 2) if not np.isnan(vpullout_neg) else vpullout_neg,
        # Pull-out voltage (negative)

        'ninetypercent_iso_ascent': ninetypercent_iso_ascent,

        'ninetypercent_iso_descent': ninetypercent_iso_descent,

        'status': 'success',

        'd2_signal': smoothed_diff_logamp_2,

        'indices': {
            'pi_plus': pullin_index_pos + first_index_pos[0],
            'po_plus': pullout_index_pos + max_positive_bias_index + first_index_pos[0] if not np.isnan(vpullout) else None,
            'pi_minus': pullin_index_neg + first_index_neg[0] if negative_bias.size > 0 and not np.isnan(vpullin_neg) else None,
            'po_minus': pullout_index_neg + min_negative_bias_index + first_index_neg[0] if negative_bias.size > 0 and not np.isnan(vpullout_neg) else None
        }

    }

    return calculations

def extract_pull_down_voltage_and_iso(file, directory, detector_coefficient=1, step=20):
    """
    Extracts the pull-down voltage and second derivative of the log amplifier signal from a CSV file.

    This function reads a CSV file containing bias voltage, log amplifier voltage, and time data,
    smooths the log amplifier signal and its second derivative using the Savitzky-Golay filter,
    and returns the processed data.

    :param file: str
        The name of the CSV file containing the data.

    :param directory: str
        The directory where the data file is located.

    :param detector_coefficient: float, optional (default is 1)
        A coefficient that could be used for detector calibration or scaling (not used in current version).

    :param step: int, optional (default is 20)
        The step size used for finite difference calculations to approximate the first and second derivatives
        of the log amplifier voltage.

    :return: tuple
        A tuple containing the following elements:
        - v_bias (np.ndarray): The truncated bias voltage array after finite difference.
        - smoothed_v_logamp (np.ndarray): The smoothed log amplifier voltage array.
        - smoothed_diff_logamp_2 (np.ndarray): The smoothed second derivative of the log amplifier voltage.
        - time_step (float): The time step between consecutive measurements.
        - time (np.ndarray): The truncated time array corresponding to the truncated v_bias.
    """

    # Change the working directory to the specified directory
    os.chdir(path=directory)

    # Open the file and load the data into a NumPy array
    # Data is assumed to be in CSV format, with the first row containing headers, and columns:
    #   1st column: Bias voltage
    #   2nd column: Logarithmic amplifier voltage
    #   3rd column: Time data
    with open(file, newline='') as f:
        data = np.loadtxt(fname=file, delimiter=',', unpack=True, skiprows=1)

        # Set the parameters for the Savitzky-Golay filter
        window_length = 15  # Length of the filter window (must be odd)
        polyorder = 4  # Order of the polynomial to fit within each window

        # Extract columns from the data
        v_bias = data[:, 0].copy()  # Bias voltage (first column)
        v_logamp = data[:, 1].copy()  # Logarithmic amplifier voltage (second column)
        time = data[:, 2].copy()  # Time data (third column)

        # Compute the time step between consecutive measurements
        time_step = time[1] - time[0]

        # Compute the first finite difference over the step size
        # This approximates the first derivative of log amp voltage spaced `step` points apart
        diff_logamp = (v_logamp[step:] - v_logamp[:-step])

        # Compute the second finite difference, which approximates the second derivative
        diff_logamp_2 = (diff_logamp[step:] - diff_logamp[:-step])

        # Smooth the original log amplifier voltage data using the Savitzky-Golay filter
        smoothed_v_logamp_pre = savgol_filter(v_logamp, window_length, polyorder)
        min_smoothed_v_logamp = np.max(smoothed_v_logamp_pre)
        smoothed_v_logamp = smoothed_v_logamp_pre - min_smoothed_v_logamp
        # Smooth the second derivative (diff_logamp_2) using the same Savitzky-Golay filter
        smoothed_diff_logamp_2 = savgol_filter(diff_logamp_2, window_length, polyorder)

        # Print out the time step difference multiplied by the step size (for reference)
        print(f"difference timestep {time_step * step}")

    # Return the truncated bias voltage, smoothed log amp voltage, smoothed second derivative,
    # the time step between measurements, and the truncated time array.
    return v_bias[:-step * 2], smoothed_v_logamp[:-step * 2], smoothed_diff_logamp_2, time_step, time[:-step * 2]

def extract_data_v2(rf_detector_channel, v_bias_channel, ramp_start=0.20559, ramp_stop=0.206,
                    ramp_start_minus=0.20632, ramp_stop_minus=0.20679, delay=0.2, conversion_coeff=1):
    """
    Returns the MEMS Characteristics including Positive & Negative Pull-in voltages,
    Positive & Negative Pull-out voltages, Switching time, isolation and insertion loss variation during
    cycling sequence.
    :param rf_detector_channel: Detector channel array
    :param v_bias_channel: Bias channel array
    :param ramp_start: Starting time of the positive ramp (0.20383)
    :param ramp_stop: End time of the positive ramp (0.20437)
    :param ramp_start_minus: Starting time of the negative ramp (0.2046)
    :param ramp_stop_minus: End time of the negative ramp (0.20519)
    :param delay: Input delay of the oscilloscope to position at the end of the cycling waveform
    :param conversion_coeff: Conversion coefficient from power to voltage of the detector
    :return: DataFrame containing all the MEMS characteristics
    """
    # Initialize variables with zero values
    vpullin_plus, vpullin_minus, vpullout_plus, vpullout_minus = 0, 0, 0, 0
    iso_ascent_value, iso_descent_minus_value = 0, 0
    switching_time, relative_amplitude, release_time = 0, 0, 0

    try:
        # Ensure the input arrays are numpy arrays
        rf_detector_channel = np.array(rf_detector_channel)
        v_bias_channel = np.array(v_bias_channel)

        # Extracting values using oscilloscope commands
        delay = float(osc.query('HORizontal:MAIn:DELay:TIMe?'))
        switching_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
        release_time = float(osc.query('MEASUrement:MEAS2:VALue?'))
        amplitude_t0 = float(osc.query('MEASUrement:MEAS4:VALue?'))
        a1, b1 = get_powermeter_channels()
        # relative_amplitude = amplitude_t0 - float(osc.query('MEASUrement:MEAS4:VALue?'))
        relative_amplitude = b1 - a1

        # Insert the get curve data with ramp position to calculate pull_in, pull_out and insertion loss + isolation
        t = rf_detector_channel[:, 1] + delay
        rf_detector_curve = rf_detector_channel[:, 0]
        v_bias_curve = v_bias_channel[:, 0]

        trigger_offset = int(t.size / (float(osc.query('HORIZONTAL:POSITION?'))))

        # Define a ramp voltage curve to calculate pull in and pull out curve.
        if t.size == 0:
            raise ValueError("Time array 't' is empty.")

        t0_ramp_indices = np.where(t > ramp_start)[0]
        if t0_ramp_indices.size == 0:
            raise ValueError("No elements found in 't' greater than ramp_start.")
        else:
            t0_ramp = t0_ramp_indices[0]

        t0_plus_rampwidth_indices = np.where(t < ramp_stop)[0]
        if t0_plus_rampwidth_indices.size == 0:
            raise ValueError("No elements found in 't' less than ramp_stop.")
        else:
            t0_plus_rampwidth = t0_plus_rampwidth_indices[-1]

        # Define a ramp voltage curve to calculate pull in and pull out curve of negative ramp.
        t0_ramp_minus_indices = np.where(t > ramp_start_minus)[0]
        if t0_ramp_minus_indices.size == 0:
            raise ValueError("No elements found in 't' greater than ramp_start_minus.")
        else:
            t0_ramp_minus = t0_ramp_minus_indices[0]

        t0_plus_rampwidth_minus_indices = np.where(t < ramp_stop_minus)[0]
        if t0_plus_rampwidth_minus_indices.size == 0:
            raise ValueError("No elements found in 't' less than ramp_stop_minus.")
        else:
            t0_plus_rampwidth_minus = t0_plus_rampwidth_minus_indices[-1]

        # Calculate the index corresponding to the Max voltage of our ramp
        max_positive_bias_index = np.argmax(v_bias_curve)
        min_negative_bias_index = np.argmin(v_bias_curve)

        # Extract the ramp voltage curve ascent and descent
        ramp_voltage_ascent = v_bias_curve[t0_ramp:max_positive_bias_index]
        ramp_voltage_descent = v_bias_curve[max_positive_bias_index:t0_plus_rampwidth]
        ramp_voltage_descent_minus = v_bias_curve[t0_ramp_minus:min_negative_bias_index]
        ramp_voltage_ascent_minus = v_bias_curve[min_negative_bias_index:t0_plus_rampwidth_minus]

        # Calculate the normalization value for the isolation
        normalized_isolation_plus = np.max(3 * rf_detector_curve[t0_ramp:t0_plus_rampwidth] / conversion_coeff)
        normalized_isolation_minus = np.max(
            3 * rf_detector_curve[t0_ramp_minus:t0_plus_rampwidth_minus] / conversion_coeff)

        # Calculate iso_ascent and iso_descent
        iso_ascent = 3 * rf_detector_curve[
                         t0_ramp:max_positive_bias_index] / conversion_coeff - normalized_isolation_plus
        iso_descent = 3 * rf_detector_curve[
                          max_positive_bias_index:t0_plus_rampwidth] / conversion_coeff - normalized_isolation_plus
        iso_descent_minus = 3 * rf_detector_curve[
                                t0_ramp_minus:min_negative_bias_index] / conversion_coeff - normalized_isolation_minus
        iso_ascent_minus = 3 * rf_detector_curve[
                               min_negative_bias_index:t0_plus_rampwidth_minus] / conversion_coeff - normalized_isolation_minus

        # Calculation Vpull in and Vpull out
        pullin_index_pos = np.where(iso_ascent <= 0.9 * np.min(iso_ascent))[0]
        if pullin_index_pos.size == 0:
            raise ValueError("No elements found in iso_ascent satisfying the condition.")
        vpullin_plus = round(ramp_voltage_ascent[pullin_index_pos[0]], 2)

        pullin_index_neg = np.where(iso_descent_minus <= 0.9 * np.min(iso_descent_minus))[0]
        if pullin_index_neg.size == 0:
            raise ValueError("No elements found in iso_descent_minus satisfying the condition.")
        vpullin_minus = round(ramp_voltage_descent_minus[pullin_index_neg[0]], 2)

        pullout_index_pos = np.where(iso_descent >= 0.1 * np.min(iso_descent))[0]
        if pullout_index_pos.size == 0:
            raise ValueError("No elements found in iso_descent satisfying the condition.")
        vpullout_plus = round(ramp_voltage_descent[pullout_index_pos[0]], 2)

        pullout_index_neg = np.where(iso_ascent_minus >= 0.1 * np.min(iso_ascent_minus))[0]
        if pullout_index_neg.size == 0:
            raise ValueError("No elements found in iso_ascent_minus satisfying the condition.")
        vpullout_minus = round(ramp_voltage_ascent_minus[pullout_index_neg[0]], 2)

        iso_ascent_value = 0.9 * np.min(iso_ascent)
        iso_descent_minus_value = 0.9 * np.min(iso_descent_minus)

    except Exception as e:
        print(f"An error occurred: {e}")

    # Creating the dictionary for DataFrame
    data = {
        'vpullin_plus': [vpullin_plus], 'vpullin_minus': [vpullin_minus], 'vpullout_plus': [vpullout_plus],
        'vpullout_minus': [vpullout_minus], 'iso_ascent': [iso_ascent_value],
        'iso_descent_minus': [iso_descent_minus_value], 'switching_time': [switching_time],
        'amplitude_variation': [relative_amplitude], 'release_time': [release_time]
    }

    # Creating the DataFrame
    mems_characteristics = pd.DataFrame(data)

    return mems_characteristics

def extract_data_v3(rf_detector_channel, v_bias_channel, ramp_start=0.2039, ramp_stop=0.205,
                    ramp_start_minus=0.2059,
                    ramp_stop_minus=0.207, delay=0.2):
    """
        Returns the MEMS Characteristics including Positive & Negative Pull-in voltages,
        Positive & Negative Pull-out voltages, Switching time, isolation and insertion loss variation during
        cycling sequence.
        :param rf_detector_channel: Detector channel array
        :param v_bias_channel: Bias channel array
        :param ramp_start: Starting time of the positive ramp (0.20383)
        :param ramp_stop: End time of the positive ramp (0.20437)
        :param ramp_start_minus: Starting time of the negative ramp (0.2046)
        :param ramp_stop_minus: End time of the negative ramp (0.20519)
        :param delay: Input delay of the oscilloscope to position at the end of the cycling waveform
        :return: DataFrame containing all the MEMS characteristics
        """
    # Ensure the input arrays are numpy arrays
    rf_detector_channel = np.array(rf_detector_channel)
    v_bias_channel = np.array(v_bias_channel)

    # Extracting values using oscilloscope commands
    delay = float(osc.query('HORizontal:MAIn:DELay:TIMe?'))
    t_on_time = float(osc.query('MEASUrement:MEAS1:VALue?'))
    t_off_time = float(osc.query('MEASUrement:MEAS2:VALue?'))
    amplitude_t0 = float(osc.query('MEASUrement:MEAS4:VALue?'))
    a1, b1, b2 = get_powermeter_channels()

    relative_amplitude = b2 - a1
    isolation = b1 - a1
    sample_rate = osc.query("HORIZONTAL:MODE:SAMPLERATE?")
    duration = osc.query("HORizontal:ACQDURATION?")

    # Insert the get curve data with ramp position to calculate pull_in, pull_out and insertion loss + isolation
    t = rf_detector_channel[:, 1] + delay
    rf_detector_curve = rf_detector_channel[:, 0]
    v_bias_curve = v_bias_channel[:, 0]

    trigger_offset = int(t.size / (float(osc.query('HORIZONTAL:POSITION?'))))

    # Define a ramp voltage curve to calculate pull in and pull out curve.
    if t.size == 0:
        raise ValueError("Time array 't' is empty.")

    t0_ramp_indices = np.where(t > ramp_start)[0]
    if t0_ramp_indices.size == 0:
        raise ValueError("No elements found in 't' greater than ramp_start.")
    else:
        t0_ramp = t0_ramp_indices[0]

    t0_plus_rampwidth_indices = np.where(t < ramp_stop)[0]
    if t0_plus_rampwidth_indices.size == 0:
        raise ValueError("No elements found in 't' less than ramp_stop.")
    else:
        t0_plus_rampwidth = t0_plus_rampwidth_indices[-1]

    # Define a ramp voltage curve to calculate pull in and pull out curve of negative ramp.
    t0_ramp_minus_indices = np.where(t > ramp_start_minus)[0]
    if t0_ramp_minus_indices.size == 0:
        raise ValueError("No elements found in 't' greater than ramp_start_minus.")
    else:
        t0_ramp_minus = t0_ramp_minus_indices[0]

    t0_plus_rampwidth_minus_indices = np.where(t < ramp_stop_minus)[0]
    if t0_plus_rampwidth_minus_indices.size == 0:
        raise ValueError("No elements found in 't' less than ramp_stop_minus.")
    else:
        t0_plus_rampwidth_minus = t0_plus_rampwidth_minus_indices[-1]

    # Calculate the index corresponding to the Max voltage of our ramp
    max_positive_bias_index = np.argmax(v_bias_curve)
    min_negative_bias_index = np.argmin(v_bias_curve)

    step = 10
    # Set the parameters for the Savitzky-Golay filter
    window_length = 9  # Length of the filter window (must be odd)
    polyorder = 4  # Order of the polynomial to fit within each window
    detector_coefficient = 1

    # Compute the first finite difference over the step size
    # This approximates the first derivative of log amp voltage spaced `step` points apart
    v_logamp_t = rf_detector_curve[:-step * 2]
    v_bias_t = v_bias_curve[:-step * 2]
    diff_logamp = (v_logamp_t[step:] - v_logamp_t[:-step])

    # Compute the second finite difference, which approximates the second derivative
    diff_logamp_2 = (diff_logamp[step:] - diff_logamp[:-step])

    # Smooth the original log amplifier voltage data using the Savitzky-Golay filter
    smoothed_v_logamp_pre = savgol_filter(v_logamp_t, window_length, polyorder)
    min_smoothed_v_logamp = np.max(smoothed_v_logamp_pre)
    smoothed_v_logamp = smoothed_v_logamp_pre - min_smoothed_v_logamp

    # Smooth the second derivative (diff_logamp_2) using the same Savitzky-Golay filter
    smoothed_diff_logamp_2 = savgol_filter(diff_logamp_2, window_length, polyorder)

    positive_bias = v_bias_t[t0_ramp + trigger_offset: t0_plus_rampwidth + trigger_offset]
    negative_bias = v_bias_t[t0_ramp_minus + trigger_offset: t0_plus_rampwidth_minus + trigger_offset]

    # Finding the first index of positive bias in v_bias array
    first_index_pos = t0_ramp  # ========> Defined by the cursor on the oscilloscope
    # print(f'first_index_pos = {first_index_pos}')

    # Finding the last index of positive bias in v_bias array
    last_index_pos = t0_plus_rampwidth  # ========> Defined by the cursor on the oscilloscope
    # print(f'last_index_pos = {last_index_pos}')

    # Finding the first index of negative bias in v_bias array
    first_index_neg = t0_ramp_minus  # ========> Defined by the cursor on the oscilloscope
    # print(f'first_index_neg = {first_index_neg}')

    # Finding the last index of negative bias in v_bias array
    last_index_neg = t0_plus_rampwidth_minus  # ========> Defined by the cursor on the oscilloscope
    # print(f'last_index_neg = {last_index_neg}')

    # Finding the index of the maximum positive bias (top of the triangle waveform)
    max_positive_bias_index = np.argmax(v_bias_t[t0_ramp + trigger_offset: t0_plus_rampwidth + trigger_offset])
    # print(f'max_positive_bias_index = {max_positive_bias_index} \n')

    # Finding the index of the minimum negative bias (bottom of the negative triangle waveform)
    min_negative_bias_index = np.argmin(
        v_bias_t[t0_ramp_minus + trigger_offset: t0_plus_rampwidth_minus + trigger_offset])

    # =========================================================================
    # Positive Bias: Calculate pull-in and pull-out voltages using second derivative method
    # =========================================================================

    # Find the maximum and minimum of the second derivative in the positive bias cycle
    # Using the maximum index -> Input this index to the v bias array to determine pull-in voltage
    try:
        max_smoothed_diff_logamp_2 = int(np.argmax(smoothed_diff_logamp_2[
                                                   first_index_pos:last_index_pos]))
        # print(f'max_smoothed_diff_logamp_2 = {max_smoothed_diff_logamp_2} \n')
        # print("Max was found in positive ramp")

        pullin_index_pos = int(np.argmax(smoothed_diff_logamp_2[
                                         first_index_pos + trigger_offset:first_index_pos + max_positive_bias_index + trigger_offset]))
        vpullin = v_bias_t[first_index_pos + trigger_offset + pullin_index_pos]
    except:
        print("Max was not found")
        print('Did not find an index for pull-in voltage using differentiation method')
        vpullin = 0

    # Using the minimum index -> Input this index to the v bias array to determine pull-out voltage
    try:
        min_smoothed_diff_logamp_2 = int(np.argmin(smoothed_diff_logamp_2[
                                                   first_index_pos + trigger_offset + max_positive_bias_index:last_index_pos + trigger_offset]))
        # print(f'min_smoothed_diff_logamp_2 = {min_smoothed_diff_logamp_2} \n')
        # print('Min was found in negative ramp')
        pullout_index_pos = int(np.argmin(smoothed_diff_logamp_2[
                                          first_index_pos + max_positive_bias_index + trigger_offset:last_index_pos + trigger_offset]))
        vpullout = v_bias_t[first_index_pos + max_positive_bias_index + trigger_offset + pullout_index_pos]
        # print(f'vpullout = {vpullout}')
    except:
        print('Did not find an index for pull-out voltage using differentiation method')
        print('Min was not found in negative ramp')
        vpullout = 0  # Fallback value

    # =========================================================================
    # Negative Bias: Calculate pull-in and pull-out voltages using second derivative method
    # =========================================================================

    # Find the maximum and minimum of the second derivative in the negative bias cycle
    # Using the maximum index -> Input this index to the v bias array to determine pull-in voltage
    try:
        max_smoothed_diff_logamp_2_neg = np.argmax(
            smoothed_diff_logamp_2[
            first_index_neg + trigger_offset:first_index_neg + min_negative_bias_index + trigger_offset])
        # print(f'max_smoothed_diff_logamp_2_neg = {max_smoothed_diff_logamp_2_neg} \n')
        # print("Max was found in negative ramp")

        pullin_index_neg = int(
            np.argmin(smoothed_diff_logamp_2[
                      first_index_neg + trigger_offset:first_index_neg + min_negative_bias_index + trigger_offset]))
        vpullin_neg = v_bias_t[first_index_neg + trigger_offset + pullin_index_neg]

        # print(f'vpullin_neg = {vpullin_neg}')
        min_smoothed_diff_logamp_2 = int(np.argmin(smoothed_diff_logamp_2[
                                                   first_index_neg:last_index_neg]))

    except:
        print("Max was not found")
        print('Did not find an index for negative pull-in(-) voltage using differentiation method')
        vpullin_neg = 0  # Fallback value

    # Pull-out voltage (negative bias): Find the index where the second derivative reaches its minimum
    # Using the maximum index -> Input this index to the v bias array to determine pull-in voltage

    try:
        min_smoothed_diff_logamp_2_neg = np.argmin(smoothed_diff_logamp_2[
                                                   first_index_neg + trigger_offset + min_negative_bias_index:last_index_neg + trigger_offset])
        # print(f'min_smoothed_diff_logamp_2_neg = {min_smoothed_diff_logamp_2_neg} \n')
        # print("Min was found in negative ramp")

        pullout_index_neg = int(np.argmin(smoothed_diff_logamp_2[
                                          first_index_neg + trigger_offset + min_negative_bias_index:last_index_neg + trigger_offset]))
        vpullout_neg = v_bias_t[first_index_neg + min_negative_bias_index + trigger_offset + pullout_index_neg]
        # print(f'vpullout_neg = {vpullout_neg}')

    except:
        print("Min was not found")
        print('Did not find an index for negative pull-out(-) voltage using differentiation method')
        vpullout_neg = 0  # Fallback value

    # Creating the dictionary for DataFrame
    data = {
        'vpullin_plus': [vpullin], 'vpullin_minus': [vpullin_neg], 'vpullout_plus': [vpullout],
        'vpullout_minus': [vpullout_neg], 't_on_time': [t_on_time],
        'insertion_loss': [relative_amplitude], 't_off_time': [t_off_time], 'isolation': [isolation]
    }
    # Creating the DataFrame
    mems_characteristics = pd.DataFrame(data)

    return mems_characteristics

def apply_threshold_filter(fft_result, magnitudes, threshold_percent):
    """
    Apply threshold-based noise filtering.

    Parameters:
    fft_result: numpy array
        Complex FFT result
    magnitudes: numpy array
        FFT magnitudes
    threshold_percent: float
        Percentage of maximum magnitude to use as threshold (0-100)

    Returns:
    numpy array: Filtered FFT result
    """
    threshold = np.max(magnitudes) * (threshold_percent / 100)
    filtered_fft = fft_result.copy()
    filtered_fft[magnitudes < threshold] = 0
    return filtered_fft

def plot_signal_fft(data, filter_type='none', threshold_percent=5, sg_window=51, sg_order=3, window_type='rectangular'):
    """
    Plot the original signal and its FFT with optional noise filtering, log y-scale, and windowing.

    Parameters:
    data: numpy array of shape (N, 2)
        data[:,0] contains voltage values in volts
        data[:,1] contains time values in seconds
    filter_type: str
        'none': No filtering
        'threshold': Simple threshold-based noise filtering
        'savgol': Savitzky-Golay filtering
        'both': Apply both filters
    threshold_percent: float
        Percentage of maximum magnitude to use as threshold (0-100)
    sg_window: int
        Window length for Savitzky-Golay filter (must be odd)
    sg_order: int
        Polynomial order for Savitzky-Golay filter
    window_type: str
        'rectangular', 'hamming', 'hann', 'blackman'
    """
    # Extract voltage and time data
    voltage = data[:, 0]
    time = data[:, 1]

    # Apply window function
    window = get_window(window_type, len(voltage))
    voltage_windowed = voltage * window

    # Apply Savitzky-Golay filter to time domain if requested
    if filter_type in ['savgol', 'both']:
        voltage_filtered = savgol_filter(voltage_windowed, sg_window, sg_order)
    else:
        voltage_filtered = voltage_windowed

    # Calculate sampling parameters
    sampling_period = time[1] - time[0]
    sampling_frequency = 1.0 / sampling_period
    n_samples = len(voltage)

    # Compute FFT
    fft_result = np.fft.fft(voltage_filtered)
    fft_freq = np.fft.fftfreq(n_samples, sampling_period)

    # Calculate magnitude spectrum
    magnitude = 2.0 * np.abs(fft_result) / n_samples

    # Apply threshold filter if requested
    if filter_type in ['threshold', 'both']:
        fft_result_filtered = apply_threshold_filter(fft_result, magnitude, threshold_percent)
        magnitude_filtered = 2.0 * np.abs(fft_result_filtered) / n_samples
    else:
        magnitude_filtered = magnitude

    # Create subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

    # Plot original signal
    ax1.plot(time * 1000, voltage, 'b-', label='Original Signal')
    ax1.plot(time * 1000, voltage_windowed, 'g-', label='Windowed Signal')
    if filter_type in ['savgol', 'both']:
        ax1.plot(time * 1000, voltage_filtered, 'r-', label='Filtered Signal')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('Time Domain Signal')
    ax1.grid(True)
    ax1.legend()

    # Plot full FFT magnitude spectrum
    positive_freq_mask = fft_freq >= 0
    ax2.semilogy(fft_freq[positive_freq_mask], magnitude[positive_freq_mask], 'b-', label='Original FFT')
    ax2.set_xscale('log')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude (log scale)')
    ax2.set_title('Full Frequency Spectrum')
    ax2.grid(True)
    ax2.legend()

    # Plot filtered FFT magnitude spectrum
    if filter_type in ['threshold', 'both']:
        ax3.semilogy(fft_freq[positive_freq_mask], magnitude_filtered[positive_freq_mask], 'r-',
                     label=f'Filtered FFT (threshold: {threshold_percent}%)')
    else:
        ax3.semilogy(fft_freq[positive_freq_mask], magnitude_filtered[positive_freq_mask], 'r-',
                     label='Filtered FFT')
    ax3.set_xscale('log')
    # ax3.set(xlim=[1e3, 1e6])
    ax3.set(ylim=[1e-7, 1e-2])
    ax3.set(xlim=[1e3, 200000])
    ax3.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.0e}'))

    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Magnitude (log scale)')
    ax3.set_title('Filtered Frequency Spectrum')
    ax3.grid(True)
    ax3.legend()

    # Make layout tight and display plot
    plt.tight_layout()
    plt.show()

    return fft_freq[positive_freq_mask], magnitude_filtered[positive_freq_mask]

def plot_signal_fft_noise_removal(current_data, previous_data, filter_type='none', threshold_percent=5, sg_window=51,
                                  sg_order=3,
                                  window_type='rectangular'):
    """
    Plot the original signal and its FFT with optional noise filtering, log y-scale, windowing, and inter-acquisition convolution.

    Parameters:
    current_data: numpy array of shape (N, 2)
        current_data[:,0] contains voltage values in volts
        current_data[:,1] contains time values in seconds
    previous_data: numpy array of shape (N, 2)
        previous_data[:,0] contains previous voltage values in volts
        previous_data[:,1] contains previous time values in seconds
    filter_type: str
        'none': No filtering
        'threshold': Simple threshold-based noise filtering
        'savgol': Savitzky-Golay filtering
        'convolve': Inter-acquisition convolution-based filtering
        'both': Apply both threshold and convolution filters
    threshold_percent: float
        Percentage of maximum magnitude to use as threshold (0-100)
    sg_window: int
        Window length for Savitzky-Golay filter (must be odd)
    sg_order: int
        Polynomial order for Savitzky-Golay filter
    window_type: str
        'rectangular', 'hamming', 'hann', 'blackman'
    """
    # Extract voltage and time data
    current_voltage = current_data[:, 0]
    current_time = current_data[:, 1]
    previous_voltage = previous_data[:, 0]
    previous_time = previous_data[:, 1]

    # Apply window function
    current_window = get_window(window_type, len(current_voltage))
    current_voltage_windowed = current_voltage * current_window

    # Apply inter-acquisition convolution-based filtering if requested
    if filter_type in ['convolve', 'both']:
        current_voltage_filtered = convolve(current_voltage_windowed, previous_voltage, mode='same')
    elif filter_type in ['savgol']:
        current_voltage_filtered = savgol_filter(current_voltage_windowed, sg_window, sg_order)
    else:
        current_voltage_filtered = current_voltage_windowed

    # Calculate sampling parameters
    current_sampling_period = current_time[1] - current_time[0]
    current_sampling_frequency = 1.0 / current_sampling_period
    current_n_samples = len(current_voltage)

    # Compute FFT
    current_fft_result = np.fft.fft(current_voltage_filtered)
    current_fft_freq = np.fft.fftfreq(current_n_samples, current_sampling_period)

    # Calculate magnitude spectrum
    current_magnitude = 2.0 * np.abs(current_fft_result) / current_n_samples

    # Apply threshold filter if requested
    if filter_type in ['threshold', 'both']:
        current_fft_result_filtered = apply_threshold_filter(current_fft_result, current_magnitude, threshold_percent)
        current_magnitude_filtered = 2.0 * np.abs(current_fft_result_filtered) / current_n_samples
    else:
        current_magnitude_filtered = current_magnitude

    # Create subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

    # Plot original signal
    ax1.plot(current_time * 1000, current_voltage, 'b-', label='Original Signal')
    ax1.plot(current_time * 1000, current_voltage_windowed, 'g-', label='Windowed Signal')
    ax1.plot(current_time * 1000, current_voltage_filtered, 'r-', label='Filtered Signal')
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title('Time Domain Signal')
    ax1.grid(True)
    ax1.legend()

    # Plot full FFT magnitude spectrum
    positive_freq_mask = current_fft_freq >= 0
    ax2.semilogy(current_fft_freq[positive_freq_mask], current_magnitude[positive_freq_mask], 'b-',
                 label='Original FFT')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Magnitude (log scale)')
    ax2.set_title('Full Frequency Spectrum')
    ax2.set_xscale('log')
    ax2.set(xlim=[1e4, 1.5e5])
    ax2.set(ylim=[1e-4, 1e-2])
    # ax2.set(xlim=[1e3, 200000])

    ax2.grid(True)
    ax2.legend()

    # Plot filtered FFT magnitude spectrum
    if filter_type in ['threshold', 'both']:
        ax3.plot(current_fft_freq[positive_freq_mask], 10 * np.log10(current_magnitude_filtered[positive_freq_mask]),
                 'r-',
                 label=f'Filtered FFT (threshold: {threshold_percent}%)')
    else:
        ax3.plot(current_fft_freq[positive_freq_mask], 10 * np.log10(current_magnitude_filtered[positive_freq_mask]),
                 'r-',
                 label='Filtered FFT')
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Magnitude (log scale)')
    ax3.set_title('Filtered Frequency Spectrum')
    ax3.grid(True)
    # ax3.set_xscale('log')
    # ax3.set(xlim=[1e3, 1e6])
    # ax3.set(ylim=[2e-4, 1e-2])
    ax3.set(ylim=[-40, -25])
    ax3.set(xlim=[1e3, 150000])
    ax3.legend()

    # Make layout tight and display plot
    plt.tight_layout()
    plt.show()

    return current_fft_freq[positive_freq_mask], current_magnitude_filtered[positive_freq_mask]

def create_smooth_pull_in_voltage_waveform(voltages: list[int] | list[float], width_pulse: float) -> np.ndarray:
    """
    Generates a waveform with ascending and descending square pulses specified by voltage values,
    modified to include increased rise time and fall time to avoid overshoots and undershoots using a Gaussian filter.

    Args:
        voltages (list of int): List of voltage amplitudes for the pulses in ascending order.
        width_pulse (float): Duration of each pulse and the zero gap in the ascending phase in microseconds.

    Returns:
        np.ndarray: The generated waveform array with smooth and rounded transitions in pulse ascension and continuous descent.
    """
    sample_rate = 7272727  # Sample rate in Hz
    pulse_width = int(width_pulse * 1e-6 * sample_rate)

    # Define the Gaussian filter
    def gaussian_filter(length, std_dev):
        return np.exp(-np.power(np.arange(length) - length / 2, 2.) / (2 * np.power(std_dev, 2.)))

    # Length of the Gaussian filter
    filter_length = 50  # This length can be adjusted based on your specific needs
    std_dev = 5  # Standard deviation controls the width of the Gaussian curve

    # Generate the Gaussian window
    gaussian_window = gaussian_filter(filter_length, std_dev)
    gaussian_window /= np.sum(gaussian_window)  # Normalize the window to maintain pulse amplitude

    # Function to apply smoothing to a pulse
    def smooth_pulse(pulse):
        return np.convolve(pulse, gaussian_window, mode='same')

    # Create the ascending phase of the waveform
    ascending_wave = [smooth_pulse(create_pulse_ascent(voltage, pulse_width, True)) for voltage in sorted(voltages)]

    # Create the descending phase of the waveform without zero values between pulses
    descending_wave = [
        smooth_pulse(create_descending_waveform(sorted(voltages, reverse=True), pulse_width))]  # for voltage in
    # sorted(voltages, reverse=True)]

    # Concatenate the ascending and descending phases
    waveform = np.concatenate(ascending_wave + descending_wave)
    scaled_waveform_data = scale_waveform_to_dac(waveform)
    return scaled_waveform_data

def scale_waveform_to_dac(waveform, min_dac=0, max_dac=32767) -> np.ndarray:
    """Scale the waveform data to fit within the DAC range of the signal generator."""
    min_wave = np.min(waveform)
    max_wave = np.max(waveform)
    # Scale and offset the waveform to fit the DAC range
    scaled_waveform = (waveform - min_wave) / (max_wave - min_wave) * (max_dac - min_dac) + min_dac
    print(scaled_waveform, end='\n')
    return np.round(scaled_waveform).astype(int)

def calculate_actuation_and_release_voltages_v2(v_bias, v_logamp, detector_coefficient=1, step=20, prominence=0.1):
    """
    Calculates pull-in and pull-out voltages using a more robust method with scipy.signal.find_peaks.

    Parameters
    ----------
    v_bias : numpy.ndarray
        Numpy array of floats representing the bias voltage applied to the MEMS.
    v_logamp : numpy.ndarray
        Numpy array of floats representing the output of the logarithmic amplifier detector.
    detector_coefficient : float, optional (default=1)
        The coefficient that relates the detector's RF to voltage characteristic.
    step : int, optional (default is 20)
        The step size used for finite difference calculations.
    prominence : float, optional (default is 0.1)
        The prominence for peak detection in `find_peaks`.

    Returns
    -------
    calculations : dict
        A dictionary containing the calculated voltages and a status message.
    """
    # Input validation
    if not isinstance(v_bias, np.ndarray) or not isinstance(v_logamp,
                                                            np.ndarray) or v_bias.size == 0 or v_logamp.size == 0:
        return {'status': 'error', 'message': 'Input arrays are invalid.'}
    if v_bias.shape != v_logamp.shape:
        return {'status': 'error', 'message': 'Input arrays must have the same shape.'}

    # Savitzky-Golay filter parameters
    window_length = 15
    polyorder = 4

    # Ensure window_length is odd and less than the size of the data
    if len(v_logamp) < window_length:
        window_length = len(v_logamp)
        if window_length % 2 == 0:
            window_length -= 1

    if window_length <= polyorder:
        return {'status': 'error',
                'message': f'window_length ({window_length}) must be greater than polyorder ({polyorder}).'}

    # --- Second Derivative Calculation ---
    # First derivative (central difference)
    dv = np.gradient(v_logamp)
    # Second derivative
    d2v = np.gradient(dv)

    # Smoothing the second derivative
    if len(d2v) >= window_length:
        smoothed_d2v = savgol_filter(d2v, window_length, polyorder)
    else:
        smoothed_d2v = d2v  # Skip filtering if too small

    # --- Peak Detection using find_peaks ---
    vpullin_plus, vpullout_plus, vpullin_minus, vpullout_minus = np.nan, np.nan, np.nan, np.nan

    # Positive bias cycle
    pos_bias_indices = np.where(v_bias > 2)[0]
    if pos_bias_indices.size > 0:
        max_pos_bias_idx = pos_bias_indices[np.argmax(v_bias[pos_bias_indices])]

        # Pull-in (max of 2nd derivative during ramp-up)
        ramp_up_indices = pos_bias_indices[v_bias[pos_bias_indices] < v_bias[max_pos_bias_idx]]
        if ramp_up_indices.size > 0:
            peaks_in, _ = find_peaks(smoothed_d2v[ramp_up_indices], prominence=prominence)
            if peaks_in.size > 0:
                vpullin_plus = v_bias[ramp_up_indices[peaks_in[0]]]

        # Pull-out (min of 2nd derivative during ramp-down)
        ramp_down_indices = pos_bias_indices[v_bias[pos_bias_indices] > 0]  # all positive bias
        ramp_down_indices = ramp_down_indices[ramp_down_indices > max_pos_bias_idx]
        if ramp_down_indices.size > 0:
            peaks_out, _ = find_peaks(-smoothed_d2v[ramp_down_indices], prominence=prominence)
            if peaks_out.size > 0:
                vpullout_plus = v_bias[ramp_down_indices[peaks_out[0]]]

    # Negative bias cycle
    neg_bias_indices = np.where(v_bias < -2)[0]
    if neg_bias_indices.size > 0:
        min_neg_bias_idx = neg_bias_indices[np.argmin(v_bias[neg_bias_indices])]

        # Pull-in (max of 2nd derivative during ramp-down)
        ramp_down_indices_neg = neg_bias_indices[v_bias[neg_bias_indices] > v_bias[min_neg_bias_idx]]
        if ramp_down_indices_neg.size > 0:
            peaks_in_neg, _ = find_peaks(smoothed_d2v[ramp_down_indices_neg], prominence=prominence)
            if peaks_in_neg.size > 0:
                vpullin_minus = v_bias[ramp_down_indices_neg[peaks_in_neg[0]]]

        # Pull-out (min of 2nd derivative during ramp-up)
        ramp_up_indices_neg = neg_bias_indices[v_bias[neg_bias_indices] < 0]
        ramp_up_indices_neg = ramp_up_indices_neg[ramp_up_indices_neg > min_neg_bias_idx]
        if ramp_up_indices_neg.size > 0:
            peaks_out_neg, _ = find_peaks(-smoothed_d2v[ramp_up_indices_neg], prominence=prominence)
            if peaks_out_neg.size > 0:
                vpullout_minus = v_bias[ramp_up_indices_neg[peaks_out_neg[0]]]

    calculations = {
        'vpullin_plus': vpullin_plus,
        'vpullout_plus': vpullout_plus,
        'vpullin_minus': vpullin_minus,
        'vpullout_minus': vpullout_minus,
        'status': 'success'
    }

    return calculations

