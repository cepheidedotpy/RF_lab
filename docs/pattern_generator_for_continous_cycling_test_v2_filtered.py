# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 17:13:57 2023
@author: T0188303
"""

import csv
import numpy as np
import scipy
from scipy import signal
import os
from os import listdir
from os.path import isfile, join
from itertools import islice
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import style

path = r'C:\Users\T0188303\Desktop\Offline\PythonDIR\Cycling'

os.chdir(path)

"""Waveform class creation that generates a square wave and a sawtooth for pull-in voltage characterization 
"""


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
    # Ensure the arrays have the same length
    if len(array1) != len(array2):
        raise ValueError("Both arrays must have the same length")

    # Create an output array
    output_array = np.where(array2 == 0, array1, array2)

    return output_array


class Waveform_calc:

    def __new__(cls, time=np.zeros(10), function=np.zeros(10), function_name='No_name', wf_info=None):
        print('Waveform created')
        return super(Waveform_calc, cls).__new__(cls)

    def __init__(self, time=np.zeros(10), function=np.zeros(10), function_name='No_name', wf_info=None):
        self.function = function
        self.time = time
        self.function_name = function_name
        self.wf_info = wf_info

    def __repr__(self):
        return "Waveform(%r)" % self.function_name

    def __getitem__(self, key):
        return self.time[key], self.function[key]


class stimulus_wf:  # Generates a waveform class with pulse width duty cycle and ramp function used for cycling

    def __init__(self, pulse_width: float = 100 / (10 ** 6), duty_cycle: float = 0.5, number_of_pulses: float = 5,
                 ramp_width=200 / (10 ** 6), amplitude_sq_a1: float = 1, amplitude_sq_a2: float = 1,
                 amplitude_ramp: float = 2.3,
                 length_top=20 / (10 ** 6)):
        # Maximum frequency of the signal generator
        max_frequency_signal_generator = 80 * 10 ** 7
        # 110% of the min periode to stay in the signal generator bandwidth
        self.min_sample_time = 1 / max_frequency_signal_generator * 1.1
        self.sample_rate = 1 / self.min_sample_time  # 72 MHz default

        self.pulse_period = 200 / (10 ** (6))
        self.sample_rate_red_factor = 100
        self.amplitude_sq_a1 = amplitude_sq_a1
        self.amplitude_sq_a2 = amplitude_sq_a2
        self.amplitude_ramp = amplitude_ramp
        self.ramp_pulse_ratio_a1 = self.amplitude_sq_a1 / self.amplitude_ramp
        self.ramp_pulse_ratio_a2 = self.amplitude_sq_a2 / self.amplitude_ramp

        # ==============================================================================
        self.pulse_width = pulse_width  # Pulse width parameter
        self.duty_cycle = duty_cycle  # Duty cycle parameter
        self.number_of_pulses = number_of_pulses  # Number of pulses
        self.pulse_period = self.pulse_width / self.duty_cycle  # Pulse period
        self.ramp_width = ramp_width  # ramp width parameter
        self.number_of_sample_in_periode = int(
            self.pulse_period / self.min_sample_time / self.sample_rate_red_factor)
        self.frequency = 1 / self.pulse_period
        self.t_pulse = np.arange(start=0, stop=self.pulse_width * 2 * self.number_of_pulses,
                                 step=self.min_sample_time * self.sample_rate_red_factor)
        self.t_pulse = np.arange(start=0, stop=self.pulse_width * 2 * self.number_of_pulses,
                                 step=self.min_sample_time * self.sample_rate_red_factor)

        wf = self.ramp_pulse_ratio_a1 * 32676 * \
             (signal.square(2 * np.pi * self.frequency *
                            self.t_pulse, duty=self.duty_cycle) + 1) / 2

        wf_2 = self.ramp_pulse_ratio_a2 * 32676 * \
               (signal.square(2 * np.pi * self.frequency *
                              (self.t_pulse - length_top), duty=self.duty_cycle) + 1) / 2
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

    # Returns the value mid-pulse of the pulse waveform

    def get_mid_pulse_values(self):
        value_mid_pulse = self.waveform[int(self.number_of_sample_in_periode * self.duty_cycle / 2):int(
            self.number_of_sample_in_periode * self.number_of_pulses):int(self.number_of_sample_in_periode)]
        print('sample number: {}\n'.format(
            int(self.number_of_sample_in_periode * self.duty_cycle / 2)))
        return value_mid_pulse

    # Returns the mid-pulse indices of the pulse waveform
    def get_mid_pulse_indices(self):
        indices = np.arange(start=int(self.number_of_sample_in_periode * self.duty_cycle / 2),
                            stop=int(self.number_of_sample_in_periode * self.number_of_pulses),
                            step=int(self.number_of_sample_in_periode))
        print('index number: {}\n'.format(
            int(self.number_of_sample_in_periode * self.duty_cycle / 2)))
        return indices

    def create_file(self, name='default.csv'):

        if name is None:
            name = '{:.0f}pulses_{:.0f}V_TOP_{:.0f}V_DC_{:.0f}%_f{:.1f}kHz.arb'.format(
                self.number_of_pulses, self.amplitude_sq_a1 * 20, self.amplitude_sq_a2 * 20, self.duty_cycle * 100,
                                       self.frequency / 1000)
            a = np.around(self.wf_file_data, decimals=0)
            b = np.around(self.filter_file_data(), decimals=0)

            name_filtered = '{:.0f}pulses_{:.0f}V_DC{:.0f}%_f{:.1f}kHz_filtered.arb'.format(
                self.number_of_pulses, self.amplitude_sq_a1 * 20, self.duty_cycle * 100, self.frequency / 1000)
            a.astype('int32')
            b.astype('int32')
        else:
            a = np.around(self.wf_file_data, decimals=0)
            b = np.around(self.filter_file_data(), decimals=0)
            a.astype('int32')
            b.astype('int32')
            name_filtered = f'{name}'

        np.savetxt(name, a, fmt='%5.0f', delimiter='\t', newline='\n',
                   header="Copyright:Agilent Technologies, 2010\nFile Format:1.10"
                          "\nChannel Count:1\nSample Rate:{""}"
                          "\nHigh Level:{}\nLow Level:0\nData Type:\"short\"\nData Points:{}".format(
                       int(self.sample_rate / self.sample_rate_red_factor), self.amplitude_ramp,
                       self.data_points),
                   comments='')
        np.savetxt(name_filtered, b, fmt='%5.0f', delimiter='\t', newline='\n',
                   header="Copyright:Agilent Technologies, 2010\nFile Format:1.10"
                          "\nChannel Count:1\nSample Rate:{"
                          "}\nHigh Level:{}\nLow Level:0\nData Type:\"short\"\nData Points:{}".format(
                       int(self.sample_rate / self.sample_rate_red_factor), self.amplitude_ramp,
                       self.data_points),
                   comments='')


if __name__ == '__main__':
    pulse_width = 100
    length_top = 0.1
    duty_cycle = 0.1
    number_of_pulses = 1000
    amplitude_top = 1.8
    amplitude_bottom = 1.8
    length_ramp = 2000

    vt = stimulus_wf(pulse_width=pulse_width / (10 ** 6), duty_cycle=duty_cycle, number_of_pulses=1000,
                     ramp_width=500 / (10 ** 6), amplitude_sq_a1=amplitude_top, amplitude_sq_a2=amplitude_bottom,
                     amplitude_ramp=2, length_top=length_top / (10 ** 6))
    win = signal.windows.hann(20)
    filtered = signal.convolve(
        vt.wf_file_data, win, mode='full', method='direct') / sum(win)

    print('PRF = {:.2f} kHz\nDuty cycle = {:.2f} %\nPulse duration = {:.6f} s'.format(
        vt.frequency / 1000, vt.duty_cycle * 100, vt.pulse_width))
    print('waveform duration = {:.2f} s'.format(vt.wf_duration))
    print('lifetime test duration to 10^9 cycles = {0:d}.{1:d} h'.format(int(
        vt.expected_10power9_cycles), int(int(str(vt.expected_10power9_cycles).split('.')[1][:1]) * 60)))
    os.chdir(r'C:\Users\T0188303\Desktop\Offline\PythonDIR\Cycling\Patterns')
    vt.create_file(name='1000pulses_{}us_pulse_dc{}%_36Vtop40V_triangle.arb'.format(int(pulse_width), int(duty_cycle*100)))

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))
    # ax.plot(vt.time[:10000], vt.wf_file_data[:10000], label='cycling sequence')
    # ax.plot(vt.time[:10000], filtered[:10000], label='cycling sequence filtered')

    # ax.plot(vt.wf_2[:10000], label='A2')
    # ax.plot(vt.wf[:10000], label='A1')
    # ax.plot(vt.wf_final[:10000], label='final')
    # ax.plot(vt.time, vt.wf_file_data, label='cycling sequence')
    ax.plot(vt.time, filtered[:vt.time.size], label='cycling sequence filtered')
    ax.grid(linestyle='--', linewidth=1)
    ax.set(title='Generated waveform')
    ax.set(xlabel='time(s)')
    ax.set(ylabel='Normalized Amplitude')
    plt.legend()
    plt.show()
