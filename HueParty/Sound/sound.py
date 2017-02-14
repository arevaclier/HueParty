import pylab
from scipy.io import wavfile
import sys

class Sound:

    def __init__(self, wav_file, samples_per_second):
        self.MAX_AMP = 32767
        self.wav_file = wav_file
        self.samples_per_second = samples_per_second

        try:
            self.frame_rate, self.snd = wavfile.read(self.wav_file)
            self.amp = self.snd / self.MAX_AMP
            self.sound_info = self.snd[:, 0]
            self.spectrum, freqs, self.t, self.im = pylab.specgram(self.sound_info, NFFT=1024, Fs=self.frame_rate, noverlap=5, mode='magnitude')

            time, frequencies = self.get_values_freq()
            amplitudes = self.get_values_amplitude(time)

            self.time, self.amplitudes = self.normalize_arrays(time, amplitudes)

            self.frequencies = frequencies.ravel()
            self.normalize_frequencies()
            self.normalize_amplitudes()

            self.song = self.get_info()

        except:
            print(sys.exc_info())

    def get_values_freq(self):
        x = len(self.t)
        time = max(self.t)
        freqs_by_s = x / time

        division = int(round(freqs_by_s / self.samples_per_second))
        frequencies = self.spectrum[1][::division]
        time = self.t[::division]
        return time, frequencies

    def get_values_amplitude(self, time):

        div = int(round(len(self.amp) / len(time)))
        amplitudes = self.amp[::div].ravel()

        return amplitudes

    def normalize_arrays(self, time, amplitudes):
        if len(amplitudes) != len(time):
            diff = len(amplitudes) - len(time)
            if diff > 0:
                amplitudes = amplitudes[:-diff]
            else:
                time = time[:diff]

        return time, amplitudes

    def get_info(self):
        song = []
        for index in range(len(self.time)):
            t = self.time[index]
            f = self.frequencies[index]
            a = abs(self.amplitudes[index])

            song.append({t: {"freq": f, "amp": a}})

        return song

    def normalize_frequencies(self):
        
        #Frequencies of the visible spectrum
        max_nm = 750
        min_nm = 380

        #Adapting our scale to range on the visible spectrum
        scale = max_nm - min_nm
        max_freq = max(self.frequencies)

        #Scaling the frequencies of the audio to light
        for index in range(len(self.frequencies)):
            calc = (self.frequencies[index] * scale / max_freq) + min_nm
            self.frequencies[index] = int(calc)

    def normalize_amplitudes(self):

        for index in range(len(self.amplitudes)):
            self.amplitudes[index] = abs(self.amplitudes[index])

        max_amplitude = max(self.amplitudes)
        max_value = 255

        for index in range(len(self.amplitudes)):
            calc = (self.amplitudes[index] * max_value) / max_amplitude
            self.amplitudes[index] = round(calc)
