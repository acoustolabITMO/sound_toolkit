from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import signal
import os


def load_signal(filename, is_filtered=False, filter_params=None):
    [_, filename_extension] = os.path.splitext(filename)

    if filename_extension == '.txt':
        [signal_frequencies, signal_amplitudes] = \
            np.loadtxt(filename, unpack=True)

        if is_filtered:
            df = signal_frequencies[1] - signal_frequencies[0]
            signal_rate = 2*int(df * len(signal_frequencies))
            # TODO: add error handler here (critical frequency must be lower
            #  than the nyquist frequency)
            signal_amplitudes = \
                filter_bandpass(signal_amplitudes,
                                f_low=filter_params['f_low'],
                                f_high=filter_params['f_high'],
                                order=filter_params['order'],
                                sample_rate=signal_rate,
                                is_freq_domain=True)

    elif filename_extension == '.wav':
        [signal_recording, _, _, signal_rate] = \
            wav_load(filename)

        if is_filtered:
            signal_recording = \
                filter_bandpass(signal_recording,
                                f_low=filter_params['f_low'],
                                f_high=filter_params['f_high'],
                                order=filter_params['order'],
                                sample_rate=signal_rate)

        [signal_frequencies, signal_amplitudes] = \
            signal_spectrum(signal_recording, signal_rate)

    return signal_frequencies, signal_amplitudes


def plot_spectrum(filename_signal,
                  is_filtered=False, filter_params=None):

    [signal_frequencies, signal_amplitudes] = \
        load_signal(filename_signal,
                    is_filtered=is_filtered, filter_params=filter_params)

    plt.figure()
    plt.plot(signal_frequencies, signal_amplitudes)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    if is_filtered:
        plt.xlim([filter_params['f_low'], filter_params['f_high']])
    plt.show()


def get_tl(filename_signal, filename_reference,
           is_filtered=False, filter_params=None):
    # TODO: error handler if no path to file was given
    [signal_frequencies, signal_amplitudes] = \
        load_signal(filename_signal,
                    is_filtered=is_filtered, filter_params=filter_params)

    [reference_frequencies, reference_amplitudes] = \
        load_signal(filename_reference,
                    is_filtered=is_filtered, filter_params=filter_params)

    # TODO: add possibility to plot filter in UI

    # TODO: add error handler
    if np.array_equal(signal_frequencies, reference_frequencies):
        transmission_loss = 20 * np.log(
            np.divide(signal_amplitudes, reference_amplitudes))
    else:
        transmission_loss = []

    # TODO: change to PyQtGraph realization
    plt.figure()
    rcParams['xtick.direction'] = 'in'
    rcParams['ytick.direction'] = 'in'

    plt.subplot(311)
    plt.plot(signal_frequencies, reference_amplitudes, 'tab:blue')
    plt.ylabel('Amplitude: reference')
    plt.xlim(0)
    if is_filtered:
        plt.xlim([filter_params['f_low'], filter_params['f_high']])

    plt.subplot(312)
    plt.plot(reference_frequencies, signal_amplitudes)
    plt.ylabel('Amplitude: signal')
    plt.xlim(0)
    if is_filtered:
        plt.xlim([filter_params['f_low'], filter_params['f_high']])

    plt.subplot(313)
    plt.plot(signal_frequencies, transmission_loss, 'tab:green')
    plt.axhline(y=0, color='k', linestyle='--', linewidth=1)
    plt.ylabel('Transmission loss')
    plt.xlabel('Frequency, Hz')
    plt.legend(['20 log(signal/reference)'])
    plt.xlim(0)
    if is_filtered:
        plt.xlim([filter_params['f_low'], filter_params['f_high']])

    plt.tight_layout()
    plt.show()
    return transmission_loss, signal_frequencies


# Load the content of a wav file:
def wav_load(filename):
    # TODO: check filename
    sample_rate, recording = wavfile.read(filename)
    recording = np.array(recording, dtype=float)
    [frequencies, amplitudes] = signal_spectrum(recording, sample_rate)
    return recording, frequencies, amplitudes, sample_rate


# Fourier transform of a signal
def signal_spectrum(audio_signal, sample_rate):
    # Define the number of samples for a given array
    samples = len(audio_signal)

    # To increase the speed of FFT:
    audio_channel = np.zeros(2 ** (int(np.ceil(np.log2(samples)))))
    audio_channel[0:samples] = audio_signal

    # Make the Fourier transform of the signal:
    signal_fft = np.fft.fft(audio_channel)
    signal_frequency = np.linspace(0, sample_rate, len(signal_fft))

    # First half is the real component, second half is imaginary:
    signal_fft_real = signal_fft[0:len(signal_fft) // 2]
    amplitudes = np.abs(signal_fft_real)

    frequencies = signal_frequency[0:len(signal_fft) // 2]

    return frequencies, amplitudes


# Filtration
def filter_bandpass(input_signal, is_freq_domain=False,
                    f_low=20, f_high=20e3, order=4, sample_rate=44100):

    # Cutoff frequencies (as fractions of Nyquist frequency):
    freq_nyquist = 0.5 * sample_rate
    low_pass = f_low / freq_nyquist
    high_pass = f_high / freq_nyquist

    # Filtration function:
    sos = signal.butter(order, [low_pass, high_pass],
                        btype='band', analog=False,
                        output='sos')
    if is_freq_domain:
        w, h = signal.sosfreqz(sos, worN=len(input_signal))
        output_signal = np.multiply(input_signal, np.abs(h))
    else:
        output_signal = signal.sosfilt(sos, input_signal)

    return output_signal


# Analysis of wav files
def wav_analysis(path2recording, filename, plot_spectrum=True):
    # Load the content of a wav file:
    filepath = '{}/{}'.format(path2recording, filename)
    rate, recording = wavfile.read('{}.wav'.format(filepath))
    recording = np.array(recording, dtype=float)
    [frequencies, amplitudes] = signal_spectrum(recording, rate)

    # Plot spectrum of the signal:
    if plot_spectrum:
        plt.figure()
        plt.plot(frequencies, amplitudes)
        plt.xlabel('Frequency, Hz')
        plt.ylabel('Signal')
        plt.xlim([20, 10000])
        plt.autoscale(enable=True, axis='both', tight=True)
        plt.savefig('{}_spectrum.png'.format(filepath))

    return frequencies, amplitudes
