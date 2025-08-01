import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd

# Constants
rate = 44100
chunk = 1024

# Prepare plot
plt.ion()
fig, ax = plt.subplots()
frequencies = np.fft.rfftfreq(chunk, d=1 / rate)
bars = ax.bar(frequencies, np.zeros_like(frequencies), width=20)

ax.set_xlim(0, 2000)  # Show up to 2 kHz
ax.set_ylim(0, 50)
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Magnitude")
ax.set_title("Live Audio Spectrum")

# Initialize buffer
audio_buffer = np.zeros(chunk)

def audio_callback(indata, frames, time, status):
    global audio_buffer
    audio_buffer = indata[:, 0]

# Use blocking stream inside main thread
with sd.InputStream(channels=1, callback=audio_callback, samplerate=rate, blocksize=chunk):
    print("Streaming live audio... Press Ctrl+C to stop.")
    try:
        while True:
            # Compute magnitude spectrum
            windowed = audio_buffer * np.hanning(len(audio_buffer))
            spectrum = np.fft.rfft(windowed)
            magnitude = np.abs(spectrum)

            # Update bars
            for bar, h in zip(bars, magnitude):
                bar.set_height(h)

            plt.pause(0.01)
    except KeyboardInterrupt:
        print("Stopped.")