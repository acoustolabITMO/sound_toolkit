import time
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import chirp

# Import local modules:
import analyzer as an


# Prepare signals to generate
def waveforms(timestamps, wf_params, signal_type='sin'):
    if signal_type == 'sin':
        signal_generated = np.sin(2 * np.pi * wf_params['freq'] * timestamps)
    elif signal_type == 'chirp':
        signal_generated = \
            chirp(timestamps,
                  f0=wf_params['f_start'], f1=wf_params['f_end'],
                  t1=wf_params['duration'],
                  method='linear', phi=-90)
    else:
        signal_generated = []

    return signal_generated


# Simultaneously generate and record sound signals:
def generate_and_record(wf_params, signal_type='sin'):

    # Define the time range:
    timestamps = \
        np.arange(wf_params['sample_rate'] * wf_params['duration']) / \
        wf_params['sample_rate']

    # Prepare signal form for generation:
    signal_generated = waveforms(timestamps, wf_params, signal_type=signal_type)
    signal_recorded = np.empty([wf_params['cycles'], len(timestamps)])

    len_fft = 2 ** (int(np.ceil(np.log2(len(timestamps)))) - 1)
    signal_amplitudes = np.empty([wf_params['cycles'], len_fft])
    signal_frequencies = np.empty([wf_params['cycles'], len_fft])

    for cycle in range(0, wf_params['cycles']):
        # Record the signal until file is done playing:
        recording = sd.playrec(signal_generated,
                               samplerate=wf_params['sample_rate'],
                               channels=1)
        sd.wait()

        signal_recorded[cycle, :] = np.array(recording[:, 0], dtype=float)

        [signal_frequencies[cycle, :],
         signal_amplitudes[cycle, :]] = \
            an.signal_spectrum(signal_recorded[cycle, :],
                               wf_params['sample_rate'])

        time.sleep(wf_params['cycles_pause'])

    # TODO: check that all frequency ranges are the same
    signal_amplitudes_avg = np.mean(np.array(signal_amplitudes), axis=0)
    signal_frequencies_avg = signal_frequencies[0, :]

    return \
        signal_frequencies_avg, signal_amplitudes_avg, timestamps, \
        signal_recorded, signal_generated


# Generate a sequence of sinusoidal signals
def discrete_sin(wf_params, freq_array, path2save):

    amplitudes_sweep = [None] * len(freq_array)
    idx_freq = 0

    with open('{}/amplitudes_sweep.txt'.format(path2save), 'w') as file2save:
        file2save.write("Frequency (Hz), Amplitude\n\n")

    for freq in freq_array:
        # Generate and record the signal
        wf_params['freq'] = freq
        [signal_frequencies_avg, signal_amplitudes_avg, _, _, _] = \
            generate_and_record(wf_params, signal_type='sin')

        timing = time.time()

        # Get amplitude at the given frequency
        idx = (np.abs(signal_frequencies_avg - freq)).argmin()
        amplitudes_sweep[idx_freq] = signal_amplitudes_avg[idx]

        # Save the result
        with open('{}/amplitudes_sweep.txt'.format(path2save), 'a') as\
                file2save:
            file2save.write("{}, {}\n".format(freq, signal_amplitudes_avg[idx]))

        # TODO: make the progress visible in the UI
        print("Recorded: {} Hz.\nRemains: {} from {} samples\n".format(
            freq, len(freq_array) - idx_freq - 1, len(freq_array)))

        exec_time = time.time() - timing
        time.sleep(wf_params['sweep pause'] - exec_time)
        idx_freq += 1

    return amplitudes_sweep


# General workflow:
def gr_workflow(wf_params, path2save):

    if wf_params['type'] == 'sweep':
        gr_workflow_sweep(wf_params, path2save)
    else:
        gr_workflow_wf(wf_params, path2save)


# Workflow for sin sweep:
def gr_workflow_sweep(wf_params, path2save):
    freq_array = np.arange(wf_params['f_start'],
                           wf_params['f_end'] + 1, wf_params['f_step'])
    amplitudes_sweep = discrete_sin(wf_params, freq_array, path2save)

    plt.figure()
    plt.plot(freq_array, amplitudes_sweep)
    plt.plot(freq_array, amplitudes_sweep, 'r.')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    if wf_params['f_end'] > wf_params['f_start']:
        plt.xlim([wf_params['f_start'], wf_params['f_end']])
    plt.savefig('{}/amplitudes_sweep.png'.format(path2save))


def gr_workflow_wf(wf_params, path2save):
    [signal_frequencies_avg, signal_amplitudes_avg, _,
     signal_recorded, signal_generated] = \
        generate_and_record(wf_params, signal_type=wf_params['type'])

    # Save the generated signal as *.wav file:
    wavfile.write("{}/generated_signal.wav".format(path2save),
                  wf_params['sample_rate'], signal_generated)
    [gen_freq, gen_amp] = \
        an.signal_spectrum(signal_generated, wf_params['sample_rate'])
    data2save = np.c_[gen_freq, gen_amp]
    header = "Frequency (Hz), Amplitude"
    np.savetxt("{}/signal_generated.txt".format(path2save), data2save,
               header=header)

    # Save the recorded signals
    for cycle in range(0, wf_params['cycles']):
        wavfile.write("{}/recorded_signal_{}.wav".format(path2save, cycle),
                      wf_params['sample_rate'], signal_recorded[cycle, :])

    # Save the averaged values
    # TODO: add info about the recording
    data2save = np.c_[signal_frequencies_avg, signal_amplitudes_avg]
    header = "Frequency (Hz), Amplitude"
    np.savetxt("{}/signal_recorded_avg.txt".format(path2save), data2save,
               header=header)
