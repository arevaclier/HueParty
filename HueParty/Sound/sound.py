##############################
#         Wav file           #
#       processing           #
#                            #
#   Created by A. Revaclier  #
#           Feb 2017         #
#                            #
##############################

import pylab
from scipy.io import wavfile
import sys


class Sound:
    def __init__(self, wav_file, samples_per_second):

        # Defines the maximum amplitude of a 16 bit wav file
        self.MAX_AMP = 32767
        self.wav_file = wav_file
        self.samples_per_second = samples_per_second

        # Try to get a representation of the audio file in terms of time: {frequency, amplitude}
        try:
            # File sampling, usually 44100Hz or 48000Hz
            self.frame_rate, self.snd = wavfile.read(self.wav_file)
            # The amplitudes cannot be higher than the max amplitude
            self.amp = self.snd / self.MAX_AMP
            # Take only one track of the file
            self.sound_info = self.snd[:, 0]
            # Get a spectrograph of the audio file
            self.spectrum, freqs, self.t, self.im = pylab.specgram(self.sound_info, NFFT=1024, Fs=self.frame_rate,
                                                                   noverlap=5, mode='magnitude')
            # Create two arrays, one containing all the timestamps and another containing frequencies of the file at
            # these timestamps.
            time, frequencies = self.get_values_freq()

            # Get amplitudes at certain timestamps
            amplitudes = self.get_values_amplitude(time)

            # Both time and amplitudes must contain the same number of elements.
            self.time, self.amplitudes = self.normalize_arrays(time, amplitudes)

            # This is a numpy array, transform it to a normal array
            self.frequencies = frequencies.ravel()

            # Take the frequencies and make them fit on a certain scale
            self.normalize_frequencies()
            # Take the amplitudes and make them fit on a certain scale
            self.normalize_amplitudes()

            # Create the array containing times, amplitudes and frequencies.
            self.song = self.get_info()

        except:
            print(sys.exc_info())

    # Get all frequencies at certain timestamps. Return both.
    def get_values_freq(self):

        # Get the actual samples per second of the file
        x = len(self.t)
        time = max(self.t)
        freqs_by_s = x / time

        # Get the ration between the desired number of samples per second and the file's
        division = int(round(freqs_by_s / self.samples_per_second))

        # Remove all superfluous frequencies and timestamp to reduce the array to the desired samples number.
        frequencies = self.spectrum[1][::division]
        time = self.t[::division]

        return time, frequencies

    # Get amplitudes for certain timestamps. Return amplitudes
    def get_values_amplitude(self, time):

        # Get the ration between the actual number of sampled amplitudes and the desired's.
        # This is done by dividing the number of amplitudes by the number of time samples.
        div = int(round(len(self.amp) / len(time)))
        # Remove unwanted amplitudes' samples.
        amplitudes = self.amp[::div].ravel()

        return amplitudes

    # Equalize the number of amplitudes with the number of timestamps
    def normalize_arrays(self, time, amplitudes):

        # If the length of these arrays are different
        if len(amplitudes) != len(time):
            diff = len(amplitudes) - len(time)

            # If we have more amplitudes than timestamps
            if diff > 0:
                # Remove extra amplitudes
                amplitudes = amplitudes[:-diff]
            else:
                # If we have more timestamps, remove extra timestamps.
                time = time[:diff]

        return time, amplitudes

    # Combines the values for timestamps, amplitudes and frequencies and return them
    def get_info(self):
        song = []

        for index in range(len(self.time)):
            t = self.time[index]
            f = self.frequencies[index]
            a = self.amplitudes[index]

            song.append({t: {"freq": f, "amp": a}})

        return song

    def normalize_frequencies(self):

        max_nm = 750
        min_nm = 380

        scale = max_nm - min_nm
        max_freq = max(self.frequencies)

        for index in range(len(self.frequencies)):
            calc = (self.frequencies[index] * scale / max_freq) + min_nm
            self.frequencies[index] = int(calc)

    # Normalize amplitudes on a scale from 0 to 255
    def normalize_amplitudes(self):

        # Amplitudes' values might be negative, take the absolute value.
        for index in range(len(self.amplitudes)):
            self.amplitudes[index] = abs(self.amplitudes[index])

        # Set the scale dynamically. The maximum value must be set for the highest amplitude.
        max_amplitude = max(self.amplitudes)
        max_value = 255

        # Set each amplitude according to the scale.
        for index in range(len(self.amplitudes)):
            calc = (self.amplitudes[index] * max_value) / max_amplitude
            self.amplitudes[index] = round(calc)
