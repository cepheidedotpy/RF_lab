import numpy as np
import scipy.signal as signal
import os

def highest_value_element_wise(array1, array2):
    """
    Returns a new array where each element is taken from array1 if the corresponding element in array2 is zero,
    otherwise from array2.

    Parameters:
    ----------
    array1 : numpy array
        The first input array.
    array2 : numpy array
        The second input array.

    Returns:
    -------
    numpy array
        A new array with elements from array1 where array2 is zero, otherwise from array2.
    """
    if len(array1) != len(array2):
        raise ValueError("Both arrays must have the same length")

    # Create an output array
    output_array = np.where(array2 == 0, array1, array2)
    return output_array

class stimulus_wf:  # Generates a waveform class with pulse width duty cycle and ramp function used for cycling
    def __init__(self, pulse_width: float = 100 / (10 ** 6), duty_cycle: float = 0.5, number_of_pulses: float = 5,
                 ramp_width=200 / (10 ** 6), amplitude_sq_a1: float = 1, amplitude_sq_a2: float = 1,
                 amplitude_ramp: float = 2.3,
                 length_top=20 / (10 ** 6),
                 sample_rate_red_factor: int = 100):
        # Maximum frequency of the signal generator
        max_frequency_signal_generator = 80 * 10 ** 7
        # 110% of the min periode to stay in the signal generator bandwidth
        self.min_sample_time = 1 / max_frequency_signal_generator * 1.1
        self.sample_rate = 1 / self.min_sample_time  # 7.2 GHz default
        self.sample_rate_red_factor = sample_rate_red_factor

        self.pulse_period = 200 / (10 ** (6))
        self.amplitude_sq_a1 = amplitude_sq_a1
        self.amplitude_sq_a2 = amplitude_sq_a2
        self.amplitude_ramp = amplitude_ramp
        self.ramp_pulse_ratio_a1 = self.amplitude_sq_a1 / self.amplitude_ramp
        self.ramp_pulse_ratio_a2 = self.amplitude_sq_a2 / self.amplitude_ramp

        # ==============================================================================
        self.pulse_width = pulse_width  # Pulse width parameter
        self.duty_cycle = duty_cycle  # Duty cycle parameter
        self.length_top = length_top  # Length at the top
        self.number_of_pulses = number_of_pulses  # Number of pulses
        # Calculate pulse period based on the final total ON time (pulse + length_top)
        self.total_on_time = self.pulse_width + self.length_top
        self.pulse_period = self.total_on_time / self.duty_cycle  # Pulse period
        
        # We need the individual square waves to have a duty cycle such that OnTime = pulse_width
        self.square_duty = self.pulse_width / self.pulse_period
        
        self.ramp_width = ramp_width  # ramp width parameter
        self.number_of_sample_in_periode = int(
            self.pulse_period / self.min_sample_time / self.sample_rate_red_factor)
        self.frequency = 1 / self.pulse_period
        self.t_pulse = np.arange(start=0, stop=self.pulse_period * self.number_of_pulses,
                                 step=self.min_sample_time * self.sample_rate_red_factor)

        wf = self.ramp_pulse_ratio_a1 * 32676 * \
             (signal.square(2 * np.pi * self.frequency *
                            self.t_pulse, duty=self.square_duty) + 1) / 2

        wf_2 = self.ramp_pulse_ratio_a2 * 32676 * \
               (signal.square(2 * np.pi * self.frequency *
                              (self.t_pulse - length_top), duty=self.square_duty) + 1) / 2
        wf_final = highest_value_element_wise(wf, wf_2)

        wf[0] = 0
        self.ramp_start_index = len(wf)
        self.wf = wf
        self.wf_2 = wf_2
        self.wf_final = wf_final
        # ==============================================================================
        # t_ramp_plus is the initial time at which the positive ramp starts
        self.t_ramp_plus = np.arange(start=self.t_pulse[-1], stop=self.t_pulse[-1] +
                                                                  self.ramp_width * 2,
                                     step=self.min_sample_time * self.sample_rate_red_factor)
        f = 1 / (2 * self.ramp_width)

        # sawtooth_plus is the positive sawtooth waveform that starts after the pulses
        self.sawtooth_plus = 32676 * \
                             (signal.sawtooth(2 * np.pi * f *
                                              (self.t_ramp_plus - self.t_ramp_plus[-1]), width=0.5) + 1) / 2

        self.wait_time = np.arange(start=self.t_ramp_plus[-1], stop=self.t_ramp_plus[-1] +
                                                                    self.ramp_width * 2,
                                   step=self.min_sample_time * self.sample_rate_red_factor)

        self.t_ramp_neg = np.arange(start=self.wait_time[-1], stop=self.wait_time[-1] +
                                                                   self.ramp_width * 2,
                                    step=self.min_sample_time * self.sample_rate_red_factor)

        self.wait_time_2 = np.arange(start=self.t_ramp_neg[-1], stop=self.t_ramp_neg[-1] +
                                                                     self.ramp_width * 2,
                                     step=self.min_sample_time * self.sample_rate_red_factor)
        self.sawtooth_neg = 32676 * \
                            - (signal.sawtooth(2 * np.pi * f *
                                               (self.t_ramp_neg - self.t_ramp_neg[-1]), width=0.5) + 1) / 2

        self.time = np.concatenate(
            (self.t_pulse, self.t_ramp_plus, self.wait_time, self.t_ramp_neg, self.wait_time_2), axis=None)

        self.waveform = np.concatenate(
            (self.wf_final, self.sawtooth_plus, self.wait_time, self.sawtooth_neg, self.wait_time_2), axis=None)

        self.data_points = len(self.waveform)
        self.wf_file_data = np.transpose(self.waveform)
        self.wf_duration = self.time[-1]
        self.expected_10power9_cycles = 10 * 10 ** 9 / \
                                        self.number_of_pulses * self.wf_duration / 3600 / 24

    def filter_file_data(self, window_pts=20):
        win = signal.windows.hann(window_pts)
        filtered = signal.convolve(
            self.wf_file_data, win, mode='full', method='direct') / sum(win)
        return filtered

    def get_mid_pulse_values(self):
        value_mid_pulse = self.waveform[int(self.number_of_sample_in_periode * self.duty_cycle / 2):int(
            self.number_of_sample_in_periode * self.number_of_pulses):int(self.number_of_sample_in_periode)]
        return value_mid_pulse

    def get_mid_pulse_indices(self):
        indices = np.arange(start=int(self.number_of_sample_in_periode * self.duty_cycle / 2),
                            stop=int(self.number_of_sample_in_periode * self.number_of_pulses),
                            step=int(self.number_of_sample_in_periode))
        return indices

    def create_file(self, directory: str, name=None):
        if name is None:
            name = '{:.0f}pulses_{:.0f}V_TOP_{:.0f}V_DC_{:.0f}percent_f{:.1f}kHz.arb'.format(
                self.number_of_pulses, self.amplitude_sq_a1 * 20, self.amplitude_sq_a2 * 20, self.duty_cycle * 100,
                                       self.frequency / 1000)
            name_filtered = '{:.0f}pulses_{:.0f}V_DC{:.0f}percent_f{:.1f}kHz_filtered.arb'.format(
                self.number_of_pulses, self.amplitude_sq_a1 * 20, self.duty_cycle * 100, self.frequency / 1000)
        else:
            name_filtered = f'{name}_filtered.arb'
            name = f'{name}.arb'

        a = np.around(self.wf_file_data, decimals=0)
        b = np.around(self.filter_file_data(), decimals=0)

        a.astype('int32')
        b.astype('int32')

        path_name = os.path.join(directory, name)
        path_filtered = os.path.join(directory, name_filtered)

        np.savetxt(path_name, a, fmt='%5.0f', delimiter='\t', newline='\n',
                   header="Copyright:Agilent Technologies, 2010\nFile Format:1.10"
                          "\nChannel Count:1\nSample Rate:{""}"
                          "\nHigh Level:{}\nLow Level:0\nData Type:\"short\"\nData Points:{}".format(
                       int(self.sample_rate / self.sample_rate_red_factor), self.amplitude_ramp,
                       self.data_points),
                   comments='')
        np.savetxt(path_filtered, b, fmt='%5.0f', delimiter='\t', newline='\n',
                   header="Copyright:Agilent Technologies, 2010\nFile Format:1.10"
                          "\nChannel Count:1\nSample Rate:{"
                          "}\nHigh Level:{}\nLow Level:0\nData Type:\"short\"\nData Points:{}".format(
                       int(self.sample_rate / self.sample_rate_red_factor), self.amplitude_ramp,
                       self.data_points),
                   comments='')
        return path_name, path_filtered
